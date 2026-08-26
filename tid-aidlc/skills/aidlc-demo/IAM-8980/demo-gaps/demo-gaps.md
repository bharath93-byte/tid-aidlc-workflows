# IAM-8980 demo gaps

Running log of mock-demo gaps for IAM-8980 (T6 threshold resolution + T7 resilience / kill-switch delay docs). Append one block per ended session. Do not dump full Q&A. Repeating gaps are not rewritten.

## 2026-08-24T06:49Z — IAM-8980 threshold chain + resilience + kill-switch delay

**Panel:** Priya (Junior Engineer), Marcus (Senior Engineer), Dana (Engineering Manager), Ravi (Technical Architect), Sam (VP of Engineering)   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **T6 is in code; T7 is not:** `threshold_for` / `_resolve_azp_threshold` implement azp override → global default → 1000, and skip override when `azp` is None (RL-POLICY-030..033, tested). T7 (merged into this ticket per Jira) is missing: no safe parsers, `route_rules()` still `RouteRule(**r)`, `enabled_signals()` still `cfg.get` on a maybe-non-dict, no `test_policy_resilience.py`. `state.json` marks T6 done and does not list T7. Ticket is In Progress for a reason.
- **Kill-switch delay is undocumented at the point of use:** `is_shadow` has no docstring. `FFM.rate_limit_shadow_mode()` does not mention cache. Policy-config LLD says “redeploy-free kill-switch” and “edits apply within 600s” but never says **warm Lambdas keep enforcing for up to 10 minutes** after the flag flips. That is the T7 doc deliverable.
- **Rate-limiting / concurrency:** Override lookup is `get_config` (**REGIONAL** default). Defaults are `get_global_config` (**GLOBAL**). A globally written `iam/rate_limit/azp/{azp}` is invisible; two regions can disagree. First sight of an azp can be a DDB GetItem on the request path (LLD admits this) — at 122 RPS a burst of new azps is a thundering herd of config reads, not counter reads.

## 2026-08-24T06:51Z — session 2: malformed config still raises

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **RL-POLICY-050/051 unmet:** Ticket: missing/malformed CONFIG_MGR entry degrades to no metering / shadow-only / default threshold. Reality: bad routes TypeError; `signals: {"azp": true}` → AttributeError on `.get`; `is_shadow` if the signal value is not a dict → AttributeError; override that is a string → no `.get`. Only *missing* keys are safe (`or []` / `or {}` / 1000). T7 hardening is the gap, not T6 happy path.

## 2026-08-24T06:53Z — session 3: `threshold_for("sub")` uses `azp_threshold`

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Non-azp signals inherit the application limit:** `if signal != "azp": return defaults.get("azp_threshold", 1000)` and skip the override lookup. Tests **encode** this (`test_threshold_for_non_azp_signal_uses_global_default`, duplicated twice in the file). Enabling `sub` later judges a human against 1000 req/min (or whatever azp default is), not a subject budget. No `sub_threshold` key is read.

## 2026-08-24T06:55Z — session 4: override type and zero/negative

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **`azp_threshold` is not an int contract:** `override.get("azp_threshold") is not None` then return as-is. `"2000"`, `Decimal("2000")`, `0`, `-1` all win. A zero override would make `effective_count > 0` breach immediately (strict `>`). A string may blow up later in the evaluator. No range check. Same for the global default path.

## 2026-08-24T06:57Z — session 5: azp in the config key

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Key is `iam/rate_limit/azp/{raw azp}`:** No encode/escape. Unusual `azp` values (`/`, `#`, very long) become odd ConfigManager keys or miss. A high-cardinality azp set means one cached entry per azp per container (LLD: “cached per distinct azp”). Memory on a busy Users Lambda is unbounded in azp count for 600s.

## 2026-08-24T06:59Z — session 6: `window_seconds` is cargo-culted

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Defaults blob includes `window_seconds` and nobody reads it:** Tests pass `{"azp_threshold": 1500, "window_seconds": 60}`. `threshold_for` only pulls `azp_threshold`. Store still hardcodes 60s minutes. Operators will edit `window_seconds` in `iam/rate_limit/defaults` and see no change. This ticket does not add `PolicyProvider.window_seconds()`.

## 2026-08-24T07:01Z — session 7: is_shadow truthiness + FFM ValueError

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Shadow flags are truthy, not bool:** `cfg_shadow or FFM...` — `shadow: "false"` is True → stuck in shadow. `FFM.rate_limit_shadow_mode()` → `_is_enabled` **raises ValueError** if `enabled` is not a bool (not fail-open). T7 said ConfigManager raises propagate; a bad **flag** value raises inside `is_shadow` the same way. Unset signal name: `signals.get(missing, {}).get("shadow", True)` → True (safe). Good default, still no 600s note.

## 2026-08-24T07:03Z — session 8: kill-switch is one-way and slow

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **“Kill switch” cannot force enforcement and is not instant:** OR semantics: flag only forces shadow. To stop 429s you flip the flag **true** and wait ≤600s on warm containers (cold starts see it immediately → mixed fleet). To start 429s you need `shadow: false` **and** flag false. Ticket asked to document this at `is_shadow` and in the LLD. Neither place says “not instant.” Ops runbook does not exist.

## 2026-08-24T07:05Z — session 9: no seeded defaults

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **`iam/rate_limit/defaults` and `iam/rate_limit/azp/*` are not in global-configs:** Every env falls through to hardcoded 1000. Override path is unexercised in any environment. Safe default works; “operators tune a noisy azp without a deploy” requires a key nobody has created and a REGIONAL vs GLOBAL write that may miss (session 1).

## 2026-08-24T07:07Z — session 10: RateLimitContext is only `azp`

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Context is a stub vs framework-core LLD:** Ticket adds `RateLimitContext.azp`. The dataclass is **only** `azp`. No `sub`, `account_id`, `identity_type`, `endpoint`. Fine for T6 in isolation; the next story that builds a real context will collide with this minimal type or fork a second dataclass (already happened on other branches). `threshold_for` cannot grow a subject/account tier without new fields.

## 2026-08-24T07:09Z — session 11: T7 not in state; nothing calls threshold_for

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Done-done is T6 unit tests only:** Duplicate test name `test_threshold_for_non_azp_signal_uses_global_default` (second definition wins). No resilience suite. No middleware calls `threshold_for`. No LLD/docstring T7 edit. Presenting 8980 as “hardened + delay documented” is false; presenting T6 “azp beats default beats 1000” is true in mocked tests only.
