# Find Technical Debt

Scan the codebase for common technical debt patterns and produce a prioritised report.

## Steps

1. Search for TODO, FIXME, HACK, and XXX comments across all apps.
2. Identify duplicated code blocks (functions or logic repeated in 3+ places).
3. Look for overly long files (>400 lines) and overly long functions (>60 lines).
4. Check for unused exports, dead imports, and orphaned files.
5. Identify outdated dependencies (check package.json and pyproject.toml).
6. Look for inconsistent patterns across the three apps.
7. Check for missing test coverage on critical paths (Neo4j repositories, API endpoints, extractors).
8. Audit Cypher queries for missing parameterisation or unbounded results.

## Output Format

Present findings grouped by category. For each item include:

- File path and line number.
- Brief description of the issue.
- Suggested fix (one sentence).
- Effort estimate: S (< 30 min), M (1-4 hours), L (> 4 hours).

Sort each category by effort estimate ascending. Quick wins first.
