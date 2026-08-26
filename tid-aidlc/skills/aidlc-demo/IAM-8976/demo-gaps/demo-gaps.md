# IAM-8976 demo gaps

Running log of mock-demo gaps for IAM-8976 (sliding-window counter store foundation). Append one block per ended session. Do not dump full Q&A. Repeating gaps are not rewritten.

## 2026-08-24T06:22Z — IAM-8976 sliding-window counter store foundation

**Panel:** Priya (Junior Engineer), Marcus (Senior Engineer), Dana (Engineering Manager), Ravi (Technical Architect), Sam (VP of Engineering)   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Rate-limiting / concurrency (two clocks):** `build_key(..., now)` embeds the calendar minute in the PK, but `incr_and_read` recomputes `window_start` / `secs_into_window` from `self._now()`. Two `now()` calls can straddle a minute: ADD hits the old PK, weight is computed for the new minute, `previous_partition_key` is the wrong neighbour. That is not the ADR-005 ~1% approximation — it is a real mis-count. Tests inject one clock into the store and a matching `build_key` now; they never cross the seam.
- **Timeout / partial failure:** UpdateItem commits, then GetItem throws → error propagates (good for fail-open) but the increment **sticks**. A blip of GetItem errors ratchets every azp up while every request is allowed. No compensation, no "increment only after both ops."
- **Table does not exist:** `RATE_LIMIT_TABLE` defaults to `iam-rate-limits`. No Terraform/SAM in `setup/`. T2 is the provisioning story. Shipping this store alone is ResourceNotFound on every check.
- **Jira vs code:** Story promised `RateLimitContext` + `SignalKey` + `CounterStore` + `DynamoDBCounterStore`. There is no `RateLimitContext`. `__init__.py` is empty (nothing exported).

## 2026-08-24T06:24Z — session 2: sequential Update+Get vs 20ms budget

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Two serial RTTs, previous read could be parallel:** Current ADD and previous GetItem use **different** keys and do not depend on each other. LLD/EARS freeze 2 sequential ops (RL-STORE-024). At 122 RPS this is 2× P99 vs a parallel fan-out, and `on_latency` is optional — if the orchestrator never passes it, `RateLimitDDBLatency` never exists. Budget ≤20ms is hoped, not measured.

## 2026-08-24T06:26Z — session 3: UPDATED_NEW vs ALL_NEW + Attributes KeyError

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **EARS RL-STORE-021 unmet; fragile read of the increment:** LLD/EARS require `ReturnValues=UPDATED_NEW`. `ddb_layer.update_item` hardcodes `ALL_NEW` for the whole platform (larger payload on every IAM update, not just this store). `incr_and_read` does `update_resp["Attributes"]` then `attrs["count"]` — no default. A missing Attributes blob (or a layer change) is KeyError, not a cold-start zero.

## 2026-08-24T06:28Z — session 4: key format ignores signal, `#`, path params

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **PK is not signal-safe or path-safe:** Always `rl#client#{value}#{endpoint}#{minute}`. `signal` is stored on `SignalKey` and never used. `sub` / `account_id` later collide with azp if values overlap. `#` in azp is unescaped. `normalise_endpoint` does not strip `{userId}` — tests use `/users/userId` → `GET-users-userId`; middleware will pass `/users/{userId}` → `GET-users-{userId}`. If anyone passes a concrete UUID path, cardinality explodes (one item per user, not per route).

## 2026-08-24T06:30Z — session 5: hardcoded 60s calendar minute

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Window is not a parameter:** Formula, TTL (`+120`), `_window_end_epoch` (`+1 minute`), and `now.second` for `secs_into_window` all assume a 60s wall-clock minute. `iam/rate_limit/defaults.window_seconds` cannot change behaviour. A later "resize window without deploy" story has to rewrite keys and math. `seconds_into_window > 60` (skew / naive clock) yields a **negative** weight.

## 2026-08-24T06:32Z — session 6: GetItem eventual consistency

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Previous window is eventually consistent by default:** `ddb_layer.get_item` uses `CONSISTENCY_MODE` (default **eventual**). Just after a minute roll, the previous item's last ADD may still be in-flight on a replica. Under-count → under-throttle. Strong consistency is a global IAM flag, not a store choice — flipping it taxes every other GetItem. No `ConsistentRead=True` override on this path. Untested.

## 2026-08-24T06:34Z — session 7: naive clock / DST / empty package

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Injectable `now` is not validated:** Store default is UTC (`datetime.now(timezone.utc)`). `build_key` / `_window_end_epoch` call `.replace` / `.timestamp()` on whatever they are given. A naive `datetime` is local wall time — labels and `reset_epoch` disagree across regions. No test. Empty `__init__.py` means `from rate_limiter import DynamoDBCounterStore` fails; callers must know the private module path.

## 2026-08-24T06:36Z — session 8: TTL vs DynamoDB deletion delay

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **TTL is "best effort, up to 48h":** `expire_at = window_end + 120` satisfies "previous survives the next window" only if DynamoDB deletes on time. Late delete is OK (extra items). Early/late combined with clock skew can make GetItem see a stale previous **or** a not-yet-deleted window from hours ago if labels somehow collide. No alarm if TTL is not enabled on the table (T2 on-hold) — items grow forever.

## 2026-08-24T06:38Z — session 9: hot minute-item + no shard hook

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **One PK per azp+endpoint+minute still hot at 122 RPS:** Writes rotate every 60s (better than a lifetime PK) but a single noisy azp still hammers one item for a full minute. ADR-013 sharding is "reserved in the key format" — the format has **no** `#shard{n}` slot today. Adding it later is a new key, not a reserved field. On-demand capacity does not fix a hot partition.

## 2026-08-24T06:40Z — session 10: test gaps vs claimed EARS

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Tests never miss `Attributes`, never use templated paths, never cross minute in `incr_and_read`:** Coverage is unit/mocked ddb_layer. No test for: GetItem after successful ADD; `now` vs key minute mismatch; `/users/{userId}` normalisation; naive datetime; `seconds_into_window` at 59.999s; `on_latency is None` (default prod path). RL-STORE-021 (UPDATED_NEW) is not asserted. "19 tests, 100% coverage" can still miss the production seams.

## 2026-08-24T06:42Z — session 11: foundation is unwired

**Panel:** Priya, Marcus, Dana, Ravi, Sam   **Intensity:** grill   **Answers:** auto via Cursor Grok 4.6

- **Nothing in a BLU calls this yet:** No middleware, no factory, no `RATE_LIMIT_TABLE` in Users/SAM. Fail-open (RL-STORE-050) is "propagate to framework-core" — framework-core is not in this tree. A raw `incr_and_read` exception would currently be an unhandled Lambda error if someone called the store directly. Story is correctly foundational; it is not a demo of rate limiting working.
