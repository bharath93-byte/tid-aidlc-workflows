# IAM-8972 demo gaps

Running log of mock-demo gaps for IAM-8972 (framework-core middleware, sub/account_id extractors, DDB timeout classification). Append one block per ended session. Do not dump full Q&A. Repeating gaps are not rewritten.

## 2026-08-24T05:53Z — IAM-8972 framework-core middleware + signals + DDB timeout class

**Panel:** Priya (Junior Engineer), Marcus (Senior Engineer), Dana (Engineering Manager), Ravi (Technical Architect), Sam (VP of Engineering)   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Rate-limiting is a no-op in prod today:** Users BLU registers `RateLimitMiddleware` with `Phase1UsersPolicyProvider`, but `create_counter_store()` cannot import `DynamoDBCounterStore` (`store.py` absent) and falls back to `NoOpCounterStore` (`incr_and_read` → `(0.0, 0)`). Threshold 200 is never approached. Shadow "would fire" cannot happen. Story admits stubs; the room will still ask what is actually being demoed.
- **Timeout / Task-call / alarm path is dead:** `is_ddb_error` now treats `BotoCoreError` / connect-read timeout / `socket.timeout` as DDB (good). Factory then tries `EMFMetricsSink` (class does not exist; real name would be `EmfMetricsSink`) and silently uses `NullMetricsSink`. Correct classification never reaches CloudWatch/Datadog. The bug the story claims to fix is classified in-process and discarded.
- **Concurrency / cost when the real store lands:** `Phase1UsersPolicyProvider.enabled_signals()` is `["azp", "sub"]`. `RateLimiter.check()` loops them **sequentially** (LLD said parallel). Two `incr_and_read` per `GET /users/{userId}` — 2× latency vs the 20ms P99 budget, 2× WCU. No `emit_latency` around those calls.
- **Config-driven signals are a fiction on Users:** App injects `Phase1UsersPolicyProvider` (hardcoded route + azp/sub + threshold 200 + `is_shadow` always True). Editing `iam/rate_limit/signals` does **not** turn `account_id` on. Extractors exist; the policy stub ignores config. HLD Phase 1 was azp-only / threshold 1000 — stub already diverged.

## 2026-08-24T05:55Z — session 2: NullMetricsSink vs the timeout fix

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **`_create_metrics` ImportError is the real bug:** `from rate_limiter.metrics import EMFMetricsSink` fails (module only defines `NullMetricsSink`). Tests patch the store, not this import. A DDB connect timeout in `check()` emits `RateLimitDDBFailure` into a no-op sink. On-call still cannot see DynamoDB availability problems — the original symptom, now with better labels in a black hole.

## 2026-08-24T05:57Z — session 3: INTERNAL_API_GW_ID / proxied bypass

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Internal BLU-to-BLU can be metered:** `is_proxied_call` is in `common/src/common/proxied_call.py` (good; users re-exports). If `INTERNAL_API_GW_ID` is unset it **returns False** after a warning — header present is not enough. Cross-region / InternalApiGateway hops then hit the limiter. With a real store that double-counts trusted traffic; with today's NoOp it is only a landmine. HLD called `is_proxied_call` accuracy a High risk.

## 2026-08-24T05:59Z — session 4: TimeoutError over-classification

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Any `TimeoutError` is a "DDB failure":** `_DDB_ERROR_TYPES` includes stdlib `TimeoutError` and `socket.timeout`, and walks `__cause__`/`__context__`. A timeout in `get_token_data`, config, or an unrelated wrapper becomes `RateLimitDDBFailure` (once a sink exists) and pages the DDB alarm. Tests celebrate `TimeoutError("read timed out")` as True. Classification is now too wide, not too narrow.

## 2026-08-24T06:01Z — session 5: BaseException swallows process signals

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Fail-open catches `KeyboardInterrupt` / `SystemExit`:** Both guards use `except BaseException`. `test_check_catches_base_exception_subclasses` asserts KeyboardInterrupt → permissive + InternalError. A deploy drain or Lambda freeze can be converted into "serve the request anyway." LLD demanded BaseException; the room should treat that as an availability vs operability trade-off, not a free win. `except Exception` plus an explicit re-raise of `BaseException` would still fail-open on real bugs.

## 2026-08-24T06:03Z — session 6: clock, key format, hardcoded 60s window

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **`datetime.now` is naive local; keys ignore signal and window config:** Default `now_fn=datetime.now` (not UTC). `build_key` truncates to calendar minute, embeds the window in the PK (`rl#client#{value}#{endpoint}#{minute}`), and always prefixes `rl#client#` even when `signal=="sub"` or `"account_id"`. No `window_seconds` argument. When counter-store / IAM-8971 schema (window-independent PK, config window) lands, this facade will call the wrong `build_key` contract or collide azp/sub values on one client-shaped key.

## 2026-08-24T06:05Z — session 7: policy stub vs "config only" story

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Users wiring freezes Phase-1 policy in code:** `add_middleware(app, [create_rate_limit_middleware(policy=Phase1UsersPolicyProvider())])`. `account_id` extractor is registered but never enabled. `SafeDefaultPolicyProvider` (factory fallback) returns **empty** `route_rules` / `enabled_signals` — if anyone drops the explicit policy arg, the middleware matches nothing and looks "healthy." Enabling a signal is still a code change on this BLU, contradicting the Jira text.

## 2026-08-24T06:07Z — session 8: sequential multi-signal, no latency hook

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Orchestrator does not time DDB and does not parallelize:** LLD: parallel ops, `emit_latency` around each store call, ≤20ms P99. `check()` has no `on_latency`, no `asyncio`/`concurrent` fan-out. Two enabled signals (azp+sub) are a serial wait. Evaluator then reports `exceeded[0]` / `next(iter(results))` stats — not the worst signal — so a `sub` breach after a passing `azp` can log azp's count.

## 2026-08-24T06:09Z — session 9: 429 seam vs stub that cannot enforce

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Enforcement path is live in middleware, dead in policy:** `if not decision.allowed: return build_429_response()` is wired. Stub `is_shadow` is always True and NoOp count is 0, so Phase 1 never 429s (RL-CORE-062 holds by accident). Flip `is_shadow` to False in a one-line stub edit (or a future real policy) and Users starts 429ing with a JSON body that is **not** `TooManyRequestsError` / `ApplicationError` (`error`/`message` vs `error_code`/`detail`/`title`). No tests that the Users error mapper understands that shape.

## 2026-08-24T06:11Z — session 10: matcher + middleware order + DPoP

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Chain and match assumptions:** `add_middleware` prepends `AuthValidationMiddleware` only — LLD said after **DPoP**. Users test only checks Auth before RateLimit. Matcher uses `fnmatch` on `resource_path`; first enabled match wins. A future `"*"` / `"/users/*"` rule placed above `GET /users/{userId}` silently changes scope. Matching the **templated** path is correct only if every event exposes `request_context.resource_path`; a raw `/users/<uuid>` path would miss `{userId}` and skip limiting.

## 2026-08-24T06:13Z — session 11: unknown signals, missing table, Users-only

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Silent skip + deploy surface:** `extract_signal` returns `None` for unknown names (no log) — a typo in `iam/rate_limit/signals` looks like "no traffic." `iam-rate-limits` table is still T2 on-hold; swapping in a real store without the table is fail-open + (if metrics existed) a page storm. Only Users `app.py` registers the middleware; other BLUs unchanged. FC stories in `state.json` are marked done while the factory still cannot import policy/store/EMF — "done" means stub-complete, not identity-aware limiting.
