# TID Team Feedback Guidelines

Coding guidelines distilled from **recurring human reviewer feedback** in TID team PRs,
covering Backend (Python/Lambda), Infrastructure (CloudFormation/SAM/Terraform), and
UI/Frontend (JS/TS/React/SCSS).

**How this was built:**
Rules were synthesized and clustered from real PR review comments across the TID codebase
(462 clusters → 3 domain rule sets). Source: `synthesized_rules_462_clusters.xml`.

> Use these as review criteria: when generating or reviewing TID code, proactively apply
> the guidelines below before a human reviewer has to ask.

---

## Backend Rules

### 1. Function & Parameter Design

- **Require explicit parameters** — Always require and explicitly pass every mandatory
  attribute/parameter (`identity`, `email`, `given_name`, `family_name`, `iam_account_id`,
  etc.). Raise an error immediately when a required value is missing instead of silently
  substituting a default, and remove default values for parameters that are always required.
- **No mutable default arguments** — Use `None` as the default for mutable function
  parameters (lists/dicts), and initialize the mutable object inside the function body so
  every call starts clean.
- **Update every caller on signature changes** — When a public method's return type or
  signature changes (e.g. two-tuple to three-tuple, new parameters), update every caller to
  handle the new contract. Add new parameters at the end of existing signatures to preserve
  backward compatibility.
