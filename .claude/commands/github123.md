---
description: Publish this project to GitHub - push, README, About, Pages, CI/CD, and a secret scan
argument-hint: <github repo URL or owner/repo>
---

Publish the current project to GitHub. The repo info is: `$ARGUMENTS`

If `$ARGUMENTS` is empty, ask the user for the GitHub repo (`owner/repo` or URL) and, if relevant, the branch. Do not guess.

Normalize the repo to `OWNER/REPO`. Use the `gh` CLI if it is available and authenticated; otherwise use the GitHub MCP tools (`mcp__github__*`). Never print or store tokens.

Work through the steps in order. **Step 1 (security scan) runs first and gates everything else.** Report a short status line per step as you go.

## Step 1 - Security scan (before anything is published)

Scan the working tree AND git history for sensitive information:

- Secrets: API keys, tokens, passwords, private keys (`-----BEGIN ... PRIVATE KEY-----`), AWS/GCP/Azure keys, `Authorization`/`Bearer` values, connection strings, webhook URLs, JWTs.
- Risky files: `.env*`, `*.pem`, `*.key`, `*.p12`, `id_rsa*`, `credentials*.json`, `*.sqlite`/`*.db`, `.npmrc`/`.pypirc` with tokens, `node_modules`, build artifacts, OS/editor junk.
- Personal data: personal emails, phone numbers, home addresses, internal hostnames/IPs, and absolute local paths that reveal usernames.
- Use `gitleaks` or `trufflehog` if installed, otherwise `grep -rEIn` with patterns for the above, plus `git log -p` / `git grep` over history. Also run the GitHub `run_secret_scanning` tool if available.

Handling findings:
- Remove the secret from the code (use env vars / placeholders), add the file to `.gitignore`, and add `.env.example` if useful.
- If a secret is in git history, STOP and tell the user: it must be rotated/revoked, and history rewriting (which is destructive) needs their explicit approval.
- Do not continue to Step 2 until the scan is clean or the user explicitly accepts the remaining findings. Show the user a summary of what was found (redact the secret values).

## Step 2 - Push the code

1. Make sure the repo has a sensible `.gitignore`.
2. Ensure `origin` points to the user's repo (`git remote add` / `set-url`). Show the user the remote before pushing.
3. Commit any pending changes with a clear message.
4. Push the current branch with `git push -u origin <branch>` (retry on network errors with backoff: 2s, 4s, 8s, 16s). Never force-push without explicit user approval.
5. If the repo does not exist, ask the user before creating it, and confirm public vs private.

## Step 3 - README

Create or update `README.md` (preserve useful existing content; edit rather than overwrite). Include: project title and one-line description, features, a live-demo link placeholder to fill in after Step 5 (GitHub Pages URL), how to run/use it locally, tech stack, project structure, and license. Base it on what the code actually does - read it first. Commit and push.

## Step 4 - About section

Set the repo's About: a concise description (under ~350 characters), 3-8 relevant topics, and the homepage URL (filled in Step 7).
- `gh repo edit OWNER/REPO --description "..." --add-topic a,b,c`
- If `gh` is unavailable, give the user the exact text and tell them to paste it under the repo's gear icon next to *About*.

## Step 5 - GitHub Pages

Detect the site type: a static site (`index.html` at root or in `docs/`), or a framework with a build step (Vite, React, Next export, Jekyll, etc.).
- Static: enable Pages from the default branch root (or `/docs`):
  `gh api -X POST repos/OWNER/REPO/pages -f "source[branch]=<branch>" -f "source[path]=/"`
  (use `-X PUT` if Pages already exists).
- Built site: deploy via a GitHub Actions workflow (`actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`) and set the Pages build type to `workflow`:
  `gh api -X POST repos/OWNER/REPO/pages -f build_type=workflow`
- Ensure `index.html` exists. If Pages can't be enabled via API/permissions, tell the user the exact manual path: *Settings -> Pages -> Build and deployment*.
- The URL will be `https://OWNER.github.io/REPO/` (or the custom domain from the Pages API response).

## Step 6 - CI/CD with GitHub Actions

Create `.github/workflows/` files appropriate to the project (read it to decide):
- `ci.yml`: on `push` and `pull_request`, checkout, set up the language/runtime, install dependencies, lint, test, build. For a plain static site, validate HTML (e.g., `html-validate`/`htmlproofer`) and check links.
- `deploy.yml` (or combined): on push to the default branch, deploy to GitHub Pages with `permissions: { contents: read, pages: write, id-token: write }` and a `concurrency` group.
- Use least-privilege `permissions`, pin actions to major versions (or SHAs), and never hardcode secrets - reference `${{ secrets.NAME }}` and tell the user which secrets to add.
- Commit, push, then check the workflow run status (`gh run list` / `gh run watch`, or `actions_list`) and fix failures until green. Report the result honestly if it is still failing.

## Step 7 - Link Pages from the repo

Once the Pages URL is live (check it responds with HTTP 200; it may take a minute or two):
- Set the repo Website/homepage: `gh repo edit OWNER/REPO --homepage "https://OWNER.github.io/REPO/"`
- Put the live URL in the README (replace the placeholder from Step 3) and push.

## Step 8 - Final verification and report

Re-run a quick secret scan on the final state (including the new workflow files and README), then give the user a summary:
- Repo URL, branch, latest commit
- Pages URL and whether it is live
- CI/CD workflow status
- Security scan results (what was found/fixed/accepted) and any remaining manual actions (rotate keys, add Actions secrets, enable Pages in settings)

## Rules

- Confirm with the user before any destructive or hard-to-reverse action (force push, history rewrite, creating/changing repo visibility, deleting files).
- Do not open a pull request unless asked.
- Never commit anything flagged in Step 1.
