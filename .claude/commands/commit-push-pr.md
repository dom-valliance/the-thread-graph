# Commit, Push, and Open PR

Run the full git workflow from staged changes to an open pull request.

## Steps

1. Run `git status` to see what has changed.
2. Run `git diff --cached` and `git diff` to understand the changes.
3. Stage all relevant files (be specific, do not use `git add -A`).
4. Write a commit message in conventional commit format. Subject line max 72 chars, imperative mood. Body explains why, not what.
5. Commit the changes.
6. Push the branch to origin with `-u` flag.
7. Open a PR using `gh pr create` with:
   - A concise title following conventional commits format.
   - A body containing: a Summary section (2-3 bullet points), a Test Plan section (checklist), and a note that it was generated with Claude Code.
8. Output the PR URL.

## Rules

- Never force push.
- Never push directly to `main` or `master`.
- If the branch does not exist on the remote yet, create it.
- If pre-commit hooks fail, fix the issue and create a new commit. Never amend.
- Do not commit `.env`, credentials, secrets files, or `terraform.tfstate`.
