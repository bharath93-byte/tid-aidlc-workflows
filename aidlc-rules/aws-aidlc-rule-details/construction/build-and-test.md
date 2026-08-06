# Build and Test

**Purpose**: Build all units and execute comprehensive testing strategy

## Prerequisites
- Code Generation must be complete for all units
- All code artifacts must be generated
- Project is ready for build and testing

---
## Step 0: Skill Discovery & Selection (MANDATORY — do not skip on resume)
- Execute `common/skill-discovery-gate.md` **before any other step in this stage**
- Create `aidlc-docs/build-and-test-skill-selection.md`; wait for user to fill `[Answer]:` and confirm
- Update `## Current Stage Skill` in `aidlc-docs/aidlc-state.md`; log resolved choice in `audit.md`
- **Do not** proceed to Step 1 until Step 0 is complete

## Step 1: Analyze Testing Requirements

Analyze the project to determine appropriate testing strategy:
- **Unit tests**: Already generated per unit during code generation
- **TDD workflow**: Confirm red-green-refactor loop and failing-test-first workflow for any new fixes or enhancements
- **Integration tests**: Test interactions between units/services
- **Gherkin scenarios**: Validate business behavior with Given/When/Then scenarios and scenario-to-test traceability
- **EARS traceability**: Roll up EARS status markers (`[x]`/`[ ]`/`[D]`) across all files under `aidlc-docs/inception/requirements/ears/` to confirm actual implementation state matches what Code Generation reported
- **Performance tests**: Load, stress, and scalability testing
- **End-to-end tests**: Complete user workflows
- **Contract tests**: API contract validation between services
- **Security tests**: Vulnerability scanning, penetration testing
- **Coverage gates**: Define line/branch/function thresholds and enforcement commands for CI and local runs

---

## Step 2: Generate Build Instructions

Create `aidlc-docs/construction/build-and-test/build-instructions.md`:

```markdown
# Build Instructions

## Prerequisites
- **Build Tool**: [Tool name and version]
- **Dependencies**: [List all required dependencies]
- **Environment Variables**: [List required env vars]
- **System Requirements**: [OS, memory, disk space]

## Build Steps

### 1. Install Dependencies
\`\`\`bash
[Command to install dependencies]
# Example: npm install, mvn dependency:resolve, pip install -r requirements.txt
\`\`\`

### 2. Configure Environment
\`\`\`bash
[Commands to set up environment]
# Example: export variables, configure credentials
\`\`\`

### 3. Build All Units
\`\`\`bash
[Command to build all units]
# Example: mvn clean install, npm run build, brazil-build
\`\`\`

### 4. Verify Build Success
- **Expected Output**: [Describe successful build output]
- **Build Artifacts**: [List generated artifacts and locations]
- **Common Warnings**: [Note any acceptable warnings]

## Troubleshooting

### Build Fails with Dependency Errors
- **Cause**: [Common causes]
- **Solution**: [Step-by-step fix]

### Build Fails with Compilation Errors
- **Cause**: [Common causes]
- **Solution**: [Step-by-step fix]
```

---

## Step 3: Generate Unit Test and TDD Execution Instructions

Create `aidlc-docs/construction/build-and-test/unit-test-instructions.md`:

```markdown
# Unit Test Execution

## TDD Workflow (Mandatory for New Changes)

For each defect fix or enhancement:
1. **Red**: Write or update a failing test first
2. **Green**: Implement the smallest code change to pass
3. **Refactor**: Improve code while keeping tests green
4. **Re-run**: Execute full unit test suite and confirm no regressions

Record each cycle in a short table:
- Test name
- Initial failure reason
- Fix summary
- Refactor summary
- Final status

## Run Unit Tests

### 1. Execute All Unit Tests
\`\`\`bash
[Command to run all unit tests]
# Example: mvn test, npm test, pytest tests/unit
\`\`\`

### 2. Review Test Results
- **Expected**: [X] tests pass, 0 failures
- **Test Coverage**: [Expected coverage percentage]
- **Test Report Location**: [Path to test reports]

### 2.1 Coverage Gate Verification (Mandatory)
- **Line Coverage Target**: >= [X]%
- **Branch Coverage Target**: >= [X]%
- **Function Coverage Target**: >= [X]%
- **Coverage Command**:

\`\`\`bash
[Command to produce coverage report and enforce thresholds]
# Example: npm test -- --coverage, pytest --cov --cov-fail-under=85, mvn test jacoco:report
\`\`\`

- **Coverage Artifact(s)**: [coverage.xml/html path, lcov path, jacoco path]
- **Gate Result**: [Pass/Fail]

### 3. Fix Failing Tests
If tests fail:
1. Review test output in [location]
2. Identify failing test cases
3. Fix code issues
4. Rerun tests until all pass
```

