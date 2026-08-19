---
name: add-iam-api-endpoint
description: Scaffold a new API endpoint in an IAM BLU. Collects API path, HTTP method, request/response payloads, and target BLU, then generates the model, DAO, service, app route, and pytest. Use when the user wants to add a new API endpoint, route, or REST operation to an IAM BLU.
---

# Add IAM API Endpoint

You are an API scaffolding expert for the IAM service. You add new REST endpoints to an existing BLU (Business Logic Unit) by following the established patterns in the codebase.

## Step 1: Gather Requirements

Use the AskQuestion tool to collect the following from the user. If AskQuestion is unavailable, ask conversationally.

### Questions to ask

1. **Target BLU** — which BLU does this endpoint belong to?
   - Options: applications, users, groups, roles, devices, organizations, bootstrap, authorization
2. **HTTP Method** — GET, POST, PUT, DELETE
3. **API Path** — e.g. `/applications/<application_id>`
4. **Request payload** (JSON example) — skip for GET/DELETE unless query params are needed
5. **Response payload** (JSON example)
6. **Brief description** of what the endpoint does (one sentence)

Store the answers for use in later steps. Refer to them as: `BLU`, `METHOD`, `PATH`, `REQUEST_JSON`, `RESPONSE_JSON`, `DESCRIPTION`.

---

## Step 2: Explore the Target BLU

Read the following files in the target BLU to understand existing patterns:

```
iam/<BLU>/src/app.py        — route definitions, decorators, resolver
iam/<BLU>/src/service.py    — business logic layer
iam/<BLU>/src/dao.py         — data access layer (if it exists, some BLUs use dal.py)
iam/<BLU>/src/models.py     — Pydantic models
iam/<BLU>/src/error_codes.py — ErrorCode enum
iam/<BLU>/tests/conftest.py — fixtures and mocks
iam/<BLU>/tests/test_app.py — existing tests
```

Also read these common files for shared types:

```
iam/common/src/common/models.py      — EdgeProperties, Cursors, Links, TokenData, etc.
iam/common/src/common/constants.py   — path constants, entity refs, BluCode
iam/common/src/common/lambda_helper.py — get_token_data, build_response, get_payload, etc.
```

**Pay attention to**:
- How existing endpoints in `app.py` are decorated (`@app.get`, `@app.post`, etc.)
- How the service method signatures look (token_data, subject, authorization_check pattern)
- How models inherit from `EntityBase`, `Meta`, `TrnModel`, `Edge`, `BaseModel`
- How error codes are structured in `error_codes.py`
- How existing tests mock dependencies (mocker.patch patterns)
- How the `conftest.py` mocks `db.app` and provides fixtures

---

## Step 3: Create or Reuse Models

Based on `REQUEST_JSON` and `RESPONSE_JSON`:

1. **Search** `iam/<BLU>/src/models.py` and `iam/common/src/common/models.py` for any existing model that matches the request or response structure.
2. **Reuse** if a matching model already exists.
3. **Create new models** only if no match is found.

### Model conventions

- Request models extend `BaseModel` from pydantic.
- Response models typically extend a combination of `EntityBase`, `Meta`, `TrnModel`, and optionally `Edge` (for relation data).
- Field names use camelCase (matching the API contract). Use pydantic `Field` for validation constraints.
- Place new models in `iam/<BLU>/src/models.py`.
- Add the new model names to existing import blocks in `app.py` and `service.py`.

---

## Step 4: Add Error Codes (if needed)

If the new endpoint can produce unique errors (e.g. "already exists", "not found", "forbidden"), add entries to `iam/<BLU>/src/error_codes.py`.

Follow the existing pattern:

```python
ERROR_NAME = (
    "<BLU_PREFIX>_NNN",          # unique code — use next available number
    HTTPStatus.<STATUS>.value,   # HTTP status
    "Message with {} placeholders",
    "Description for documentation"
)
```

Use the next available numeric code in the existing sequence.

---

## Step 5: Add DAO Method (if needed)

