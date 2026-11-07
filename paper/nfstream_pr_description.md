## Description

Fixes #262. Possibly also the cause of #120.

`NFCache` is an LRU `OrderedDict`, but it moves a key to the most-recently-used end only in
`__setitem__`. In `consume()`, a normal update (`cache[flow_key].update(...)` returning `None`)
leaves the entry where it is, so the cache stays in creation order. `meter_scan()` stops at the
first non-idle LRU entry. A long-lived active flow at the head therefore blocks idle expiry of
every flow behind it until that flow hits `active_timeout`.

This PR calls `cache.move_to_end(flow_key)` in the update branch (O(1) on an `OrderedDict`).
Flow boundaries and features are unchanged, because `NFlow.update()` already splits flows on
idle and active timeouts. Only export timing changes.

Measured effect in live capture (`idle_timeout=15`, `active_timeout=120`): the median export
delay after a flow's last packet dropped from 82.5 s to 15.6 s. Details are in #262.

## Type of change

- [x] Bug fix (non-breaking change which fixes an issue)

## How Has This Been Tested?

- [x] Added `test_idle_expiration_order` to `tests.py`. It builds a synthetic two-flow pcap at
  runtime (stdlib only; no new file in `tests/pcaps`, so the per-pcap result tests are
  unaffected):
  - Flow A sends one packet per second for 200 s.
  - Flow B sends two packets at t = 10 s and t = 11 s.
  - With `idle_timeout=15` and `active_timeout=120`, B must be exported before A's first segment.
  - Export order is `A, B, A` without the fix (test fails) and `B, A, A` with it (test passes).
- [x] Ran these existing tests before and after the change against an NFStream 6.6.0 build with
  only `meter.py` patched. All pass with and without the fix:
  - `test_idle_timeout_parameter`, `test_active_timeout_parameter`
  - `test_n_meters_parameter`, `test_max_nflows_parameter`
  - `test_expiration_management`, `test_statistical`, `test_splt`
  - `test_export`, `test_max_nflows`
- `test_multi_files` and `test_optional_string_fields` fail in my environment **both with and
  without** the change. I believe this comes from my local build/version, not from this PR. CI
  should confirm.

**Test Configuration**:
* OS version: Ubuntu 24.04 (WSL2, kernel 6.6)
* Python version: 3.12
* Hardware: Intel i5-8350U laptop

## Checklist:

- [x] My code follows the style guidelines of this project
- [x] I have performed a self-review of my own code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] My changes generate no new warnings
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes (except the two listed above, which also fail without them)