---

## Step 4: Generate Integration Test Instructions

Create `aidlc-docs/construction/build-and-test/integration-test-instructions.md`:

```markdown
# Integration Test Instructions

## Purpose
Test interactions between units/services to ensure they work together correctly.

## Test Scenarios

Each integration scenario must include one or more Gherkin scenarios and a verification checklist.

### Gherkin Scenario Template
\`\`\`gherkin
Feature: [Business capability]

     Scenario: [Scenario title]
          Given [initial context]
          When [action/event]
          Then [expected outcome]
\`\`\`

### Gherkin Verification Checklist (Mandatory)
- Scenario title maps to an executable test name
- Given preconditions are implemented in setup steps or fixtures
- When action is represented by a concrete API/UI/service interaction
- Then assertions validate observable outcomes (status, payload, state, side effects)
- Pass/fail status is captured in summary report

### Scenario 1: [Unit A] → [Unit B] Integration
- **Description**: [What is being tested]
- **Setup**: [Required test environment setup]
- **Test Steps**: [Step-by-step test execution]
- **Expected Results**: [What should happen]
- **Cleanup**: [How to clean up after test]

### Scenario 2: [Unit B] → [Unit C] Integration
[Similar structure]

## Setup Integration Test Environment

### 1. Start Required Services
\`\`\`bash
[Commands to start services]
# Example: docker-compose up, start test database
\`\`\`

### 2. Configure Service Endpoints
\`\`\`bash
[Commands to configure endpoints]
# Example: export API_URL=http://localhost:8080
\`\`\`

## Run Integration Tests

### 1. Execute Integration Test Suite
\`\`\`bash
[Command to run integration tests]
# Example: mvn integration-test, npm run test:integration
\`\`\`

### 2. Verify Service Interactions
- **Test Scenarios**: [List key integration test scenarios]
- **Expected Results**: [Describe expected outcomes]
- **Logs Location**: [Where to check logs]
- **Gherkin Verification Result**: [Pass/Fail with scenario count]

### 3. Cleanup
\`\`\`bash
[Commands to clean up test environment]
# Example: docker-compose down, stop test services
\`\`\`
```

---

## Step 5: Generate Performance Test Instructions (If Applicable)

Create `aidlc-docs/construction/build-and-test/performance-test-instructions.md`:

```markdown
# Performance Test Instructions

## Purpose
Validate system performance under load to ensure it meets requirements.

## Performance Requirements
- **Response Time**: < [X]ms for [Y]% of requests
- **Throughput**: [X] requests/second
- **Concurrent Users**: Support [X] concurrent users
- **Error Rate**: < [X]%

## Setup Performance Test Environment

### 1. Prepare Test Environment
\`\`\`bash
[Commands to set up performance testing]
# Example: scale services, configure load balancers
\`\`\`

### 2. Configure Test Parameters
- **Test Duration**: [X] minutes
- **Ramp-up Time**: [X] seconds
- **Virtual Users**: [X] users

## Run Performance Tests

### 1. Execute Load Tests
\`\`\`bash
[Command to run load tests]
# Example: jmeter -n -t test.jmx, k6 run script.js
\`\`\`

### 2. Execute Stress Tests
\`\`\`bash
[Command to run stress tests]
# Example: gradually increase load until failure
\`\`\`

### 3. Analyze Performance Results
- **Response Time**: [Actual vs Expected]
- **Throughput**: [Actual vs Expected]
- **Error Rate**: [Actual vs Expected]
- **Bottlenecks**: [Identified bottlenecks]
- **Results Location**: [Path to performance reports]

## Performance Optimization

If performance doesn't meet requirements:
1. Identify bottlenecks from test results
2. Optimize code/queries/configurations
3. Rerun tests to validate improvements
```