If the endpoint requires a new data access operation, add a method to `iam/<BLU>/src/dao.py` (or the BLU's equivalent DAL file, e.g. `dal.py`).

Follow the existing pattern:
- Thin wrapper around `db.app` functions (`find_resource`, `add_resource`, `list_resources`, `add_relation`, etc.)
- Use `EntityTypes` and `EntityRelations` enums for type refs and relation names
- Log success with the IAMLogger

If the BLU has no `dao.py` or `dal.py`, check how the service accesses data and follow that pattern.

---

## Step 6: Add Service Method

Add the business logic method to `iam/<BLU>/src/service.py`.

### Standard service method structure

Follow the established pattern observed in the BLU:

```python
def <method_name>(self, <params>, token_data: TokenData) -> <ResponseModel>:
    # 1. Extract subject
    subject: Subject = get_subject(None, token_data)

    # 2. Validate entities exist (if referencing existing resources)
    #    e.g. self.validate_account(account_id)

    # 3. Authorization check
    self.authorization_check(
        token_data, subject, Action.<ACTION>,
        constants.<TYPE_REF>,
        ErrorCode.<FORBIDDEN_CODE>, <context_id>
    )

    # 4. Business logic (DAO calls, transformations, validations)

    # 5. Build and return response model
```

### Key conventions
- Always perform authorization check using `self.authorization_check`
- Use `get_subject(None, token_data)` to extract the subject
- Use `get_meta_data(entity.meta)` to convert meta to response format
- Use `Trn(resource_type=..., resource_id=...).to_string()` for TRN generation
- Raise errors via `raise_application_error(ErrorCode.XXX, *args)`

---

## Step 7: Add App Route

Add the endpoint to `iam/<BLU>/src/app.py`.

### Route conventions

```python
@app.<method>(
    <PATH_CONSTANT>,
    summary='<Short summary>',
    description='<DESCRIPTION>',
    response_description='<Response description>',
    responses={
        <success_status>: {
            'description': 'Success',
            'content': {'application/json': {'model': <ResponseModel>}},
        },
        400: VALIDATION_ERROR,    # or inline dict with error_content
        403: ACCESS_ERROR,
        404: DATA_ERROR,          # if applicable
        500: INTERNAL_SERVER_ERROR
    }
)
def <function_name>(<path_params>):
    # For POST/PUT: extract payload
    payload: dict = get_payload(app.current_event)
    request_model = <RequestModel>(**payload)

    # Extract token data
    token_data: TokenData = get_token_data(app.current_event)

    # For endpoints under /accounts: get account_id
    # account_id = get_account_id(app.current_event, token_data)

    # Call service
    result = <blu>_service.<method_name>(<args>, token_data)

    # Audit log (for state-changing operations: POST, PUT, DELETE)
    audit_logger.log_with_event(
        event=app.current_event,
        token_data=token_data,
        target_object={"id": <resource_id>, "type": <TYPE_REF>},
        event_type=f"IAM: {<BLU>Event.<EVENT_NAME>}"
    )

    return build_response(HTTPStatus.<STATUS>, result.model_dump_json(
        exclude_none=True, exclude_unset=True
    ))
```

### Key conventions
- GET endpoints: use `query_string_parameters` for filters/pagination
- POST/PUT endpoints: use `get_payload(app.current_event)` for body
- Path params come from angle-bracket placeholders in the route
- Add audit logging for state-changing operations (POST, PUT, DELETE)
- Return `HTTPStatus.OK` (200) for GET/PUT, `HTTPStatus.CREATED` (201) for POST, `HTTPStatus.NO_CONTENT` (204) for DELETE
- Place the new route before the `@app.exception_handler` block and after existing routes

If the path needs a new constant, add it to `iam/common/src/common/constants.py`.

---

## Step 8: Write Tests

Create tests in `iam/<BLU>/tests/test_app.py` (append to existing file).

### Required test cases

For **every** new function, write tests at two levels:

#### A. Service-level tests

Test the service method directly using the existing service fixture pattern (e.g. `application_service`):

1. **Success case** — happy path, assert return type and key fields
2. **Authorization forbidden** — mock `authorization_check` to raise `ApplicationError(403, ...)`
3. **Resource not found** — mock validation/DAO to raise `NotFoundException`
4. **Conflict / duplicate** (if applicable) — mock DAO to return existing record

#### B. Endpoint-level test

Test the full endpoint through `lambda_handler`:

1. **Success case** — mock the service method, set up `lambda_event`, assert `statusCode` and response body structure

### Test conventions (follow existing patterns in the BLU)

```python
# Service-level test
def test_<method>_success(<service_fixture>, mocker):
    mocker.patch('service.get_subject', return_value=MagicMock())
    <service_fixture>.authorization_check = MagicMock(return_value=True)
    # Mock DAO methods on <service_fixture>.<dao_attr>.<method>
    # Call the service method
    # Assert result

# Endpoint-level test
def test_<method>_endpoint_success(<app_fixture>, mocker, lambda_event, lambda_context, user_token):
    mocker.patch('app.<service_var>.<method>', return_value=<ResponseModel>(...))
    lambda_event["path"] = "<path>"
    lambda_event["httpMethod"] = "<METHOD>"
    lambda_event["requestContext"]["authorizer"]["token_data"] = json.dumps(user_token)
    # For POST/PUT:
    lambda_event["body"] = json.dumps({...})

    response = <app_fixture>.lambda_handler(lambda_event, lambda_context)
    assert response["statusCode"] == <expected_status>
    body = json.loads(response["body"])
    # Assert body fields
```

### Import rules for tests

- Imports that depend on `db.app` (which is mocked in `conftest.py`) must be done **inside** test functions or fixtures, not at the top of the file. This includes the service class and DAO class.
- Imports from `db.dal_models`, `common.models`, `error_codes`, `models` (Pydantic models), and `unittest.mock` can be at the top level.

---

## Step 9: Verify

1. Run `ReadLints` on all modified files to check for linter errors. Fix any introduced errors.
2. Present a summary of all changes:
   - New/modified models
   - New error codes (if any)
   - New DAO method (if any)
   - New service method
   - New app route
   - New test cases

---

## Checklist

Track progress with this checklist:

```
- [ ] Requirements gathered (BLU, method, path, payloads, description)
- [ ] Existing BLU code explored and patterns understood
- [ ] Request model created or reused
- [ ] Response model created or reused
- [ ] Error codes added (if needed)
- [ ] DAO method added (if needed)
- [ ] Service method implemented
- [ ] App route added
- [ ] Service-level tests written
- [ ] Endpoint-level test written
- [ ] Linter errors checked and fixed
- [ ] Summary presented
```
