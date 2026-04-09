# Code Review

Review the current branch's changes against main and provide structured feedback.

## Steps

1. Run `git diff main...HEAD` to see all changes on this branch.
2. Run `git log main..HEAD --oneline` to understand the commit history.
3. For each changed file, use a subagent to perform a focused review.
4. Collect all findings and present a structured report.

## Review Checklist

For each changed file, assess:

- **Correctness**: Does the logic do what the commit messages claim? Edge cases?
- **Security**: Hardcoded secrets, injection vectors (Cypher injection in particular), unvalidated input?
- **Performance**: Unbounded Cypher queries, missing pagination, N+1 API calls, D3 memory leaks?
- **Testing**: Tests for new behaviour? Existing tests still valid?
- **Style**: Follows conventions in CLAUDE.md?
- **Neo4j**: Parameterised queries? MERGE idempotence? Proper index usage?
- **Error handling**: Errors caught and handled with actionable messages?

## Output Format

Group findings by severity:

- **Blocking**: Must fix before merge.
- **Should fix**: Strong recommendation, not a blocker.
- **Nit**: Style or preference.

End with a one-line summary: "Approve", "Approve with comments", or "Request changes".
