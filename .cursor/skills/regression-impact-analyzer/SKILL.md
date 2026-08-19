---
name: regression-impact-analyzer
description: Automate IAM test analysis workflow in phases - deploy branches, run automation tests, download Allure reports, compare test results between main and a feature branch, and analyze failures using PR diff. Designed as a multi-session skill with state persistence between invocations. Use when the user asks to run test analysis, compare test results, analyze automation failures, deploy and test a branch, analyze regression impact, or says "regression-impact-analyzer" or "proceed" (to continue a running analysis).
compatibility: Requires 'gh' cli to be installed on host machine
metadata:
  author: Jayanth Balakrishnan
  version: "1.4"
---

# Regression Impact Analyzer

Phased workflow: deploy main -> run tests -> deploy branch -> run tests -> compare -> analyze.
Each phase ends when a pipeline is triggered. User re-invokes the skill to continue.

## State Management

**Analysis directory (outside the repo — no git noise, cross-platform):**

| OS | Default path |
|----|----------------|
| Windows | `%LOCALAPPDATA%\iam-test-analysis\` |
| macOS / Linux | `~/.local/share/iam-test-analysis/` (or `$XDG_DATA_HOME/iam-test-analysis/`) |

**Override (any OS):** set `IAM_TEST_ANALYSIS_DIR` to a custom folder.

**Backups:** `<ANALYSIS_DIR>/backups/<yyyy-MM-dd_HHmmss>_<env>_<branch>/`

Referred to as `<ANALYSIS_DIR>` throughout this skill.

**At the start of every invocation**, resolve `<ANALYSIS_DIR>` once:

```bash
python <skill_path>/scripts/paths.py
```

```bash
# bash / zsh
export ANALYSIS_DIR="$(python <skill_path>/scripts/paths.py)"
```

```powershell
# PowerShell
$ANALYSIS_DIR = python <skill_path>/scripts/paths.py
```

At each invocation, read `<ANALYSIS_DIR>/state.json`.
- If it does not exist: start at Phase 1.
- If it exists: resume from the phase indicated in `current_phase`.

State file schema:
```json
{
  "current_phase": 2,
  "environment": "dev3",
  "branch": "feature/IAM-1234",
  "pr_number": 567,
  "aws_region": "us-west-2",
  "data_region": "us",
  "marker": "regression",
  "deploy_graphql": false,
  "pr_head_sha": "abc123...",
  "main_sha": "def456...",
  "branch_sha": "abc123...",
  "reuse_main_artifacts": false,
  "reuse_branch_artifacts": false,
  "reuse_pr_diff": false,
  "main_deploy_run_id": null,
  "main_test_run_id": null,
  "branch_deploy_run_id": null,
  "branch_test_run_id": null,
  "orchestrator_run_id": null
}
```

Update `<ANALYSIS_DIR>/state.json` after each action (save run IDs, SHAs, reuse flags, advance `current_phase`).

---

## Cache Optimization (same unchanged PR)

Avoid re-deploying, re-testing, and re-fetching when the PR and `main` have not changed.

**Cache location:** `<ANALYSIS_DIR>/cache/` (persists across runs; not moved by archive)

**Cache keys (by commit SHA and test configuration):**
| Type | Key | Skips |
|------|-----|-------|
| PR diff | `pr_number` + PR head SHA | `gh pr diff` in Phase 5 |
| Main artifacts | `environment` + `data_region` + `marker` + `main` SHA | Phases 1–2 (deploy + test main) |
| Branch artifacts | `environment` + `data_region` + `marker` + branch + PR head SHA | Phases 3–4 (deploy + test branch) |

Artifact cache entries are **not** reused when `marker` or `data_region` differs — those change which tests run and which region they target.

**At start of Phase 1** (after gathering inputs), always run:
```bash
python <skill_path>/scripts/cache_manager.py check \
  --repo Trimble-Cloud-Core-Platform/iam \
  --pr <pr_number> \
  --env <environment> \
  --branch <branch> \
  --marker <marker> \
  --data-region <data_region>
```

Then restore anything reusable:
```bash
python <skill_path>/scripts/cache_manager.py restore \
  --repo Trimble-Cloud-Core-Platform/iam \
  --pr <pr_number> \
  --env <environment> \
  --branch <branch> \
  --marker <marker> \
  --data-region <data_region>
