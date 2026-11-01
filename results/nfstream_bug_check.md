# NFStream 6.6.0 idle-expiry bug: before and after the patch

Same two live windows (SQLi, XSS), idle_timeout 15 s, 200 packet/s ping ticker running throughout.

| NFStream | Window | Median verdict after flow end (s) | Packet ratio live/offline | Flows live / offline |
|---|---|---|---|---|
| unpatched | SqlInjection | 82.5 | 1.0033 | 471 / 464 |
| unpatched | XSS | 49.2 | 0.645 | 118 / 224 |
| patched | SqlInjection | 15.6 | 1.0029 | 469 / 464 |
| patched | XSS | 15.5 | 0.9941 | 217 / 224 |
