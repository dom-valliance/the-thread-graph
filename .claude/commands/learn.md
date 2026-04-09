# Learn from a Correction

Capture a mistake or correction so Claude never repeats it. Primary mechanism for building long-term memory for this codebase.

## Arguments

The user will describe what went wrong and what the correct approach is. If they do not provide enough detail, ask before proceeding.

## Steps

1. Understand the correction. Identify:
   - What Claude did wrong.
   - What the correct behaviour should have been.
   - Whether this is specific to a file, module, or project, or whether it applies globally.

2. Ensure the notes directory exists at `.claude/notes/`.

3. Determine the target notes file:
   - Global: `.claude/notes/global.md`
   - Neo4j/Cypher: `.claude/notes/neo4j.md`
   - Notion sync: `.claude/notes/notion-sync.md`
   - D3 visualisation: `.claude/notes/d3.md`
   - Infrastructure: `.claude/notes/infra.md`
   - NLP pipeline: `.claude/notes/nlp.md`
   - Create the file if it does not exist.

4. Append a new entry:

```markdown
### [YYYY-MM-DD] Short description

**Context**: What Claude was doing when the issue occurred.
**Correction**: What the developer corrected.
**Rule**: The generalised rule to prevent recurrence.
**Applies to**: global | specific file/module/pattern
```

5. Check whether this correction should be promoted to `.claude/CLAUDE.md` Gotchas section.

6. Confirm what was captured and where.

## Rules

- Never delete existing entries in notes files.
- Keep entries concise. No filler.
- Use today's date for the entry.
- If the correction contradicts an existing rule in CLAUDE.md, flag the conflict.