```

**Routing based on `skip_to_phase` from check output:**

| `skip_to_phase` | Action |
|-----------------|--------|
| `5` | Main + branch artifacts cached → set `current_phase: 5`, skip pipelines, go straight to compare + analyze |
| `3` | Main artifacts cached → set `current_phase: 3`, skip Phases 1–2, only deploy + test branch |
| `null` | Full workflow from Phase 1 (even if partial cache exists in the index) |

**Always use `apply_reuse` from the check output** — not the raw `reuse` block — when saving state:

| `apply_reuse` field | Set `reuse_*` in state when |
|---------------------|----------------------------|
| `main_artifacts` | `skip_to_phase` is `3` or `5` |
| `branch_artifacts` | `skip_to_phase` is `5` only |
| `pr_diff` | `skip_to_phase` is `5` only |

Example mapping after check:
- `reuse_main_artifacts` ← `apply_reuse.main_artifacts`
- `reuse_branch_artifacts` ← `apply_reuse.branch_artifacts`
- `reuse_pr_diff` ← `apply_reuse.pr_diff`

This prevents stale branch artifacts from being reused when only main was cached but the branch is being re-tested (`skip_to_phase: 3` or `null`).

When `reuse_*_artifacts` is `true`, **do not call `gh run view` or `gh run download`** for that side — artifacts are already restored locally. Run IDs may be unset on cache hits; that is expected.

Save `pr_head_sha`, `main_sha`, `branch_sha`, and the **`apply_reuse`** flags (as `reuse_*` in state) from the check output into `state.json`.

Tell the user what was reused, e.g. *"PR unchanged — reusing cached main results and PR diff; only branch deploy+test needed."*

**After downloading artifacts, store to cache** (pass `--repo`; missing SHAs are fetched automatically):
```bash
python <skill_path>/scripts/cache_manager.py store --type main --repo Trimble-Cloud-Core-Platform/iam
python <skill_path>/scripts/cache_manager.py store --type branch --repo Trimble-Cloud-Core-Platform/iam
python <skill_path>/scripts/cache_manager.py store --type pr --repo Trimble-Cloud-Core-Platform/iam
```

For PR metadata (used by cache), save before `store --type pr`:
```bash
gh pr view <pr_number> --repo Trimble-Cloud-Core-Platform/iam --json title,body,files,headRefOid > "$ANALYSIS_DIR/pr-metadata.json"
```

**Phase 5 PR diff:** Skip `gh pr diff` if `reuse_pr_diff` is `true` in state (use restored `pr-diff.patch`).

**Phase 3 main download:** Skip download if `reuse_main_artifacts` is `true`.

**Phase 5 branch download:** Skip download if `reuse_branch_artifacts` is `true`.

If the user explicitly asks to **force refresh** (e.g. "ignore cache", "re-run everything"):
- Skip cache check/restore
- Set all `reuse_*` flags to `false` in state
- Before the first `store` call, ensure SHAs are present (either run `cache_manager.py resolve-shas` or rely on `store --repo` which fetches them automatically)

---

## Workflow Run Discovery

After every `gh workflow run`, discover the run ID by **polling** — never use `sleep 5` + `gh run list --limit=1` (race-prone on a busy repo).

Use bash (Git Bash on Windows is fine). Set `DISPATCH_EPOCH` immediately **before** `gh workflow run`:

```bash
REPO=Trimble-Cloud-Core-Platform/iam
DISPATCH_EPOCH=$(date -u +%s)
DISPATCH_EPOCH=$((DISPATCH_EPOCH - 5))

gh workflow run <workflow_file> --repo "$REPO" --ref <branch> ...

RUN_ID=""
for attempt in $(seq 1 30); do
  RUN_ID=$(gh run list --repo "$REPO" \
    --workflow=<workflow_file> \
    --branch=<branch> \
    --event=workflow_dispatch \
    --limit=20 \
    --json databaseId,createdAt \
    -q "[.[] | select((.createdAt | fromdateiso8601) >= $DISPATCH_EPOCH)][0].databaseId")
  if [ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ]; then
    break
  fi
  sleep 10
done

if [ -z "$RUN_ID" ] || [ "$RUN_ID" = "null" ]; then
  echo "ERROR: Could not find workflow_dispatch run for <workflow_file> on <branch>" >&2
  exit 1
