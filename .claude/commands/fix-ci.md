# Fix Failing CI

Diagnose and fix failing CI pipeline checks.

## Steps

1. Run `gh run list --limit 5` to see recent CI runs.
2. Find the failing run and use `gh run view <id> --log-failed` to get the failure logs.
3. Analyse the failure:
   - Is it a test failure? Read the test, read the source, fix the source.
   - Is it a lint error? Run the linter locally and fix.
   - Is it a build error? Run the build locally and fix.
   - Is it a type error? Run the type checker locally and fix.
   - Is it a dependency issue? Check lockfiles and install.
   - Is it a Terraform validation failure? Run `terraform validate` locally.
   - Is it a Docker build failure? Run `docker build` locally.
4. After fixing, run the same checks locally to verify.
5. Commit the fix with a message like `fix: resolve failing CI [describe what broke]`.
6. Push and confirm the new run is triggered.

## Rules

- Fix the root cause, not the symptom.
- Never disable a test to make CI pass.
- Never skip linting rules to make CI pass.
- If the fix requires a configuration change, explain why in the commit message.