---

## Step 6: Generate Additional Test Instructions (As Needed)

Based on project requirements, generate additional test instruction files:

### Contract Tests (For Microservices)
Create `aidlc-docs/construction/build-and-test/contract-test-instructions.md`:
- API contract validation between services
- Consumer-driven contract testing
- Schema validation

### Security Tests
Create `aidlc-docs/construction/build-and-test/security-test-instructions.md`:
- Vulnerability scanning
- Dependency security checks
- Authentication/authorization testing
- Input validation testing

### End-to-End Tests
Create `aidlc-docs/construction/build-and-test/e2e-test-instructions.md`:
- Complete user workflow testing
- Cross-service scenarios
- UI testing (if applicable)
- Gherkin scenarios for each critical user journey
- Scenario traceability between product requirement, test case, and execution result

---

## Step 7: Generate Test Summary Report

Create `aidlc-docs/construction/build-and-test/build-and-test-summary.md`:

```markdown
# Build and Test Summary

## Build Status
- **Build Tool**: [Tool name]
- **Build Status**: [Success/Failed]
- **Build Artifacts**: [List artifacts]
- **Build Time**: [Duration]

## Test Execution Summary

### Unit Tests
- **Total Tests**: [X]
- **Passed**: [X]
- **Failed**: [X]
- **Coverage**: [X]%
- **Status**: [Pass/Fail]

### Coverage Gate Summary (Mandatory)
| Metric | Actual | Target | Status |
|--------|--------|--------|--------|
| Line Coverage | [X]% | [X]% | [Pass/Fail] |
| Branch Coverage | [X]% | [X]% | [Pass/Fail] |
| Function Coverage | [X]% | [X]% | [Pass/Fail] |

### Integration Tests
- **Test Scenarios**: [X]
- **Passed**: [X]
- **Failed**: [X]
- **Status**: [Pass/Fail]

### Gherkin Scenario Verification (Mandatory)
| Feature | Scenario | Linked Test | Result |
|---------|----------|-------------|--------|
| [Feature name] | [Scenario name] | [Test ID/Name] | [Pass/Fail] |

### EARS Requirements Traceability (Mandatory)

Roll up status markers from every file under `aidlc-docs/inception/requirements/ears/`. If any test that a status marker relies on is failing, the marker must be `[ ]`, not `[x]` — reconcile discrepancies here rather than trusting Code Generation's self-report blindly.

| EARS File | Total | `[x]` Implemented | `[ ]` Gap | `[D]` Deferred | Discrepancies Found |
|-----------|-------|--------------------|-----------|-----------------|----------------------|
| [feature-subfeature-ears.md] | [X] | [X] | [X] | [X] | [None / list IDs corrected] |

**Overall EARS Coverage**: [X]% implemented ([X] of [X] non-deferred requirements)

### Failed Scenario Analysis (If Any)
- **Scenario**: [Name]
- **Failure Type**: [Assertion/Error/Timeout/Environment]
- **Root Cause**: [Summary]
- **Remediation**: [Action taken or planned]

### Performance Tests
- **Response Time**: [Actual] (Target: [Expected])
- **Throughput**: [Actual] (Target: [Expected])
- **Error Rate**: [Actual] (Target: [Expected])
- **Status**: [Pass/Fail]

### Additional Tests
- **Contract Tests**: [Pass/Fail/N/A]
- **Security Tests**: [Pass/Fail/N/A]
- **E2E Tests**: [Pass/Fail/N/A]

## Overall Status
- **Build**: [Success/Failed]
- **All Tests**: [Pass/Fail]
- **Coverage Gates**: [Pass/Fail]
- **Gherkin Verification**: [Pass/Fail]
- **EARS Coverage**: [X]% implemented
- **Ready for Operations**: [Yes/No]

## Next Steps
[If all pass]: Ready to proceed to Operations phase for deployment planning
[If failures]: Address failing tests and rebuild
```

---

## Step 8: Update State Tracking

Update `aidlc-docs/aidlc-state.md`:
- Mark Build and Test stage as complete
- Update current status