fi
```

Save `RUN_ID` to the appropriate field in `state.json` (`main_deploy_run_id`, `main_test_run_id`, etc.).

---

## Phase 1: Gather Inputs + Deploy Main

**Entry condition:** `state.json` does not exist.

1. Ask user for:
   - Target environment (e.g. `dev3`, `qa`, `dev`)
   - Feature branch name
   - PR link or number
   - Test marker (default: `regression`)
   - AWS region (default: `us-west-2`)
   - Data region (default: `us`)
   - Deploy GraphQL? (default: `false` — only set to `true` if user explicitly mentions GraphQL)

2. **Cache check** (unless user requested force refresh) — see [Cache Optimization](#cache-optimization-same-unchanged-pr). If `skip_to_phase` is `5` or `3`, follow routing table and skip steps below as indicated.

   **Or use the orchestrator workflow** (`deploy-and-test.yml`) instead of Phases 1–4 manually:
```bash
gh workflow run deploy-and-test.yml \
  --repo Trimble-Cloud-Core-Platform/iam \
  --ref main \
  -f STACK=<environment> \
  -f feature_branch=<branch> \
  -f marker=<marker> \
  -f DeployGraphql=<deploy_graphql>
```
   Save `orchestrator_run_id` in state using [Workflow Run Discovery](#workflow-run-discovery) with `workflow_file=deploy-and-test.yml` and `branch=main`. Set `current_phase: 2`, tell user to return in ~90 min. Phase 2 checks orchestrator status, downloads all 4 artifacts from that single run.

3. Trigger deployment from main (skip if `reuse_main_artifacts` is `true`):
```bash
gh workflow run release_sam_apply.yml \
  --repo Trimble-Cloud-Core-Platform/iam \
  --ref main \
  -f STACK=<environment> \
  -f AWS_REGION=<aws_region> \
  -f DATA_REGION=<data_region> \
  -f SERVICE_NAME=all \
  -f DeployCommonLayer=true \
  -f DeployGraphql=<deploy_graphql> \
  -f DeployIamAuthorizationLambda=false \
  -f SonarScan=false \
  -f TRIGGER_PERF_TEST=false
```

Where `<deploy_graphql>` is `false` by default, or `true` only if the user explicitly requested GraphQL deployment.

4. Discover the run ID using [Workflow Run Discovery](#workflow-run-discovery) with `workflow_file=release_sam_apply.yml` and `branch=main`.

5. Save state to `<ANALYSIS_DIR>/state.json` with `current_phase: 2` and `main_deploy_run_id` (or `current_phase: 3` if main was reused from cache).

6. Tell user: **"Main deployment triggered (Run ID: XXXX). This takes ~25 minutes. Come back and say 'proceed' when ready."** — or if main was cached, skip to branch phase message.

---

## Phase 2: Verify Main Deploy + Run Tests on Main

**Entry condition:** `current_phase == 2`

1. Check deployment status:
```bash
gh run view <main_deploy_run_id> --repo Trimble-Cloud-Core-Platform/iam --json status,conclusion
```

2. **If `status == "in_progress"`:** Tell user the pipeline is still running and to check back later. Do NOT advance phase.

3. **If `conclusion == "failure"`:** Alert user, show error, ask whether to retry or abort.

4. **If `conclusion == "success"`:** Trigger automation tests from main:
```bash
gh workflow run automation-testing.yaml \
  --repo Trimble-Cloud-Core-Platform/iam \
  --ref main \
  -f environment=<environment> \
  -f georegion=<data_region> \
  -f bluegreen=Actual \
  -f marker=<marker> \
  -f parallel=loadfile \
  -f iam_2452_enabled=false \
  -f publish_to_domo=false \
  -f cleanup_roles=true \
  -f cleanup_user_groups=true \
  -f cleanup_user_accounts=true \
  -f generate_url=false \
  -f send_notification=false
