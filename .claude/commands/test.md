# Run Tests and Report

Run the project's test suites across all apps and provide a clear report.

## Steps

1. Determine which app(s) to test. If the user specifies one (web, api, nlp), test only that. Otherwise test all.
2. Run the appropriate test commands:
   - Frontend: `pnpm --filter web test`
   - API: `cd apps/api && pytest -v`
   - NLP: `cd apps/nlp && pytest -v`
   - All: `turbo run test`
3. If tests fail, analyse the failures:
   - Identify which tests failed and why.
   - Check if the failure is in new code or existing code.
   - Suggest a fix for each failure.
4. If all tests pass, confirm with a summary: total tests per app, passing, time elapsed.

## Rules

- Always run tests from the project root unless a specific app is targeted.
- If a test requires environment variables, check `.env.example` and flag any that are missing.
- Never modify test files to make tests pass. Fix the source code.
- For API integration tests, ensure the testcontainers Neo4j instance starts correctly before flagging test failures.
- If there is no test suite configured for an app, say so clearly.
