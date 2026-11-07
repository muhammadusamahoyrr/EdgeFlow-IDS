"""Blocking rule of the live gateway: a host pair is blocked once it has k attack verdicts."""
import types

import pytest

import gateway
from gateway import ID_FIELDS, Classifier

FEATS = ["f1", "f2"]


class FixedModel:
    """Returns the queued predictions, one per flow, in order."""

    def __init__(self, preds):
        self.preds = list(preds)

    def predict(self, X):
        out, self.preds = self.preds[:len(X)], self.preds[len(X):]
        return out


class Rows(list):
    def writerow(self, row):
        self.append(row)


def flow(src, dst):
    f = types.SimpleNamespace(**{name: 0 for name in ID_FIELDS + FEATS})
    f.src_ip, f.dst_ip = src, dst
    return f


@pytest.fixture
def blocks(monkeypatch):
    calls = []
    monkeypatch.setattr(gateway, "block_pair", lambda bridge, a, b: calls.append((bridge, a, b)))
    return calls


def run(flows, preds, policy, enforce=True):
    rows = Rows()
    clf = Classifier(FixedModel(preds), FEATS, rows, enforce, "s1", batch_size=len(flows),
                     max_wait_ms=50, policy=policy)
    for f in flows:
        clf.add(f)
    clf.flush()
    return clf, rows


def test_first_verdict_blocks_when_k_is_1(blocks):
    _, rows = run([flow("10.1.1.1", "10.1.1.2")], ["DDoS-SYN"], {})
    assert blocks == [("s1", "10.1.1.1", "10.1.1.2")]
    assert rows[0][-1] == 1  # blocked_now


def test_k_verdicts_needed_and_pair_is_unordered(blocks):
    flows = [flow("a", "b"), flow("b", "a"), flow("a", "b")]
    _, rows = run(flows, ["Recon", "Recon", "Recon"], {"min_attack_verdicts": 2})
    assert len(blocks) == 1  # second verdict (reverse direction) blocks; third is already blocked
    assert [r[-1] for r in rows] == [0, 1, 0]


def test_benign_verdicts_never_count(blocks):
    run([flow("a", "b")] * 3, ["Benign"] * 3, {"min_attack_verdicts": 1})
    assert blocks == []


def test_mitm_verdicts_ignored_when_policy_says_so(blocks):
    policy = {"min_attack_verdicts": 1, "ignore_mitm_flow_verdicts": True}
    run([flow("a", "b"), flow("c", "d")], ["MITM-ARP", "Web"], policy)
    assert blocks == [("s1", "c", "d")]


def test_no_blocking_without_enforce(blocks):
    _, rows = run([flow("a", "b")], ["DDoS-SYN"], {}, enforce=False)
    assert blocks == [] and rows[0][-1] == 0


def test_reset_forgets_votes_and_blocks(blocks):
    clf, _ = run([flow("a", "b")], ["Mirai"], {"min_attack_verdicts": 2})
    clf.reset()
    clf.model = FixedModel(["Mirai"])
    clf.add(flow("a", "b"))
    clf.flush()
    assert blocks == []  # the vote before the reset does not carry over


def test_every_flow_written_once(blocks):
    flows = [flow("a", "b"), flow("c", "d")]
    clf, rows = run(flows, ["Benign", "Web"], {})
    clf.flush()  # an empty flush writes nothing
    assert len(rows) == 2 and clf.n_classified == 2
    assert [r[len(ID_FIELDS)] for r in rows] == ["Benign", "Web"]
