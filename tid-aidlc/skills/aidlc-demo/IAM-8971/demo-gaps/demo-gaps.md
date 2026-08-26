# IAM-8971 demo gaps

Running log of mock-demo gaps for IAM-8971 (rate-limit observability + window / DDB schema / blind-spot). Append one block per ended session. Do not dump full Q&A.

## 2026-08-24T05:43Z — IAM-8971 observability + window/DDB/blind-spot

**Panel:** Priya (Junior Engineer), Marcus (Senior Engineer), Dana (Engineering Manager), Ravi (Technical Architect), Sam (VP of Engineering)   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Rate-limiting / concurrency (hot key):** Counter PK is now window-independent (`rl#client#{value}#{endpoint}`). Every increment for an azp+endpoint lands on one DynamoDB item. Original LLD spread writes across per-minute items. At 122 RPS on `GET /users/{userId}`, a single noisy azp is a hot-partition risk. No sharding in Phase 1.
- **Timeout / extra WCU:** Happy path is one `UpdateItem` (ALL_NEW). After an idle gap, `_sweep_orphaned_attrs` issues a second `UpdateItem`. Sweep errors are swallowed; `RateLimitDDBLatency` still only dimensions `operation=UpdateItem` (GetItem is gone; EARS RL-OBS-012 still lists GetItem). P99 alarm can fire on the sweep path without distinguishing it.
- **Window resize without deploy:** `window_seconds` from `iam/rate_limit/defaults` now drives bucket math, but ConfigManager cache is ≤600s. Resizing 60→120 (or the reverse) reuses minute-named attributes on the same item with a new epoch alignment — no migration, no versioned key. Mid-flight resize can mis-weight `previous_attr` or look like a counter reset.
- **Task-call / monitor spend:** Datadog queries in `rate-limit-monitors.tf` use unverified placeholders (`aws.iam.ratelimit.rate_limit_ddb_failure` etc.) with TODOs. `terraform validate` was not run in the implementation env. On-call pages for DDB failure / latency may never fire until names are confirmed after first EMF emission.
- **Blind-spot metric vs log:** `RateLimitEvaluated` now has `visibility=metered|unmetered` (azp or sub present). Breach log still hardcodes `"signal": "azp"`. `build_key` always prefixes `rl#client#` even if the value is `sub`. Operators reconstructing a `sub` breach will mis-attribute.
- **Observability fail-open is silent:** `EmfMetricsSink.emit` / `emit_failure` / `emit_latency` use `except Exception: pass`. LLD required a debug log. A broken sink hides DDB failures from the very monitors meant to page.
- **LLD / EARS drift:** Counter-store LLD still documents 2-item PK + GetItem. Observability LLD has no `visibility` dimension and says `RateLimitEffectiveCount` unit is None; code uses `MetricUnit.Count`. Story is blocked by IAM-8980 (policy-config / kill-switch delay).

## 2026-08-24T05:50Z — session 2: wiring / missing orchestrator

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Sink is unwired:** No `RateLimitMiddleware`, `RateLimiter`, `evaluator.py`, `errors.py`, or `policy_stub.py` exist. `common/src/rate_limiter/__init__.py` is empty. `metrics.py` comments cite `rate_limiter.policy_stub.Phase1UsersPolicyProvider` and `rate_limiter.errors.is_ddb_error` — neither module is in the tree. EMF / breach logs / DDB failure pages cannot fire in any BLU until framework-core is implemented and registered via `add_middleware`.

## 2026-08-24T05:52Z — session 3: Datadog log query vs IAMLogger envelope

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Shadow-breach monitor will not match:** `IAMLogger.warning()` wraps the payload as `{"data": <dict>}`, so the field is `@data.event` (or similar), not `@event`. `RateLimitShadowBreach_review` queries `logs("... @event:rate_limit_would_fire")`. Threshold-review alerts stay silent even after the sink is wired. Distinct from the unverified *metric-name* TODO already logged.

## 2026-08-24T05:54Z — session 4: window_seconds type coercion

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Config type trap:** `window_seconds()` accepts only `isinstance(value, int) and value > 0`. DynamoDB / JSON often yield `Decimal("60")` or `60.0` (or `"60"`). Those fail the check, log a warning, and silently stay on 60. There is no unit test of `DynamoPolicyProvider.window_seconds()` itself — only downstream `build_key` / formula tests with a hardcoded int.