```

5. Discover the test run ID using [Workflow Run Discovery](#workflow-run-discovery) with `workflow_file=automation-testing.yaml` and `branch=main`. Save as `main_test_run_id`, set `current_phase: 3` in `<ANALYSIS_DIR>/state.json`.

6. Tell user: **"Automation tests triggered on main (Run ID: XXXX). Takes ~20 minutes. Say 'proceed' when ready."**

---

## Phase 3: Download Main Results + Deploy Branch

**Entry condition:** `current_phase == 3`

**If `reuse_main_artifacts` is `true`:** Skip steps 1–4 (no `gh run view` or download — artifacts already restored). Go to step 5.

1. Check test run status (skip if `reuse_main_artifacts` is `true`):
```bash
gh run view <main_test_run_id> --repo Trimble-Cloud-Core-Platform/iam --json status,conclusion
```

2. **If still running:** Tell user and wait. Do NOT advance.

3. **If failed:** The test workflow itself may "fail" because tests had failures - this is expected. Check if artifacts were produced. If so, proceed.

4. Download artifacts (skip if `reuse_main_artifacts` is `true`):
```bash
gh run download <main_test_run_id> --repo Trimble-Cloud-Core-Platform/iam --name allure-results --dir "$ANALYSIS_DIR/main-results"
gh run download <main_test_run_id> --repo Trimble-Cloud-Core-Platform/iam --name Allure-Single-Report --dir "$ANALYSIS_DIR/main-report"
```

Store main artifacts in cache after download:
```bash
python <skill_path>/scripts/cache_manager.py store --type main
```

5. Trigger branch deployment:
```bash
gh workflow run release_sam_apply.yml \
  --repo Trimble-Cloud-Core-Platform/iam \
  --ref <branch> \
  -f STACK=<environment> \
  -f AWS_REGION=<aws_region> \
  -f DATA_REGION=<data_region> \
  -f SERVICE_NAME=all \
  -f DeployCommonLayer=true \
  -f DeployGraphql=<deploy_graphql> \
  -f DeployIamAuthorizationLambda=false \
  -f SonarScan=false \
  -f TRIGGER_PERF_TEST=false
```

Use the same `<deploy_graphql>` value saved in state (consistent between main and branch deployments).

6. Discover the run ID using [Workflow Run Discovery](#workflow-run-discovery) with `workflow_file=release_sam_apply.yml` and `branch=<branch>`. Save as `branch_deploy_run_id`, set `current_phase: 4` in `<ANALYSIS_DIR>/state.json`.

7. Tell user: **"Main results downloaded. Branch deployment triggered (Run ID: XXXX). ~25 min. Say 'proceed' when ready."**

---

## Phase 4: Verify Branch Deploy + Run Tests on Branch

**Entry condition:** `current_phase == 4`

1. Check branch deployment status:
```bash
gh run view <branch_deploy_run_id> --repo Trimble-Cloud-Core-Platform/iam --json status,conclusion
```

2. **If still running:** Tell user to wait. Do NOT advance.

3. **If failed:** Alert user, offer retry or abort.

4. **If success:** Trigger tests from branch:
```bash
gh workflow run automation-testing.yaml \
  --repo Trimble-Cloud-Core-Platform/iam \
  --ref <branch> \
  -f environment=<environment> \
  -f georegion=<data_region> \
  -f bluegreen=Actual \
  -f marker=<marker> \
  -f parallel=loadfile \
  -f iam_2452_enabled=false \
  -f publish_to_domo=false \
  -f cleanup_roles=true \
  -f cleanup_user_groups=true \
  -f cleanup_user_accounts=true \
  -f generate_url=false \
  -f send_notification=false
