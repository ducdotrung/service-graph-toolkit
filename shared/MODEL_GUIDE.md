# Model Selection Guide

Choose the smallest capable model after deterministic tools have reduced the
problem. Client adapters may map these classes to their available models.

| Task | Model class | Reasoning level |
|---|---|---|
| File discovery, classification, short extraction | fast/low-cost | low |
| Focused code change, test repair, routine review | coding-capable | medium |
| Cross-service implementation plan, QA scope | strong general/coding | high |
| Architecture, security review, incident root cause | strongest available | high or maximum |

Never use a model to reproduce command output, list files, convert documents,
or run validation that a local script can perform. Raise reasoning before
switching providers when the current model has sufficient context and tools.
