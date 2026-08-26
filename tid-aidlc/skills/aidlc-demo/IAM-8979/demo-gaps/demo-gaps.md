# IAM-8979 demo gaps

Running log of mock-demo gaps for IAM-8979 (signal enablement, shadow-mode determination, `rate_limit_shadow_mode` seed). Append one block per ended session. Do not dump full Q&A. Repeating gaps are not rewritten.

## 2026-08-24T06:46Z — IAM-8979 signals + shadow kill-switch + flag seed

**Panel:** Priya (Junior Engineer), Marcus (Senior Engineer), Dana (Engineering Manager), Ravi (Technical Architect), Sam (VP of Engineering)   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Story vs tree — the kill-switch is not built:** Jira asks for `enabled_signals()`, `is_shadow()`, and seeding `rate_limit_shadow_mode` to **true** in common + dev (because a missing flag silently defaults to False). On disk: `enabled_signals()` only. No `is_shadow()`. No `FFM.rate_limit_shadow_mode()`. `configs-common.json` / `configs-dev.json` `iam/feature_flags` still have only 2452 / fedramp / cdh_sync. `_is_enabled` still returns **False** when the key is absent — the exact landmine the ticket claims to close.
- **Rate-limiting / concurrency:** `enabled_signals()` is a dict-comprehension over config. There is no `iam/rate_limit/signals` seed. Missing/empty → `[]` (RL-POLICY-012) → zero counters once wired. Phase-1 `["azp"]` exists only as a unit-test fixture, not in any env.
- **Timeout / fail-open:** `cfg.get("enabled")` assumes every value is a dict. A malformed signal row (`"azp": true` or a string) is `AttributeError` on the hot path. ConfigManager exceptions still have no framework-core guard on this branch.

## 2026-08-24T06:48Z — session 2: truthiness of `enabled`

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **`enabled: "false"` turns the signal ON:** Filter is `if cfg.get("enabled")` (truthy), not `is True`. JSON/DDB string `"false"` is truthy; `"true"` is truthy; `1`/`0` work by accident. Missing `enabled` is None → excluded (safe). No test for non-bool. Opposite of “operators flip a boolean in config.”

## 2026-08-24T06:50Z — session 3: no allowlist vs extractors

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Any key with `enabled: true` is “a signal”:** Tests enable `"ip"` and `"user_id"`. There is no registry (this branch has no `signals.py`). A typo `azpp` or a curious `ip` in prod config becomes an enabled signal. Orchestrator (when it exists) will `extract_signal` → None and skip, or worse, key a counter on a garbage name. Silent mis-config, no log.

## 2026-08-24T06:52Z — session 4: `shadow` on the signals blob is ignored

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Operators will think `shadow: false` means something:** Phase-1 fixture includes `"shadow": true` but `enabled_signals()` never reads it. Without `is_shadow()`, setting `shadow: false` in `iam/rate_limit/signals` does **nothing**. Combined with a missing flag that defaults False, the first person who implements LLD `cfg_shadow or FFM.flag` and then sets `shadow: false` in config **enforces** — because the seeded safety net is not there.

## 2026-08-24T06:54Z — session 5: 600s to enable/disable a signal

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **“Purely through config” is a 10-minute, mixed-fleet flip:** `get_global_config` uses the process cache (`do_refresh_check=False`). Enabling `sub` or disabling `azp` applies on cold start immediately and on warm containers at `CONFIG_REFRESH_TIME` (600s). Two Lambdas can disagree about which signals are metered for up to 10 minutes — different DDB write volume and different effective limits for the same caller.

## 2026-08-24T06:56Z — session 6: FeatureFlagManager default-False contract

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Absent flag ≠ safe:** `_is_enabled` → `flag.get("enabled", False)`. Non-bool raises `ValueError` (not fail-open). Jira’s seed (`enabled: true` in common + dev) is the only way “missing” becomes “shadow.” It is not in `configs-common.json`, `configs-dev.json`, or docker `default_configs.yaml`. QA/stage/prod were never mentioned — even a complete seed of common/dev leaves other stacks on False.

## 2026-08-24T06:58Z — session 7: OR kill-switch cannot force enforce

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **When `is_shadow` is built per LLD, the flag is one-way:** `shadow = cfg_shadow OR flag`. Flag can only **force shadow**, never force enforcement if the per-signal flag is still true. To enforce you must set **both** `shadow: false` in signals **and** flag false, and wait 600s. The ticket text (“kill switch”) sounds like an instant off. It is a slow, dual-control, shadow-only switch — and today it is neither implemented nor seeded.

## 2026-08-24T07:00Z — session 8: RL-POLICY-011 is a mocked fixture

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Phase-1 `["azp"]` is not an environment fact:** `test_enabled_signals_phase1_config_returns_azp` injects the blob. No `iam/rate_limit/signals` in global-configs. EARS RL-POLICY-011 (“shall report exactly azp given Phase-1 configuration”) is vacuously true in tests and false in every deployed env (empty → `[]`).

## 2026-08-24T07:02Z — session 9: T5 EARS have zero tests

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **RL-POLICY-020..022 are unchecked:** No `is_shadow` tests (config true, flag forces shadow, unset defaults shadow). `state.json` has T4 `done` and does not list T5. Ticket 8979 is In Progress and bundles T4+T5+seed. Calling T4 done while demoing 8979 as “shadow determination + seeded flag” is a status lie.

## 2026-08-24T07:04Z — session 10: dict order and unknown names

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Enabled list order is JSON key order:** Later `check()` will increment signals sequentially in that order. Reordering keys in `iam/rate_limit/signals` changes which signal is `next(iter(results))` / `exceeded[0]` for metrics (framework-core gap waiting to happen). No canonical sort (`azp` then `sub` then `account_id`).

## 2026-08-24T07:06Z — session 11: enablement without a consumer

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Flipping `azp.enabled` still meters nothing:** No `RateLimiter.check()`, no extractors, no middleware, no table. `enabled_signals()` is a pure config projection. Demo of “operators turn signals on per environment through config” is a list comprehension over a missing key. Ship the seed + `is_shadow` + flag accessor before presenting 8979 as done.