```

5. Discover the test run ID using [Workflow Run Discovery](#workflow-run-discovery) with `workflow_file=automation-testing.yaml` and `branch=<branch>`. Save as `branch_test_run_id`, set `current_phase: 5` in `<ANALYSIS_DIR>/state.json`.

6. Tell user: **"Branch tests triggered (Run ID: XXXX). ~20 min. Say 'proceed' for final analysis."**

---

## Phase 5: Download Results + Compare + Analyze

**Entry condition:** `current_phase == 5`

1. **Download main artifacts** (skip if `reuse_main_artifacts` is `true`, or if `main-results/` already exists):
```bash
gh run download <main_test_run_id> --repo Trimble-Cloud-Core-Platform/iam --name allure-results --dir "$ANALYSIS_DIR/main-results"
gh run download <main_test_run_id> --repo Trimble-Cloud-Core-Platform/iam --name Allure-Single-Report --dir "$ANALYSIS_DIR/main-report"
```

Store main artifacts in cache after download:
```bash
python <skill_path>/scripts/cache_manager.py store --type main --repo Trimble-Cloud-Core-Platform/iam
```

2. **Download branch artifacts** (skip if `reuse_branch_artifacts` is `true`, or if `branch-results/` already exists):

Check branch test run status first when `branch_test_run_id` is set and `reuse_branch_artifacts` is `false`. If still running, tell user to wait.

```bash
gh run download <branch_test_run_id> --repo Trimble-Cloud-Core-Platform/iam --name allure-results --dir "$ANALYSIS_DIR/branch-results"
gh run download <branch_test_run_id> --repo Trimble-Cloud-Core-Platform/iam --name Allure-Single-Report --dir "$ANALYSIS_DIR/branch-report"
```

Store branch artifacts in cache after download:
```bash
python <skill_path>/scripts/cache_manager.py store --type branch --repo Trimble-Cloud-Core-Platform/iam
```

3. Run comparison script:
```bash
python <skill_path>/scripts/compare_allure_results.py \
  --baseline "$ANALYSIS_DIR/main-results" \
  --target "$ANALYSIS_DIR/branch-results" \
  --output "$ANALYSIS_DIR/comparison-report.json"
```

Where `<skill_path>` is the directory containing this SKILL.md.

4. Get PR diff (skip if `reuse_pr_diff` is `true` — use cached `pr-diff.patch`):
```bash
gh pr view <pr_number> --repo Trimble-Cloud-Core-Platform/iam --json title,body,files,headRefOid > "$ANALYSIS_DIR/pr-metadata.json"
gh pr diff <pr_number> --repo Trimble-Cloud-Core-Platform/iam > "$ANALYSIS_DIR/pr-diff.patch"
python <skill_path>/scripts/cache_manager.py store --type pr --repo Trimble-Cloud-Core-Platform/iam
```

5. **Generate shareable GitHub links** (required — include in report and show to user):
```bash
python <skill_path>/scripts/get_shareable_links.py \
  --output "$ANALYSIS_DIR/shareable-links.md"
```

This produces artifact download URLs in the same format as the `deploy-and-test` workflow summary:
`https://github.com/Trimble-Cloud-Core-Platform/iam/actions/runs/{run_id}/artifacts/{artifact_id}`

Works with `orchestrator_run_id`, `main_test_run_id` / `branch_test_run_id`, or **local artifact paths** when results were restored from cache (no run IDs in state).

6. **Analyze PR-introduced failures:** For each test in `new_failures` from the comparison report (includes both regressions and branch-only failing tests in `new_tests_failed`):
   - Read the test source from `tests/automation/tests/`
   - Cross-reference with PR diff to find which code change caused the failure
   - Classify as: **Code regression**, **Test update needed**, or **Flaky/environmental**

7. **Determine verdict** (required — show prominently at top of report). Use `counts.pr_introduced_failures` (or `new_failures` length — they are equivalent after comparison):

| Overall Result | Condition |
|----------------|-----------|
| **PASS** | Zero PR-introduced failures (`pr_introduced_failures == 0`) |
| **FAIL** | One or more PR-introduced failures (regressions or new failing tests) |

| Safe to Merge | Condition |
|---------------|-----------|
| **YES** | No PR-introduced failures, OR all are **Flaky/environmental** only |
| **CONDITIONAL** | PR-introduced failures are **Test update needed** only (product change is intentional; update tests before or immediately after merge) |
| **NO** | Any failure classified as **Code regression**, OR unclassified PR-introduced failures remain |

**Fixed tests** means tests that **failed on main and passed on branch** — not skipped or other status changes.

**Recommended further actions** (tailor to verdict — list only what applies):

| Situation | Action |
|-----------|--------|
| Code regression | Fix code in the files identified by PR diff; re-run analysis after push |
| Test update needed | Update automation tests to match new behaviour; reference `test_automation.instructions.md` |
| Flaky/environmental | Re-run tests once to confirm; if persistent, log as known flaky — do not block merge on flaky alone |
| Persistent failures (pre-existing) | Not caused by this PR — track separately; do not block this merge |
| Fixed tests | Note as positive signal — branch fixes existing failures |
| FAIL + NO merge | Do not merge until code regressions are fixed and analysis re-run shows PASS |
| PASS + YES merge | Safe to proceed with merge from a test perspective |
| CONDITIONAL merge | Merge only if team agrees tests will be updated in this PR or a fast-follow |