---

## Step 9: Present Results to User

Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 🔨 Build and Test Complete
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of build and test results
        - Format: "Build and test has completed with the following results:"
        - List build status and artifacts
        - List test results by category (unit, integration, performance, etc.)
            - Include coverage gate outcome and Gherkin verification outcome
        - List generated instruction files
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the build and test summary at: `aidlc-docs/construction/build-and-test/build-and-test-summary.md`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the build and test instructions based on your review
> ✅ **Approve & Continue** - Approve build and test results and proceed to **Operations**

---
```

---

## Step 10: Log Interaction

**MANDATORY**: Log the stage completion in `aidlc-docs/audit.md`:

```markdown
## Audit Log Rules (Tabular Format - Mandatory)

1. Use a single markdown table for all stage entries (do not append free-form blocks).
2. Append one row per Build and Test execution.
3. Use ISO 8601 IST timestamp (`YYYY-MM-DDTHH:mm:ss+05:30`).
4. Include **User** (actor) as the user name only — never include email.
5. Keep status values normalized: `Success|Failed` and `Pass|Fail|N/A`.
6. Include coverage and Gherkin verification outcomes in dedicated columns.

| Timestamp (IST) | User | Stage | Build Status | Test Status | Coverage Gates | Gherkin Verification | Summary Report | Files Generated |
|-----------------|------|-------|--------------|-------------|----------------|----------------------|----------------|-----------------|
| [2026-08-04T18:04:56+05:30] | [User name only] | Build and Test | [Success/Failed] | [Pass/Fail] | [Pass/Fail] | [Pass/Fail] | [aidlc-docs/construction/build-and-test/build-and-test-summary.md] | [build-instructions.md; unit-test-instructions.md; integration-test-instructions.md; performance-test-instructions.md; build-and-test-summary.md] |

---
```

---

## Step 11: Generate Regression Test Cases (Final Step)

Create `aidlc-docs/construction/build-and-test/regression-test-cases.md`:

```markdown
# Regression Test Cases

## Purpose
Define a stable regression suite to validate previously working behavior after fixes, refactors, dependency updates, and release changes.

## Regression Case Rules
1. Include coverage across unit, integration, and end-to-end critical paths.
2. Include all previously failed scenarios that were remediated.
3. Include high-risk business workflows and boundary conditions.
4. Every case must include traceability to an **EARS ID** (from `aidlc-docs/inception/requirements/ears/`) or defect ID — do not invent a separate `REQ-XXX` scheme; EARS IDs are the canonical requirement identifier.
5. Every case must have an explicit expected result and execution priority.

## Regression Test Case Table (Mandatory)

| Test Case ID | Category | EARS ID / Defect | Scenario Title | Preconditions | Test Steps | Test Data | Expected Result | Priority | Automation | Owner | Status |
|--------------|----------|---------------------|----------------|---------------|------------|-----------|-----------------|----------|------------|-------|--------|
| REG-001 | Unit | [AUTH-LOGIN-001 / Defect-123] | [Validation rule persists after refactor] | [State/setup] | [1..N concise steps] | [Input values] | [Deterministic output/assertion] | [High/Medium/Low] | [Yes/No/Planned] | [Team/Person] | [Not Run/Pass/Fail/Blocked] |
| REG-002 | Integration | [PAY-CHECKOUT-010] | [Service interaction remains compatible] | [Services running] | [1..N concise steps] | [Payload/fixtures] | [Status + side effects] | [High/Medium/Low] | [Yes/No/Planned] | [Team/Person] | [Not Run/Pass/Fail/Blocked] |
| REG-003 | E2E | [CART-EDIT-005] | [Critical user journey remains functional] | [Environment ready] | [1..N concise steps] | [User/session data] | [Workflow completes successfully] | [High/Medium/Low] | [Yes/No/Planned] | [Team/Person] | [Not Run/Pass/Fail/Blocked] |

## Regression Execution Summary
- **Total Cases**: [X]
- **Executed**: [X]
- **Passed**: [X]
- **Failed**: [X]
- **Blocked**: [X]
- **Pass Rate**: [X]%
- **Release Readiness**: [Ready/Not Ready]
```
