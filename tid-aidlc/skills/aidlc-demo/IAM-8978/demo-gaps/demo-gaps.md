# IAM-8978 demo gaps

Running log of mock-demo gaps for IAM-8978 (policy-config route rule loading). Append one block per ended session. Do not dump full Q&A. Repeating gaps are not rewritten.

## 2026-08-24T06:24Z — IAM-8978 policy-config route rule loading

**Panel:** Priya (Junior Engineer), Marcus (Senior Engineer), Dana (Engineering Manager), Ravi (Technical Architect), Sam (VP of Engineering)   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Rate-limiting coverage is "empty until someone inserts a key":** `route_rules()` reads `iam/rate_limit/routes` via `CONFIG_MGR.get_global_config`. Missing → `[]` (RL-POLICY-003). There is **no seed** of that key in SAM/Terraform/central-config fixtures. In every env today the list is empty, so even a wired middleware would meter **nothing**. "Config-driven coverage" is an empty inbox.
- **Timeout / fail-open is not this module's problem — and not present:** `RouteRule(**r)` and a raising `ConfigManager` both throw. LLD says ConfigManager errors propagate to framework-core fail-open. This branch has no middleware guard. A malformed routes blob on a hot path is an unhandled exception if anyone calls `route_rules()` from a handler.
- **Concurrency / cache:** No local cache (good). Relies on ConfigManager 600s. Enabling `GET /users/{userId}` or reordering rules is not "no deploy, instant" — warm Lambdas keep the old list for up to 10 minutes. `do_refresh_check` is never passed (`False`).

## 2026-08-24T06:26Z — session 2: RouteRule(**r) is not total

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Malformed config crashes the accessor:** LLD overview and RL-POLICY-050/051 require log-once + degrade to `[]`. Implementation is `[RouteRule(**r) for r in raw]` — extra keys, missing `enabled`, a string element, `enabled: "true"`, or a dict-shaped value all `TypeError`. T3 tests only happy list + `None`. Resilience is a later T7 story; the approved LLD already claimed totality. One bad rule poisons the **entire** list (no skip-and-continue).

## 2026-08-24T06:28Z — session 3: `or []` type confusion

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Falsy / wrong-shape values:** `raw = get_global_config(...) or []`. `{}` becomes `[]` (lucky). A stored JSON **string** `"[{...}]"` is truthy; iterating a string yields characters → TypeError. A dict-of-routes (ops paste an object instead of an array) iterates **keys** (strings) → TypeError. Empty list `[]` is untested (only `None`). No `isinstance(raw, list)` guard.

## 2026-08-24T06:30Z — session 4: 600s route flip is a slow kill-switch

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Turning a route off is not an emergency control:** First-match + `enabled: false` only works after cache refresh. A mistaken `"*"` / `enabled: true` rule (when matcher exists) stays live for ≤600s on warm containers. Cold starts see the new list immediately — mixed behavior in the fleet. No feature-flag override on `route_rules()` (shadow flag is a different story).

## 2026-08-24T06:32Z — session 5: Pydantic promised, dataclass delivered

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Schema drift vs LLD data models:** LLD: "All parsed via Pydantic with safe defaults." Code: frozen dataclass, no validators, no default `enabled=True`. `method` is not uppercased; `"get"` vs `"GET"` is the matcher's problem (matcher is not in this story). `route` is not required to be a templated API Gateway path. Invalid globs are stored as-is.

## 2026-08-24T06:34Z — session 6: incomplete PolicyProvider port

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **ABC is a time bomb for T4–T6:** `PolicyProvider` only abstracts `route_rules()`. Comments defer `enabled_signals` / `is_shadow` / `threshold_for`. The day those become abstract, `DynamoPolicyProvider` is instantly un-instantiable. Framework-core cannot depend on the port yet without isinstance hacks. `RouteRule` lives in `policy.py` while `ports.py` TYPE_CHECKING-imports it — a later `matcher.py` already grew a duplicate `RouteRule` on the 8972 branch.

## 2026-08-24T06:36Z — session 7: disabled rules still returned

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Loader does not filter `enabled: false`:** Ordered list includes disabled rows. Correct if the matcher skips them (RL-CORE-011). Nothing in T3 documents that contract. A naive caller that meters every returned rule would rate-limit disabled routes. No test that disabled rules are preserved in order (they are, in the happy-path fixture) **and** that callers must ignore them.

## 2026-08-24T06:38Z — session 8: get_global_config region/source assumptions

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **GLOBAL store only, default DB source:** `get_global_config` reads `ConfigRegionType.GLOBAL`. A regional-only insert of `iam/rate_limit/routes` is invisible. `config_src` defaults to DB — tests/local file source is unused. If GLOBAL vs REGIONAL conventions differ per env, Phase-1 `GET /users/{userId}` can be "configured" in the wrong partition and never load. Untested against a real ConfigManager.

## 2026-08-24T06:40Z — session 9: test surface is three cases

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **100% coverage, almost no behavior:** Tests: construct RouteRule; ordered map; `None` → `[]`. Missing: `[]` input, extra keys, missing fields, non-list, ConfigManager exception, empty-string method/route, duplicate rules, 20-rule list (first-match cost), `enabled` as 0/1. Coverage on a 10-line method is not evidence the production config shape works.

## 2026-08-24T06:42Z — session 10: blocked-by 8976 is package coupling only

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Jira blocker does not match the code dependency:** IAM-8978 is blocked by IAM-8976 (counter store). `policy.py` does not import `store.py`. The blocker is "share the `rate_limiter` package," not a functional need. Ops can read that as "cannot load routes until counters exist," which is false — and the reverse is also true: routes without a matcher still meter nothing.

## 2026-08-24T06:44Z — session 11: nothing consumes route_rules()

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Loader with no caller:** No middleware, no `match_route`, no Users registration, no seeded config. `state.json` marks T3 **done**. The demo can only show a mocked `get_global_config` returning three dicts. Shipping this as "the framework now knows which endpoints to meter" oversells a function that nobody calls and that prod config does not populate.
