# Kyle Controlled Hermes Update Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move Kyle's live Hermes runtime from the May 13 upstream base to current `origin/main` without losing the six local operational fixes or the ability to roll back.

**Architecture:** Build and test current upstream in an isolated worktree. Audit every local-only commit against current upstream, port only behavior that is still missing, and preserve each retained behavior with focused tests. Promote the verified commit to the stable `/Users/kyle/hermes-agent` path only after a data backup, source rollback branch, virtualenv backup, and live preflight checks exist.

**Tech Stack:** Git worktrees, Python 3.13 virtual environments, Hermes CLI/gateway, pytest through `scripts/run_tests.sh`, macOS `launchctl`.

---

### Task 1: Establish rollback points and isolated upstream

**Files:**
- Create: `docs/plans/2026-07-17-kyle-controlled-hermes-update.md`
- Preserve: branch `backup/kyle-live-pre-controlled-update-20260717`
- Preserve: `/Users/kyle/.hermes/backups/pre-controlled-update-20260717.zip`

**Steps:**

1. Verify the live checkout is clean and record its commit.
2. Create the backup branch at the live commit.
3. Create a full Hermes data backup.
4. Create `codex/kyle-controlled-hermes-update-20260717` from current `origin/main` in a separate worktree.
5. Confirm the live gateway still runs from the original checkout.

### Task 2: Build and baseline current upstream

**Files:**
- Create: worktree-local `.venv/` (ignored)

**Steps:**

1. Create a Python 3.13 virtual environment in the isolated worktree.
2. Install the editable package with runtime and development extras needed by gateway, cron, Telegram, Codex, and MCP tests.
3. Run `scripts/run_tests.sh` on the test files touched by the six local commits.
4. Record any upstream baseline failures before applying local patches.

### Task 3: Audit all six local commits against current upstream

**Files:**
- Inspect: `cron/jobs.py`, `cron/scheduler.py`
- Inspect: `gateway/config.py`, `gateway/platforms/telegram.py`
- Inspect: `agent/codex_responses_adapter.py`, `agent/auxiliary_client.py`, `run_agent.py`
- Inspect: `tools/mcp_oauth.py`, `tools/mcp_tool.py`
- Inspect: corresponding tests

**Steps:**

1. Audit cron persistence commit `ecde0708d` and Telegram commits `6508b5b49`, `a60efe709` against upstream behavior.
2. Audit Codex subscription commit `a4274e2dd` against upstream behavior.
3. Audit MCP commits `48e9708d0`, `fc3e0b041` against upstream behavior.
4. Classify each commit as upstream-equivalent, still required, or obsolete.
5. Identify focused behavior tests for every still-required patch.

### Task 4: Port only still-required behavior

**Files:**
- Modify only files justified by Task 3.
- Add or update behavior tests beside each retained patch.

**Steps:**

1. Run each relevant test on pristine upstream and confirm the missing behavior fails or is uncovered.
2. Apply the smallest compatible implementation on current upstream.
3. Run the focused test through `scripts/run_tests.sh` and confirm it passes.
4. Commit each independent behavior group with a Lore-format commit.
5. Confirm no unrelated upstream code was reverted.

### Task 5: Verify the candidate update

**Files:**
- No new files expected.

**Steps:**

1. Run `git diff --check` and inspect the full diff from `origin/main`.
2. Run all focused cron, Telegram, Codex, MCP, update, and gateway tests through `scripts/run_tests.sh`.
3. Run static compilation/import checks.
4. Run Hermes CLI version, doctor, MCP Plaud connection, and gateway startup preflights from the isolated worktree against a safe temporary `HERMES_HOME` where possible.
5. Confirm the live gateway has not been disturbed.

### Task 6: Promote with an immediate rollback path

**Files:**
- Preserve: `/Users/kyle/hermes-agent/.venv/` backup before dependency mutation.
- Update: live `/Users/kyle/hermes-agent` checkout and editable environment.

**Steps:**

1. Verify no taskcheck, cron, or interactive Hermes job is active.
2. Create a recoverable copy of the live virtualenv.
3. Stop the gateway and atomically reset the stable checkout to the verified candidate commit.
4. Reinstall/update dependencies in the stable virtualenv.
5. Restart the gateway and verify its process, logs, Telegram connection, Plaud tools, cron state, and no-browser OAuth canary.
6. If any live canary fails, reset to the backup branch, restore the virtualenv, and restart the previous gateway.

### Task 7: Finalize and document

**Files:**
- Update this plan with audit and verification results if useful.

**Steps:**

1. Confirm the stable checkout is clean at the candidate commit.
2. Keep the rollback branch, full data backup, and previous virtualenv until the user explicitly approves cleanup.
3. Report retained patches, upstream-equivalent patches, tests, live evidence, and remaining risks.
