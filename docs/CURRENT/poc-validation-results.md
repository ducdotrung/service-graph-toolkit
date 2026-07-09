# PoC Validation Results

Date: 2026-07-08
GitNexus version: 1.6.8
Indexed services: 6

## Index summary

| Service | Files | Symbols | Edges | Clusters | Wall-clock |
|---------|-------|---------|-------|----------|------------|
| gateway-service | 35 | 192 | 367 | 12 | 5.2s |
| identity-service | 114 | 681 | 1,278 | 28 | 4.2s |
| bio-service | 1,466 | 14,492 | 33,896 | 809 | 40.0s |
| user-service | 1,714 | 11,913 | 25,592 | 712 | 29.3s |
| platform-mcp | 37 | 317 | 531 | 7 | 3.6s |
| assistant-service | 1,290 | 24,200 | 46,243 | 934 | 52.5s |

All pilot services stayed within a usable indexing time range.

## Q1 — Service map

**PASS.** `gitnexus list` showed distinct indexes with non-zero symbol counts.

## Q2 — Client-to-controller bridging inside one index

**PARTIAL.** A declarative HTTP client interface was not automatically bridged
to the controller that served the same contract.

Conclusion:
- GitNexus is strong inside explicit code relationships
- service-contract matching still needs overlay help

## Q3 — Cross-index HTTP client lookup

**PASS (canonical case).** A client symbol defined in one service was not
automatically resolved inside another service's index.

Conclusion:
- cross-service HTTP edges should still exist in the manifest
- `gitnexus group` may reduce this gap, but should be validated first

## Q4 — Gateway route lookup

**PASS.** Route ownership is best answered by manifest or gateway config, not by
pure code graph traversal.

## Q5 — Event producer/consumer tracing

**PARTIAL.** The consumer side was easy to find. The producer side was less
reliable without extra indexing scope or explicit manifest edges.

## Summary

| Query | Result | Status |
|-------|--------|--------|
| Service map | Distinct, usable indexes | PASS |
| Client-to-controller bridging | Not automatic | PARTIAL |
| Cross-index HTTP lookup | Not automatic | PASS |
| Gateway route lookup | Best answered from config | PASS |
| Event origin tracing | Consumer easy, producer less certain | PARTIAL |

## Main takeaway

The pilot supports the basic architecture:

- GitNexus for in-service code questions
- manifest or overlay for cross-service edges
- optional group bridge once the pilot proves it improves query quality
