# Collective Feedback Guidelines

Coding guidelines distilled from **recurring human reviewer feedback** across ~1,550 merged
PRs in `Trimble-Cloud-Core-Platform/iam`.

**How this was built (3-stage pipeline):**

1. **Vector embeddings** — every review comment (after filtering out bot reviews,
   acknowledgements and one-liners) is encoded with `sentence-transformers`
   (`all-MiniLM-L6-v2`), so semantically similar asks land next to each other.
2. **Clustering** — HDBSCAN groups ~8,400 comments into 144 tight themes.
3. **LLM synthesis** — each theme is distilled into a single definitive guideline below.

Reproduce with `scripts/cluster_feedback.py`; raw buckets live in
`references/feedback-clusters.json`. Each guideline notes how often the theme recurred.

> Use these as review criteria: when generating or reviewing IAM code, proactively apply
> the guidelines below before a human reviewer has to ask.

---

## 1. Logging & Observability

- **Never use `print()` for logging — use the logger.** Remove `print`/debug prints from
  source, tests, and scripts; if the information is needed, log it. _(recurred ~26x)_
- **Log at the correct severity.** Failures go to `ERROR`/`WARNING`, not `INFO`. Use
  `logger.exception` when the traceback aids debugging; don't log an error at `INFO` right
  after raising it. _(recurred ~10x)_
- **Emit exactly one entry log per API call**, containing path/query params for traceability.
  Do **not** re-log the full request payload, query params, or path params that API Gateway
  already logs — it only inflates CloudWatch. _(recurred ~9x)_
- **Never log PII or secrets.** No email, name, phone, tokens, `raw_token`, passwords, or
  whole event payloads. Extract only the specific, non-sensitive fields you need. _(recurred ~15x)_
- **Give log messages context.** Include identifiers like `account_id`, `user_id`, `ref` and
  a clear, unambiguous message so logs are debuggable on their own. _(recurred ~9x)_
- **Use structured/deferred logging, not f-strings, in log calls.** Prefer
  `logger.info("updating %s", relation)` over `logger.info(f"updating {relation}")`. _(recurred ~8x)_
- **When calling external services in scripts, log the response status code and body** and
  handle non-success status codes explicitly. _(recurred ~9x)_
- **Use the project's standard logger (`IAMLogger` from `logger_util`)** so logs carry the
  shared metadata; don't instantiate ad-hoc `Logger` imports or reach into logger internals
  (e.g. `logger.logger.level`). _(recurred ~6x)_

## 2. Error Handling & Exceptions

- **Don't catch generic `Exception` in the service layer.** Raise domain errors (e.g.
  `ApplicationError`) from service/DAL and let the common exception handler add the stack
  trace and response. Handle `NotFoundException` in the DAL or service, not everywhere. _(recurred ~9x)_
- **Re-raise with a bare `raise`, never `raise e`** — `raise e` resets the traceback and
  loses the original error context. _(recurred ~6x)_
- **Keep error responses generic; don't leak internals.** `ApplicationError` messages should
  carry only the error code and a safe detail message; set the HTTP status at raise time,
  not by hardcoding it in the enum. _(recurred ~7x)_
- **Follow the error-message style contract:** start with a capital letter, no trailing full
  stop, and keep wording consistent across BLUs. _(recurred ~9x)_
- **Wrap all DynamoDB/S3 calls in error handling** for `ResourceNotFoundException`,
  throttling, validation, and network errors; don't silently swallow failures and then log
  "success". _(recurred ~6x)_

## 3. Data Access & Transactions

- **Multi-write operations must be all-or-nothing.** Use transactional DAL operations across
  multiple DB writes so a partial failure can't corrupt state. _(recurred ~10x)_
- **Minimize DB round-trips.** Avoid redundant/duplicate reads (e.g. get-then-write when one
  hop suffices); batch reads/writes to avoid throttling. _(recurred ~10x)_
- **Keep persistence concerns inside the DAL.** Side effects like updating/deleting a unique
  key when an entity changes (incl. TTL) belong in the DAL, done transactionally — not
  exposed to or re-implemented by the service layer. _(recurred ~14x)_

## 4. Architecture & Layering

- **Validation belongs in the model layer.** Put field/request validation in the core
  (pydantic) models — reuse existing validated types (e.g. `Email`) instead of validating
  ad hoc in the service or duplicating the check. _(recurred ~24x across themes)_
- **One function, one responsibility.** A function named `is_consent_required` must return a
  bool; move side effects (sending invitations/notifications) to the caller. _(recurred ~8x)_
- **Reuse existing models and helpers; don't create near-duplicates.** Before adding a model
  or method, check for an existing one (e.g. `UserToAccount`, `find_relation`,
  `multi_authorization_check`, `fail_safe_request`) and reuse or extend it. _(recurred ~50x across themes)_
- **BLUs own their models; the common layer does not.** Put BLU-specific models in the BLU;
  only genuinely shared code goes in `common`. _(recurred ~9x)_
- **Prefer `match` statements over giant `if/elif` ladders**, and extract per-scenario logic
  into helper functions for readability and maintainability. _(recurred ~14x)_
- **Don't use module-level/global variables for request state** — pass values from the
  calling function instead. _(recurred ~13x)_

## 5. Naming & Readability

- **Don't encode a variable's type in its name.** Use `roles`, not `role_list`; pick a clean
  singular/plural name (`roleId` vs `roleIds`) based on cardinality. _(recurred ~9x)_
- **Keep parameter and resource-type naming consistent and unambiguous** (e.g.
  `resource_id`/`resource_type`), and align singular vs plural with the constants they
  reference. _(recurred ~9x)_