## 2026-08-24T05:56Z — session 5: sub threshold reuses azp_threshold

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **`threshold_for("sub")` is wrong by construction:** Non-`azp` signals skip the override chain and return `defaults["azp_threshold"]` (else 1000). Tests encode this (`test_threshold_for_non_azp_signal_uses_global_default`). Comments claim `sub` now meters alongside `azp`, so a subject would be judged against the application aggregate limit, not a per-`sub` budget. Phase-3 `sub` enablement via config would over-throttle humans or under-throttle M2M.

## 2026-08-24T05:58Z — session 6: RateLimitDecision contract drift

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Decision object does not match evaluation LLD:** Code is `{action, effective_count, threshold, window: str}`. LLD requires `allowed`, `exceeded_signals`, `shadow`, `reset_epoch`. Sink recomputes `exceeded` as `effective_count > threshold` (good — same `>` rule) but cannot name *which* signal breached. No evaluator exists to populate `window`; tests pass the literal `"1m"` while LLD logs show an ISO minute. Multi-signal Phase 2 has nowhere to put `max(reset_epoch)`.

## 2026-08-24T06:00Z — session 7: table not provisioned (T2 on-hold)

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **`iam-rate-limits` table is not in this repo's Terraform:** Audit has T2 (table provisioning) on-hold (`tmp/rl-T2-rate-limits-table-2`). Grep of `setup/` finds no `iam-rate-limits`. Shipping the store + sink without the table means every check is a DDB resource error → fail-open + (if monitors ever match) a Sev-1 page storm, or silent if names/queries are still wrong.

## 2026-08-24T06:02Z — session 8: ddb_layer ALL_NEW blast radius

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Global `update_item` now always returns ALL_NEW:** `common/src/db/ddb_layer.py` hardcodes `ReturnValues: ALL_NEW` for every caller, not just the rate-limiter. Unrelated IAM updates (users, devices, relations) now pay larger DynamoDB return payloads on the hot path. Rate-limiter needed ALL_NEW; the rest of the platform did not. Regression/cost blast radius is outside IAM-8971's stated scope.

## 2026-08-24T06:04Z — session 9: monitor SLO + shared event name

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Burst SLO and Phase-2 mix-up:** Vision required a Datadog monitor that surfaces a breach burst within 60s. Implemented log monitor is `last("15m") > 100` — 15× slower, and 100 is a guess. Both `would_throttle` and `throttled` emit the same `event: rate_limit_would_fire`, so after enforcement cutover the "review thresholds" monitor cannot tell shadow from real 429s. DDB-failure monitor is Sev-1 on `sum > 0` over 2m — one transient throttle pages on-call (alert fatigue vs fail-open).

## 2026-08-24T06:06Z — session 10: EMF volume + failure dimensions

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Per-request EMF cost and unscoped failures:** Happy path emits 2 `single_metric` blobs; a breach emits 3. At 122 RPS that is ~244–366 extra log-embedded metrics/sec, per region, before other BLUs onboard. `emit_failure` / `RateLimitDDBFailure` have **no** `endpoint` or region dimension — on-call cannot tell which route or region failed. `RateLimitContext.identity_type` defaults to `"application"`, so missing claim data is counted as M2M on every dashboard.

## 2026-08-24T06:08Z — session 11: clock skew, key injection, item-size, ADD+REMOVE collision

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Concurrency / clock / item growth:** Window labels come from each Lambda's clock (`_window_start` / `fromtimestamp`). Skewed containers ADD different minute attributes on the **same** hot item, so `previous_attr` can miss and under-count. `azp`/`sub` values with `#` are interpolated into `rl#client#{value}#{endpoint}` with no escaping. If orphan sweep keeps failing, attributes accumulate toward DynamoDB's 400KB item limit; a later `ADD` then fails the whole increment (fail-open, but the limiter is blind). Same-expression `ADD #cur` + `REMOVE #stale` is unsafe if a resize ever makes `current_attr == stale_attr` (DynamoDB rejects two updates to one attribute in one call).
