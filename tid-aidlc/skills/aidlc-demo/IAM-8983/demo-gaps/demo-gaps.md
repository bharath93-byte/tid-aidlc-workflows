# IAM-8983 demo gaps

Running log of mock-demo gaps for IAM-8983 (evaluation-response decision model, evaluator, breach classification, enforcement rollout gate). Append one block per ended session. Do not dump full Q&A. Repeating gaps are not rewritten.

## 2026-08-24T10:11Z — IAM-8983 evaluator + breach classes + rollout gate

**Panel:** Priya (Junior Engineer), Marcus (Senior Engineer), Dana (Engineering Manager), Ravi (Technical Architect), Sam (VP of Engineering)   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Ticket vs tree — no `evaluate()`, no gate:** Jira asks for `DefaultRateLimitEvaluator.evaluate()` (ALLOWED / WOULD_THROTTLE / THROTTLED) **and** an explicit go/no-go: compute Unmetered/(Metered+Unmetered) from shadow data before flipping any signal to enforce, else enable a fallback or write an accepted risk in `audit.md`. On disk: `RateLimitAction` + `RateLimitDecision.permissive()` in `context.py`, `RateLimitEvaluator` ABC in `ports.py`. **No `evaluator.py`.** No tests of the decision model. No `test_evaluator.py`. `audit.md` has T8 claimed/seams only — no blind-spot ratio, no acceptance row. Observability `visibility` dimension (needed to compute that ratio) is not on this branch (IAM-8971). `state.json` T8 = in-progress.
- **Rate-limiting / concurrency:** Without `evaluate()`, nothing classifies a sliding-window count vs threshold. Strict `>` and “evaluate all signals, `reset_epoch = max`” (ADR-008) are LLD/EARS only. A later sequential `check()` can still *increment* two signals; this story does not consume those tuples.
- **Timeout / fail-open:** `permissive()` is the intended fail-open decision (`allowed=True`, `ALLOWED`). It is unused — no `RateLimiter.check()` catch path on this tree. If someone constructs `RateLimitDecision(allowed=False, action=THROTTLED)` by hand, there is still no 429 (T10).

## 2026-08-24T10:13Z — session 2: T8 model exists, untested

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **RL-EVAL-001..012 cannot pass:** T8 ACs require a pure `evaluate()` for empty results, `effective == threshold` → allowed, no I/O. The ABC cannot be instantiated. `test_context.py` still only covers `build_key`. Decision fields match RL-EVAL-003 on the dataclass, but nothing asserts `permissive()` or frozen-ness. Audit said empty-results defaults 0/0/0 — that lives in a seam note, not code.

## 2026-08-24T10:15Z — session 3: T9 breach path is design-only

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **WOULD_THROTTLE / THROTTLED never returned:** Enum values exist; no loop `eff > thr`, no `policy.is_shadow`, no `any_enforced`. Multi-signal “enforce wins, `reset_epoch = max(exceeded)`” is unimplemented. Jira 8983 bundles T8+T9; jira-stories.json splits them (T9 blocked by T8). Demo of shadow vs enforce is a slide, not a function.

## 2026-08-24T10:17Z — session 4: rollout gate has no data plane

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Blind-spot ratio is undefined here:** Formula Unmetered/(Metered+Unmetered) needs `RateLimitEvaluated` with `visibility` (IAM-8971). This package has `Null`-less metrics — no sink at all. No dashboard query, no threshold for “high,” no owner, no `audit.md` template row. Operators cannot satisfy the gate 8983 says they must pass before enforcement.

## 2026-08-24T10:19Z — session 5: `permissive()` vs empty evaluate

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Two “allow” shapes:** `permissive()` is fail-open (error). Empty `results` should be “no signal metered” (also allow). Same `ALLOWED` / `allowed=True`. Observability must not treat them the same (one is `RateLimitInternalError`/`DDBFailure`, one is `visibility=unmetered`). The decision object has no `reason` / `signal=none` field. Downstream will collapse both into “allowed” metrics unless the caller remembers the exception path.

## 2026-08-24T10:21Z — session 6: frozen dataclass, mutable list

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **`exceeded_signals` is a mutable list on a frozen dataclass:** Rebinding is blocked; `.append()` is not. A later sink that mutates the list aliases across tests/requests. `effective_count` is float vs `threshold` int — sliding-window floats can sit `100.0000000002 > 100` (breach) or `nan > 100` is **False** in Python (never breach). Untested.

## 2026-08-24T10:23Z — session 7: first-signal stats / dict order (LLD trap)

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **When evaluate is copied from the LLD, allowed-path stats are `next(iter(results))`:** Insertion order = `enabled_signals()` JSON order. Breach path uses `exceeded[0]`, not the worst overshoot. `ctx` is unused in the LLD snippet. `RateLimitContext` is still only `azp` — evaluate cannot attribute `sub` vs `azp` in the decision besides `exceeded_signals` names.

## 2026-08-24T10:25Z — session 8: StrEnum vs log/metric strings

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Names are `ALLOWED` / values `"allowed"`:** Observability LLD samples `"action": "would_throttle"`. Using `.name` vs `.value` will break Datadog. `StrEnum` compares equal to the value, not the name. No tests lock `.value`. Middleware `if not decision.allowed` vs `action == THROTTLED` can diverge if someone builds a contradictory object (`allowed=True`, `action=THROTTLED`) — no `__post_init__` invariant.

## 2026-08-24T10:27Z — session 9: THROTTLED without T10 is a footgun

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Classification without a 429:** 8983 includes THROTTLED. T10 (`TooManyRequestsError` / `build_429_response`) is a separate story and is absent. If T9 lands and someone sets `shadow: false` before T10+middleware, `allowed=False` has **no** HTTP mapping — or a future middleware 429s with an ad-hoc body. Phase-1 “429 artifacts exist but never fire” (RL-EVAL-053) is false: they do not exist.

## 2026-08-24T10:29Z — session 10: empty `__init__.py` / no factory

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Package does not export the evaluator:** `__init__.py` is empty. `RateLimitEvaluator` is abstract. There is no `DefaultRateLimitEvaluator` to inject. Framework-core (IAM-8972) is not on this branch. `evaluate` purity (no I/O) cannot be shown; `policy.is_shadow` *will* I/O when T9 is written — that is a purity leak unless `is_shadow` is precomputed into `results`. LLD still calls `policy.is_shadow` inside `evaluate()`.

## 2026-08-24T10:31Z — session 11: status and blocker

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Blocked-by 8980 vs T8 `blockedBy: []`:** Jira 8983 is blocked by IAM-8980. Design T8 has no blocker. Evaluator does not call `threshold_for` (caller is supposed to pass already-resolved triples). The 8980 wait is process, not code. Presenting 8983 as “we classify breaches and have an enforcement gate” oversells a dataclass, an ABC, and a missing audit sentence.
