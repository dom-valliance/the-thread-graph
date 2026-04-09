# Recall Relevant Learnings

Search Claude's memory (notes and CLAUDE.md) for past learnings relevant to the current task.

## Steps

1. Identify the topic. Consider: which app (web, api, nlp, infra), which entity types, which technology.

2. Read `.claude/CLAUDE.md`, focusing on Gotchas.

3. Check `.claude/notes/` for relevant files:
   - `global.md`: Broadly applicable learnings.
   - `neo4j.md`: Cypher, driver, index, constraint issues.
   - `notion-sync.md`: API, rate limiting, field mapping.
   - `d3.md`: Force simulation, React integration.
   - `infra.md`: Terraform, AKS, Docker.
   - `nlp.md`: Prompt engineering, extraction accuracy.

4. Compile relevant learnings grouped by source.

5. If no relevant learnings found, say so.

## Output Format

```
## Relevant Learnings for [current task description]

### From CLAUDE.md
- [relevant gotcha or rule]

### From notes/global.md
- [YYYY-MM-DD] [relevant learning summary]

### From notes/<topic>.md
- [YYYY-MM-DD] [relevant learning summary]

### No matches
[State if a section had nothing relevant]
```

## Rules

- Read the files. Do not rely on memory from a previous session.
- Be selective. Only surface genuinely relevant entries.