8. Present report using this format (also save to `<ANALYSIS_DIR>\analysis-report.md`). **Verdict must be the first section after the title.** Append `shareable-links.md` at the end. Always show Verdict + Shareable Links in the chat response:

```markdown
# Test Analysis Report

## Verdict

| | |
|--|--|
| **Overall Result** | PASS / FAIL |
| **Safe to Merge** | YES / NO / CONDITIONAL |
| **PR** | #{pr_number} — {branch} vs main |
| **Environment** | {environment} |

**One-line summary:** e.g. "FAIL — 2 new code regressions in devices BLU. Not safe to merge."

## Recommended Further Actions
1. [Highest priority action]
2. [Next action]
3. [Optional / follow-up]

## Test Results
| Metric | Main | Branch | Delta |
|--------|------|--------|-------|
| Total  | X    | X      | +/-   |
| Passed | X    | X      | +/-   |
| Failed | X    | X      | +/-   |

## New Failures (introduced by PR — regressions and new failing tests)
| # | Test Name | BLU | Classification | Likely Cause |
|---|-----------|-----|----------------|--------------|
| 1 | test_xxx  | accounts | Code regression | Changed validation in ... |

## Fixed Tests (failed on main → passed on branch)
| # | Test Name | BLU |
|---|-----------|-----|

## Persistent Failures (pre-existing, not PR-related)
| # | Test Name | BLU |
|---|-----------|-----|

<!-- paste shareable-links.md content below -->
```

9. **Archive to backup folder** (always run after analysis — do not delete):
```bash
python <skill_path>/scripts/archive_analysis.py
```

This moves all active artifacts into:
```
<ANALYSIS_DIR>/backups/<yyyy-MM-dd_HHmmss>_<environment>_<branch>/
```

Each backup contains: `state.json`, `comparison-report.json`, `pr-diff.patch`, `analysis-report.md`, `main-results/`, `main-report/`, `branch-results/`, `branch-report/`, and `manifest.json` (archive metadata with timestamp and paths).

10. Analysis complete. **Do not write or update `state.json` after archive** — it was moved to the backup folder. The next invocation starts fresh at Phase 1 when `state.json` is absent. Tell user:
   - **Verdict** (PASS/FAIL and Safe to Merge YES/NO/CONDITIONAL) — lead with this
   - **Recommended further actions** — numbered list
   - Backup folder path for local reference
   - **Shareable Links** with GitHub download URLs

---

## Shortcut: Skip to Comparison

If user says they already have reports or provides run IDs directly:
- Ask for **both** test run IDs (main and branch)
- Skip to Phase 5 (download + compare + analyze)
- Create `<ANALYSIS_DIR>/state.json` with `current_phase: 5`, `main_test_run_id`, `branch_test_run_id`, and all inputs (`pr_number`, `environment`, `branch`, `marker`, `data_region`)
- Set all `reuse_*` flags to `false` — Phase 5 step 1 downloads main, step 2 downloads branch
- Run `python <skill_path>/scripts/cache_manager.py resolve-shas --repo Trimble-Cloud-Core-Platform/iam` before any `store` calls (or use `store --repo`, which resolves SHAs automatically)

---

## Important Notes

- Always confirm with user before triggering deployments (shared environments).
- The automation-testing workflow exits with code 1 if tests fail — this is EXPECTED. Download artifacts regardless.
- Artifact retention: `allure-results` = 5 days, `Allure-Single-Report` = 14 days.
- All artifacts and state live under `<ANALYSIS_DIR>` (see [State Management](#state-management)) — outside the repo, no `.gitignore` needed.
- After analysis completes, artifacts are **archived** (not deleted) under `<ANALYSIS_DIR>/backups/`.
- **Cache** (`<ANALYSIS_DIR>/cache/`) is kept across runs — re-running the same unchanged PR reuses PR diff, main, and/or branch artifacts automatically.
- Requires `python` and `gh` on PATH (Windows, macOS, or Linux).
- To re-open a past run, point the comparison script at folders inside a backup directory.
- If `gh` commands fail with auth errors, tell user to run `gh auth login`.