- **Name files by their contents.** e.g. a file of error strings should be
  `error_messages.py`, not `error.py` (which implies exception classes). _(recurred ~12x)_

## 6. Constants & Magic Values

- **Use `HTTPStatus` enums instead of raw status codes** (`HTTPStatus.CREATED`, not `201`). _(recurred ~17x)_
- **Extract repeated literals and hardcoded values into constants/config.** Move duplicated
  strings, error messages, and fixed dictionaries to a constant and reference it everywhere. _(recurred ~50x across themes)_
- **Never hardcode infra identifiers** (AWS account IDs, role IDs, region codes, ARNs, API
  Gateway IDs); derive them from variables/parameters/config. _(recurred ~40x across themes)_
- **Never hardcode UUIDs.** Generate with `uuid.uuid4()` or read from config. _(recurred ~6x)_

## 7. Type Hints & Documentation

- **Every function needs type hints, including the return type — even `-> None`.** _(recurred ~18x)_
- **Add docstrings to new and updated public methods** describing purpose, args, and return
  value; keep the `Raises:`/`Returns:` sections accurate to the implementation. _(recurred ~18x)_
- **Use modern typing.** Prefer `X | None` (PEP 604) over `Optional[X]`, and don't restate
  types that the hints already convey inside the docstring. _(recurred ~13x)_

## 8. Formatting & Lint (ruff / PEP 8)

- **Run `ruff format` before pushing.** Fix trailing whitespace, extra/missing blank lines
  (two blank lines around top-level functions), spaces after commas, and spacing around `=`
  (none for kwargs, single around operators). _(recurred ~60x across themes)_
- **Remove unused and duplicate imports; import at module level.** Unused imports/locals fail
  Ruff `F401`/`F841`; don't import inside functions or import the same module twice. _(recurred ~15x)_
- **Fix grammar in user-facing strings and error descriptions** (missing "when", "a" vs
  "an", etc.). _(recurred ~9x)_
- **Use f-strings for interpolation instead of `+` concatenation** — but don't wrap a plain
  string with no substitutions in `f""`. _(recurred ~18x)_

## 9. Dead Code, Comments & TODOs

- **Remove commented-out code.** Rely on version control; if kept intentionally, add a remark
  explaining why. _(recurred ~22x)_
- **Every `TODO` needs a clear description and/or Jira ticket** for accountability, e.g.
  `# TODO(IAM-123): ...`. _(recurred ~10x)_
- **Remove temporary/debug/experimental code before merge.** Don't leave "remove this later"
  code in the branch. _(recurred ~6x)_

## 10. Testing

- **Test files must be prefixed `test_`** and test names must match what they assert. _(recurred ~15x)_
- **Assertions must actually verify behavior.** Don't leave tests that assert nothing, assert
  against mocked-away values, or place asserts inside a `pytest.raises` block (they never
  run). Base API-test assertions on error codes/constants. _(recurred ~25x across themes)_
- **Avoid global variables in tests.** They create inter-test dependencies and `NameError`s
  when tests run independently; use fixtures or instance/class attributes. _(recurred ~7x)_
- **Mocks must match the real implementation** — patch the correct import path, mock every
  method the code actually calls, and use the real method signature/return type. _(recurred ~14x)_
- **Use `pytest.parametrize` for repetitive cases**, keep test data internally consistent,
  and add docstrings describing what each test covers. _(recurred ~29x across themes)_
- **Set explicit Allure titles per test** (dynamic titles fail when the failure is in a
  fixture and make parametrized cases indistinguishable). _(recurred ~11x)_
- **Add unit tests for every new method/branch**, including edge cases. _(recurred ~26x)_

## 11. Security & Supply Chain

- **Pin GitHub Actions to a commit SHA, not a mutable `@v1` tag**, to prevent supply-chain
  attacks and ensure reproducible builds. _(recurred ~8x)_
- **Reference reusable workflows via a stable ref (`@main`), never a feature branch.** _(recurred ~6x)_
- **Don't gate access with `contains()` on a serialized list string** — it matches
  substrings (a crafted username can slip through). Use a proper array membership check and
  keep allow-lists in repo variables. _(recurred ~9x)_

## 12. Configuration & Environment

- **Move hardcoded settings into external configuration**, and consolidate values that must
  be identical into a single config source. _(recurred ~10x)_
- **Resolve SSM parameters properly.** When an env var holds an SSM parameter path, resolve it
  to its value — don't use the raw path as the value. _(recurred ~8x)_
- **Config values must match their file's environment and region.** Keep `Environment`, region
  codes, ARNs, bucket names, and stack tags consistent with the path they live in. _(recurred ~50x across themes)_
- **Manage env vars via `.env`/config, not giant command lines**, and remove redundant
  lambda-level config. _(recurred ~15x)_

## 13. Datetime

- **Always use timezone-aware UTC datetimes** (`datetime.now(timezone.utc)`); never rely on
  naive/system-local time. _(recurred ~7x)_

## 14. JavaScript / TypeScript (GraphQL & k6)

- **Use `let`/`const`, never `var`,** and strict equality (`===`/`!==`); always declare
  variables to avoid implicit globals. _(recurred ~13x)_
- **Call `response.json()` once**, store it in a variable, and guard against JSON-decode
  errors before accessing fields — especially in hot loops. _(recurred ~8x)_

## 15. Pull-Request Hygiene

- **Commit `poetry.lock`** and keep the Poetry version consistent across the repo. _(recurred ~8x)_
- **When deferring work to a follow-up PR, link the ticket/PR** so the deferral is tracked
  and reviewers can approve with context. _(recurred ~20x)_
