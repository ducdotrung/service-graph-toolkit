# MCP Tool Contract

Read-only tools should return concise, bounded evidence:

```json
{"summary":"short result","data":{},"sources":[],"truncated":false,"nextAction":"optional command"}
```

Sources identify a path, URL, revision, or generated artifact. Mutation tools
must be separate, require explicit authorization, and never return secrets.