- **Cap method size and complexity** — Keep methods short (guideline: 15 lines for
  OAuth-file methods, 20 lines for general global methods, 50-line soft ceiling, 100-line
  absolute max) with no more than 5–10 parameters. Keep cyclomatic complexity at or below
  10, using early returns, extracted helpers, or Strategy/Command/State patterns instead of
  deep branching. Limit indentation to 3 levels globally (2 levels in
  `lambdas/dynamo_trigger/**`), and never use `\` line continuation. Keep modules/classes
  at or under 300 lines, and never exceed 1000.
- **Simplify conditional logic** — Break complex multi-condition `if` statements into
  smaller, commented conditions. Replace repeated if/elif chains with dictionary-based
  lookups/mappings. Assign boolean expressions directly to a variable instead of an
  if-block that only sets `True`. Use single-expression ternaries instead of nested
  if/else, declare variables outside conditional blocks rather than only inside an `else`
  branch, and keep conditional logic confined to the branch it belongs in rather than
  executing unconditionally.
- **Prefer `match`/`case` over long chains** — Prefer `match`/`case` statements over long
  if/elif/`isinstance` chains for multi-way branching on exception or condition types, and
  always include a default/wildcard case.

### 2. Error Handling & Exceptions

- **Catch specific exceptions only** — Never use a bare `except:`. Log caught exceptions
  with `logger.exception()` at the exact point they are handled — don't duplicate the same
  log at multiple layers. On failure, raise a descriptive custom exception rather than
  silently continuing or returning a default value, and never log-and-rethrow the same
  exception without added value. Where reasonable, consolidate per-type exception handlers
  into one parameterized handler.
- **Return generic errors externally, keep detail internal** — Raise/return precise
  internal `HTTPStatus` codes and diagnostic detail, but expose only generic client-facing
  messages (e.g. "Invalid input") externally. Mask sensitive values (e.g. raw emails) from
  any response, and avoid unnecessary IAM calls made purely for validation.
- **Explicit error responses, no silent fallbacks** — Return an explicit error response
  (e.g. `HTTPStatus.NOT_FOUND` with a descriptive JSON body) instead of silently serving a
  default fallback asset or value on error. Wrap JSON parsing (`json.loads`) in try/except
  to handle malformed input gracefully. Check for `None` before accessing
  attributes/methods, and catch exceptions like `HTTPError` to return a meaningful value
  instead of silently returning `None`.
- **Guard against infinite loops** — Give every loop a well-defined exit condition —
  bounded `for` ranges, or an explicit `break`/return inside `while` loops. Never write
  `while True` without a guaranteed exit.

### 3. Logging & Observability

- **F-strings, never manual concatenation** — Build every log/error message with f-strings
  (never `%s`-substitution or `+` concatenation).
- **Log only what's actionable** — Log actionable, contextual information immediately after
  the operation it describes — never generic text like "Error occurred", and never before
  the operation completes. Use severity levels correctly: `error` for real failures,
  `warning` for non-blocking issues, `debug` for verbose/cache-level data — never a
  blanket `info`/`warning` for everything.
- **Traceability and efficiency** — Include a UUID or correlation ID in log messages for
  cross-request traceability. Group/batch logger calls rather than scattering them
  line-by-line to reduce log volume and cost. Log the response body whenever an IAM/external
  API call returns a non-200 status — never silently `pass`. Log method entry/exit and
  error context around critical operations. Measure and log operation duration via
  start/end timestamps — never use exception handling as a timing mechanism.
- **Replace print, clean up dead logging** — Replace every `print()` with
  `logging`/`logger` calls. Remove unused functions, variables, imports, logger
  instances/parameters, unused global flags, commented-out code, and stale/resolved TODOs
  — every remaining TODO should state a clear plan. Keep imports alphabetically sorted,
  import each module exactly once, and never use wildcard `from module import *`.

### 4. PII & Data Protection

- **Mask PII before it's logged or queued** — Mask PII (e.g. via a shared `mask_email`
  helper that keeps the domain and replaces the local part with asterisks) before it is
  logged or included in any log/audit payload. Log only the UUID `user_id` to security
  logs — never raw emails or full user-info objects — and never log sensitive
  configuration/policy details.
- **Minimize response payloads** — Include only necessary, documented fields in API
  responses/cookies; never persist or return unused fields.
- **Exclude secrets from entity objects** — Exclude the `app_secret` field from federation
  entity objects/responses; expose secrets only via a dedicated accessor (e.g.
  `get_client_secret`).

### 5. Testing

- **Comprehensive, well-structured tests** — Add pytest (Python) / JUnit (Java) unit tests
  for every new function, changed branch, and edge case, including federation flows tested
  against enterprise Okta users, native users, and error paths. Separate test cases with
  blank lines, use `HTTPStatus` enum values (never raw status codes) in assertions, and
  split unrelated test sets into dedicated files.
- **Precise mocking** — Call `assert_called_once_with` with the full argument set
  (positional and keyword). Ensure mocks return the correct data type (e.g. tuples where a
  tuple is expected), and populate all required fields on `conftest.py` mock objects. Use
  the `moto` library to simulate AWS services instead of hand-rolled mock classes, and
  reuse existing test objects instead of duplicating instances.

### 6. Database & DynamoDB

- **Route access through a DAO/DB layer** — Route all database access through a dedicated
  DAO/DB layer — never call `db_layer` directly from higher-level business logic. Let DAO
  methods reference their own internal table name rather than accepting it as a parameter.
  Instantiate boto3 resources in `__init__`/as instance variables, never via a static
  factory method. Reuse parent-class helpers (e.g. `dynamo_response_to_json`) instead of
  duplicating response-handling logic, and extract shared DynamoDB query-parameter
  construction into one common helper.
- **DynamoDB batch limit and write validation** — Cap DynamoDB batch-get operations at
  `DYNAMO_BATCH_GET_LIMIT = 100` items or fewer. Build `ExpressionAttributeValues` with
  generic parameterized variables, never hardcoded literals. Validate data before writing —
  exclude `None` values and empty dicts, and only add optional fields to update expressions
  when present and non-None. Configure `TimeToLiveSpecification` at the template/DB level,
  not ad hoc in application code.
- **Cache repeated lookups** — Cache and reuse the result of any repeated DB call,
  list/API call, config lookup, or environment-variable read within a function instead of
  recomputing it. Memoize expanded scope results (e.g. via `functools.lru_cache`) and
  reuse a single `ThreadPoolExecutor` across requests.
- **Safe dictionary access** — Always use `.get(key, default)` with an explicit default —
  never bare indexing, an unguarded walrus assignment, or a bare `dict.pop(key)` — to
  avoid `KeyError`/`AttributeError`. Prefer `.get()` with a default over manual `if`/`or`
  None-checks.
- **Normalize IPs and headers before use** — Validate IP addresses with
  `validate_ip_address` before using them as a partition/entity key. Normalize header
  dictionaries once via a shared helper (e.g. `convert_keys_to_lowercase`) into a local
  `event_headers` variable rather than mutating `event['headers']` or checking multiple
  case variants inline.
- **Paginate outbound calls** — Include pagination parameters (e.g. `page_size`) on
  outbound API calls to retrieve complete result sets without extra repeated calls.

### 7. OAuth, JWT & Token Security

- **Validate and verify JWTs properly** — Verify a JWT has the correct number of segments
  before decoding, validate signatures with the correct key/algorithm/JWKS (`verify=True`,
  `verify_iss=True`), and never hardcode URLs/secrets or skip signature verification.
- **Token lifecycle and revocation** — Check token expiry and refresh access tokens locally
  within the lambda. Revoke a refresh token only via the same or a stronger authentication
  method than it was issued with — never downgrade to a weaker auth type for revocation.
  Require MTLS with PKCE wherever mixed auth is restricted.
- **Consistent claim naming** — Set `azp` to `initiating_client_id` and `client_id` to
  `application_id` as distinct claims — never assign the same value to both. Return a
  single `scope` field in token/response objects; never add a redundant `scopes` list.
- **PKCE handling** — Store PKCE parameters in a dedicated object that always carries
  `pkce_challenge` and `pkce_method`. Run PKCE validation before client-ID checks, and
  raise specific errors (e.g. "PKCE algorithm 'S256' not supported") — never a generic
  "Contact us" message.

### 8. Federation & SAML

- **Validate federation claims defensively** — Always validate that `federation_idp` exists
  before accessing its properties, and explicitly check for missing/required claims during
  federation flows. Log whether a federation lookup found a match or returned `None`.
- **No duplicate SAML entity IDs** — Before allowing reuse of a SAML entity ID, check via
  `dynamo.get_application_from_saml_entity_id` that it isn't already bound to another
  application; raise on conflict.
- **Propagate federation source faithfully** — Pass `federation_source` explicitly to every
  `audit()` call for MFA/sign-in events. Implement claim-processing generically via a
  database-driven mapping rather than hardcoding federation identifiers.
- **Consistent, safe federated ID handling** — Use consistent, space-free `id_type` values
  (e.g. `"azure_tenant"`, not `"Azure MarketPlace"`), and always check key existence before
  accessing federated ID-token payloads.

### 9. MFA & Account Security

- **Centralize MFA logic** — Centralize MFA logic (association, blocking, secure-method
  selection) into single, well-named functions. Store multiple MFA settings as an
  array/list, not separate flags. Update MFA settings only through a dedicated manager
  method, never by mutating fields directly.
- **User identity consistency** — Always assign `user_id` and `sub` together whenever a
  user identifier is obtained. Normalize (strip + lowercase) email addresses via a shared
  helper before every comparison. Drive limits like max user IDs from configuration, never
  a hardcoded literal.
- **Secure defaults and role checks** — Default security-sensitive flags (e.g.
  `enable_api_product`, `is_internal`) to `False`/deny-by-default. Never bypass role checks
  via an undocumented `skip_role_check=True`.
- **Password security** — Define password policies as named constants (never inline/magic
  numbers). Run password-history checks consistently on both account creation and update.
  Generate temporary passwords via a vetted library, and never hardcode sensitive values.
- **Authorize by action/resource, not path** — Authorize using explicit `action`/`resource`
  pairs from a predefined allow-list; never use the raw request path as the resource
  identifier.

### 10. Code Structure & Reuse

- **Extract and reuse shared helpers** — Move duplicated logic into shared helper modules or
  a base class. Centralize all token-validation logic into one shared `token_validator.py`,
  and centralize repeated flag/condition checks into a single reusable function.
- **Naming and type clarity** — Name modules, classes, and boolean methods/fields precisely
  for their responsibility. Use one consistent term for the same concept across the
  codebase. Annotate parameters and return types precisely with `typing` constructs/
  `TypedDict`/dataclasses instead of `-> dict`/`-> Any`.
- **Eliminate duplication** — Extract logic duplicated across files/methods into a single
  reusable function/module. Replace primitive-obsession patterns with proper wrapper types.
- **No global state** — Pass all required data as function parameters and return updated
  data explicitly, instead of storing state in module-level globals.
- **Module-scoped singleton clients** — Initialize expensive/shared clients (KMS, boto3
  resources, service objects) once at module scope or in `__init__`, not per call or inside
  handler functions.
- **Document non-obvious logic** — Document the intent of every non-obvious conditional
  branch with a comment. Validate required parameters and document expected values/usage in
  docstrings.

### 11. Auditing, Metrics & Triggers

- **Accurate, minimal audit payloads** — Extract only the specific required fields (e.g.
  `user_id`, `event_type`) for audit logs instead of passing the entire event body.
- **Correct metrics mapping** — Map trigger sources to metric events via an explicit lookup
  dict rather than hardcoding a single event, and reuse existing metrics utilities instead
  of duplicating metric logic.
- **Cognito trigger persistence** — Ensure every Cognito trigger handler persists event data
  via explicit save logic before completing.

### 12. Process & Code Review

- **Actionable, well-reviewed PRs** — Write PR review comments that are specific and
  actionable. Require at least two named-reviewer approvals before merging any PR —
  including global-scope changes — and escalate to a detailed review when a change spans
  more than 9 modules. Merge only via reviewed/approved feature-branch PRs, never directly
  into `global`/`develop`.
- **Clean merge hygiene** — Fully resolve all merge conflicts (no `<<<<<<<`/`=======`/
  `>>>>>>>` markers left) and squash commits into one before merging.
- **Keep architecture docs current** — Update architecture diagrams whenever new
  buckets/resources are introduced, and file unrelated or significant refactors as separate
  tickets rather than bundling them into unrelated changes.

---

## Infrastructure & IaC Rules

### 13. Templates & CloudFormation/SAM

- **API path naming** — Format every API Gateway path in `template.yml` using kebab-case
  (e.g. `/api/api-products`). Never use camelCase/PascalCase paths, and drop the legacy
  `/support/api` prefix from support-API paths.
- **No hardcoded Lambda function names** — Let CloudFormation auto-generate `FunctionName`
  values. Never pin them with `!Sub` or hardcoded strings in SAM templates.
- **No hardcoded IAM roles** — Define IAM roles as template `Parameters`/`!Ref` values.
  Never hardcode role ARNs directly in a template.
- **Region selection via conditionals** — Select region references through explicit
  conditionals instead of one hardcoded region ref. Never create primary-region-only
  resources inside secondary/DR region templates.
- **Password policy integrity** — Never remove or weaken `PasswordPolicy` attributes
  (`MinimumLength`, `RequireLowercase`, `RequireNumbers`, `RequireSymbols`,
  `RequireUppercase`, `TemporaryPasswordValidityDays`) without explicit, documented
  justification.
- **Cookie/header whitelist hygiene** — Document why each cookie/header is whitelisted in
  CloudFront/API Gateway policies, avoid duplicate entries, and include only what is
  functionally required.
- **Remove unused IaC resources** — Delete unused CloudFormation/Terraform resources,
  VPC/SQS endpoint entries, DynamoDB stream `EventSourceMapping`s, and log subscription
  filters for lambdas that no longer exist.
- **Granular Terraform dependencies** — Build `depends_on` lists dynamically instead of
  manually enumerating every module dependency.
- **API key auth over plaintext tokens** — Authenticate infrastructure/monitoring endpoints
  via an API Gateway `AWS::ApiGateway::ApiKey` + `x-api-key` header. Never pass tokens or
  passwords as plaintext template variables.

### 14. Regional, DR & Multi-Environment Configuration

- **Environment variables defined everywhere they're needed** — Region/environment-specific
  variables must be defined in *every* relevant template/region file, including new
  environments. Never leave one region's template with a missing or stale value.
- **DR variable file consistency** — Keep DR variable files consistent across regions and
  avoid unexplained divergence between them.
- **Central gen-vars file** — Manage region- and environment-specific configuration through
  one central `gen_vars`/`gen_vars.json` file with `@extends` inheritance, rather than
  duplicating or hardcoding values per environment file.
- **AWS account IDs and regions via parameters** — Always reference AWS account IDs, KMS
  key IDs, and regions through environment variables/parameters. Never hardcode literal
  account IDs or regions.
- **No single-region assumptions in scripts** — Never hardcode a single AWS region or
  endpoint in client initialization. Explicitly pass `region_name`, and build multi-region
  logic so URIs/config are derived per region instead of assumed.

### 15. Configuration Management & Secrets

- **Never hardcode secrets** — API keys, client IDs, IAM role/permission IDs, auth tokens,
  and certificates must never appear as literal values in JSON/YAML/config files. Source
  them from environment variables, AWS Secrets Manager, or an encrypted vault.
- **Precise, purposeful config keys** — Name configuration keys for exactly what they do
  (never generic or misleading names), document non-obvious settings and sensitive defaults
  with inline comments, and scope feature flags per environment/user-group.
- **Common vs. per-environment config separation** — Keep environment-specific settings only
  in their own per-environment file. `config_common.json` should contain only settings that
  truly apply to every environment, with zero duplication across files.
- **No unused function kwargs** — Define only the parameters a function actually uses, with
  type hints; never accept an unused `**kwargs` catch-all.
- **No external links or PII in shared code** — Never embed direct links to Jenkins, Google
  Docs, Jira, or similar external systems, and never share email addresses or other
  sensitive data in globally-visible code, comments, or configs.

### 16. DynamoDB & Data Scripts

- **Precise DynamoDB filters and indexing** — Use a named constant/variable for table
  names, add `attribute_exists(<key>)` to scan/query `FilterExpression`s instead of overly
  broad conditions, add secondary indexes for frequently filtered attributes, and prefer
  `query` with an index over `scan`.
- **Always paginate large reads** — Paginate DynamoDB/PartiQL reads for large datasets
  using `NextToken`/`batch_get`-style loops. Never rely on a single unpaginated fetch.
- **Parallelize migration I/O correctly** — In data-migration scripts, parallelize
  reads/writes using Python's built-in `multiprocessing` — never Dask, and never sequential
  per-ID reads. Cache repeated `time.time()` timestamps in one variable and reuse it.

### 17. Logging & Script Quality (Infrastructure)

- **Use logging, never print** — Always use the `logging` module (never `print`) in scripts
  and configuration builders. Log successes with `logger.info`, use `logger.exception` for
  caught exceptions.
- **F-strings and disciplined error handling** — Always use f-strings for log/error message
  formatting (never `%s`-style substitution). Only wrap code in try/except when the
  exception is actually handled — let it bubble up otherwise.
- **Script-level exception handling** — Always catch specific exception types (never a bare
  `except:`), and never log-then-rethrow the same exception without a clear reason.
- **Validate once, not repeatedly** — Validate input formats (e.g. email) once at the start
  of processing rather than multiple times; remove unused CLI arguments and dead code paths.

### 18. Security & Governance

- **Secure password handling in automation** — Always generate passwords securely and mark
  them non-temporary (`permanent_password=True`); never pass a temporary password with
  `permanent_password=False`.
- **Treat global scope as high-risk** — Any change under `global/**`, or any global
  configuration, session-management, or flow-triggering change, must be documented in a
  support-automation ticket and tested thoroughly for both functionality and security impact.

---

## UI & Frontend Rules

### 19. Conditional & Workflow Logic

- **Centralize flow-condition constants** — Move repeated `src_page`/flow-condition values
  into a shared constants file and branch on one derived boolean (e.g.
  `isConfiguredMfaPicker`). Never hardcode repeated `src_page`/parameter comparisons across
  multiple `if` conditions.
- **Single-parameter access-control helpers** — Access-control functions should take one
  well-defined parameter, not multiple fields fetched just to check one flag.
  Exemption-list route names must never include a leading slash.
- **Remove dead form logic** — Remove unnecessary null/undefined assignments, redundant
  nested `.catch()` handlers, and duplicate `case` branches that are already covered.
- **Cap method size and complexity** — Keep methods at or under 100 lines (target ~50) and
  avoid deeply branching conditionals; refactor each responsibility into its own small,
  single-purpose function.

### 20. Maintainability & Code Health

- **Reuse styles and classes** — Reuse existing CSS classes/utility styles (e.g.
  `text-secondary`) instead of defining new ones or overriding colors inline.
- **Refactor for maintainability** — Remove unused/redundant code, extract complex logic
  and `switch` statements into small reusable functions, and move shared logic into common
  utility modules (e.g. `error-mapping.ts`). Avoid unnecessary React `useState` hooks that
  are never reset.
- **Encapsulate Cognito methods** — Group all Cognito-related methods into a single
  dedicated object/module (e.g. `cognitoIdp`). Never attach unrelated methods to that
  object.
- **Extract nested helper logic** — In shared helper files (e.g. `form_helper.js`), extract
  nested/switch-heavy logic into small, named functions rather than deeply nested inline
  blocks.
- **Replace deprecated jQuery patterns** — Replace deprecated shorthand methods (e.g.
  `.click()`) with `.on("click", fn)` equivalents, and terminate every statement with a
  semicolon.

### 21. Forms, Inputs & Navigation

- **Scope input selectors to their form** — Always scope jQuery selectors to their
  containing form/context (e.g. `$('span.alias', form)`); never use unscoped global
  selectors. Source URLs from configuration rather than hardcoding them.
- **Unique error messages** — Every user-facing error message/key must be unique across
  step JS/HTML files. Never duplicate the same error text in more than one location.
- **Safe browser history management** — Always call `history.pushState({}, ...)` with a
  valid state object (never `null`), and use `window.history.pushState` instead of
  `location.replace` so users retain the ability to navigate back.

### 22. Styling (SCSS/CSS)

- **Organize styles for reuse and theming** — Move reusable styles into SCSS partials, use
  CSS variables for theming/sizing, and implement responsive design with media queries
  rather than inline media queries or fixed background positions. Style via classes rather
  than inline HTML styles or hardcoded fixed dimensions.
- **Consistent HTML punctuation/spacing** — Use consistent spacing and punctuation
  conventions around inline HTML tags (e.g. `<b>` phrases) across all step templates.

### 23. Translations & i18n

- **Keep translations consistent and current** — Translation strings must stay consistent,
  current, and free of duplicate/unused keys across every language and locale file. Use
  proper/escaped HTML entities (`&amp;`, `&lt;`, `&gt;`) or placeholders for dynamic
  content instead of embedding raw HTML tags in translation strings. Remove any translation
  key no longer referenced by code or build files.
- **Escape HTML entities everywhere** — Always escape `&`, `<`, and `>` (as `&amp;`,
  `&lt;`, `&gt;`) in both HTML markup and JS-generated text; never emit raw special
  characters.

### 24. UI Security & Privacy

- **Minimal user identifiers** — Only include identifiers (e.g. `user_id`) in UI requests
  when strictly required by the operation. Prefer hashed/derived identifiers over raw ones,
  and drop unused UUID fields.
- **No console logs in production** — Never leave `console.log` statements in production UI
  code; use a logging mechanism that is disabled in production instead.
- **Bundle critical assets, don't rely on third-party CDNs** — Bundle and serve critical
  scripts/resources from a CloudFront distribution you control. Never load them from
  third-party CDNs (e.g. `cdnjs.cloudflare.com`).

### 25. Performance & Environment Configuration

- **Minify below threshold, skip unneeded polyfills** — Minify/compress UI assets below a
  10KB threshold, and rely on modern-browser feature support instead of loading polyfills
  for features that are already supported.
- **Per-environment config files** — Load environment-specific values (e.g. hCaptcha site
  keys) from a dedicated per-environment file (`environment.<env>.js`) selected at
  build/runtime. Never hardcode environment-specific secrets/keys in shared config.
- **Keep external links verified and current** — Keep all external links/URLs in
  environment and workflow config up to date and verified, and reflect any change in related
  documentation/feature flags.
