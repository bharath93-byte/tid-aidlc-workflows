# Generated aidlc-docs/ Reference

When you run the AI-DLC workflow, all documentation artifacts are generated inside an `aidlc-docs/` directory at your workspace root. The exact files created depend on your project type (greenfield vs brownfield), complexity, and which stages the workflow executes or skips.

Below is the fully populated structure showing every possible file across all phases and stages. Conditional files are annotated with notes indicating when they appear.

```text
aidlc-docs/
├── aidlc-state.md                                          # Workflow state tracker — project info, stage progress, current status
├── audit.md                                                # Complete audit trail — every user input, AI response, and approval with timestamps
│
├── inception/                                              # 🔵 INCEPTION PHASE — determines WHAT to build and WHY
│   ├── plans/
│   │   ├── execution-plan.md                               # Workflow visualization and phase execution decisions (always created)
│   │   ├── application-design-plan.md                      # Component/service/HLD/LLD/EARS design plan with questions (if Application Design executes)
│   │   └── unit-of-work-plan.md                            # System decomposition (Story Breakdown) plan with questions (if Units Generation executes)
│   │
│   ├── reverse-engineering/                                # Created only for brownfield projects (existing codebase detected)
│   │   ├── business-overview.md                            # Business context, transactions, and dictionary
│   │   ├── architecture.md                                 # System architecture diagrams, component descriptions, data flow
│   │   ├── code-structure.md                               # Build system, key classes/modules, design patterns, file inventory
│   │   ├── api-documentation.md                            # REST APIs, internal APIs, and data models
│   │   ├── component-inventory.md                          # Inventory of all packages by type (application, infrastructure, shared, test)
│   │   ├── technology-stack.md                             # Languages, frameworks, infrastructure, build tools, testing tools
│   │   ├── dependencies.md                                 # Internal and external dependency graphs and relationships
│   │   ├── code-quality-assessment.md                      # Test coverage, code quality indicators, technical debt, patterns
│   │   └── reverse-engineering-timestamp.md                # Analysis metadata and artifact checklist
│   │
│   ├── requirements/
│   │   ├── requirements.md                                 # Functional and non-functional requirements with intent analysis (always created)
│   │   ├── requirement-verification-questions.md           # Clarifying questions with [Answer]: tags for user input (always created)
│   │   └── ears/                                           # Created only if Application Design executes (Step 10.2, derived from each LLD)
│   │       └── {feature}-{subfeature}-ears.md              # Canonical, testable EARS requirements with semantic IDs and status markers
│   │
│   └── application-design/                                 # Created only if Application Design and/or Units Generation execute
│       ├── application-design.md                           # Consolidated design document (if Application Design executes)
│       ├── components.md                                   # Component definitions, responsibilities, and interfaces
│       ├── component-methods.md                            # Method signatures, purposes, and input/output types
│       ├── services.md                                     # Service definitions, responsibilities, and orchestration patterns
│       ├── component-dependency.md                         # Dependency matrix and communication patterns between components
│       ├── hld.md                                          # Canonical, project-level High-Level Design (if Application Design executes)
│       ├── lld/                                            # One Low-Level Design per major component (if Application Design executes)
│       │   └── {component}.md                              # Refined in place by Construction-phase stages as unit-level detail emerges
│       ├── personas.md                                     # User archetypes (only if Units Generation determines personas add value)
│       ├── unit-of-work.md                                 # Unit definitions, EARS Coverage, and user-story framing (if Units Generation executes)
│       ├── unit-of-work-dependency.md                      # Dependency matrix between units (if Units Generation executes)
│       └── unit-of-work-story-map.md                       # Mapping of stories/personas to units (if Units Generation executes)
│
├── construction/                                           # 🟢 CONSTRUCTION PHASE — determines HOW to build it
│   ├── plans/
│   │   ├── {unit-name}-functional-design-plan.md           # Business logic design plan with questions (per unit, if Functional Design executes)
│   │   ├── {unit-name}-nfr-requirements-plan.md            # NFR assessment plan with questions (per unit, if NFR Requirements executes)
│   │   ├── {unit-name}-nfr-design-plan.md                  # NFR design patterns plan with questions (per unit, if NFR Design executes)
│   │   ├── {unit-name}-infrastructure-design-plan.md       # Infrastructure mapping plan with questions (per unit, if Infrastructure Design executes)
│   │   ├── {unit-name}-code-generation-plan.md             # Standard Code Generation plan (opt-in method)
│   │   ├── {unit-name}-tdd-code-generation-plan.md         # TDD cycle plan (default Code Generation Method)
│   │   └── {unit-name}-dual-agent-tdd-plan.md              # Dual-Agent TDD Orchestrator plan (when Code Generation Method is Dual-Agent TDD)
│   │
│   ├── {unit-name}/                                        # Per-unit artifacts — one directory per unit of work
│   │   ├── functional-design/                              # Created only if Functional Design executes for this unit
│   │   │   ├── business-logic-model.md                     # Detailed business logic and algorithms
│   │   │   ├── business-rules.md                           # Business rules, validation logic, and constraints
│   │   │   ├── domain-entities.md                          # Domain models with entities and relationships
│   │   │   └── frontend-components.md                      # UI component hierarchy, props, state, interactions (if unit has frontend)
│   │   │
│   │   ├── nfr-requirements/                               # Created only if NFR Requirements executes for this unit
│   │   │   ├── nfr-requirements.md                         # Scalability, performance, availability, security requirements
│   │   │   └── tech-stack-decisions.md                     # Technology choices and rationale
│   │   │
│   │   ├── nfr-design/                                     # Created only if NFR Design executes for this unit
│   │   │   ├── nfr-design-patterns.md                      # Resilience, scalability, performance, and security patterns
│   │   │   └── logical-components.md                       # Logical infrastructure components (queues, caches, etc.)
│   │   │
│   │   ├── infrastructure-design/                          # Created only if Infrastructure Design executes for this unit
│   │   │   ├── infrastructure-design.md                    # Cloud service mappings and infrastructure components
│   │   │   └── deployment-architecture.md                  # Deployment model, networking, scaling configuration
│   │   │
│   │   ├── dual-agent/                                     # Created only if Code Generation Method is Dual-Agent TDD
│   │   │   ├── public-contract.md                          # Public operations/events/DTOs when no OpenAPI/AsyncAPI exists
│   │   │   ├── firewall-manifest.md                        # Tester allow/deny paths and write roots
│   │   │   ├── tester-packet.md                            # Spec + contract + test constraints (no production source)
│   │   │   ├── builder-packet.md                           # Requirements + tests to satisfy + production context
│   │   │   ├── tester-launch-prompt.md                     # Copy-paste prompt for a new unlinked Tester session
│   │   │   ├── builder-launch-prompt.md                    # Copy-paste prompt for a new unlinked Builder session
│   │   │   ├── red-evidence.md                             # Test run proving new tests failed before Builder
│   │   │   └── green-evidence.md                           # Test run proving the suite passed after Builder
│   │   │
│   │   └── code/                                           # Markdown summaries of generated code (always created per unit)
│   │       └── *.md                                        # Code generation summaries (actual code goes to workspace root)
│   │
│   ├── shared-infrastructure.md                            # Shared infrastructure across units (if applicable)
│   │
│   └── build-and-test/                                     # Always created after all units complete code generation
│       ├── build-instructions.md                           # Prerequisites, build steps, troubleshooting
│       ├── unit-test-instructions.md                       # Unit test execution commands and expected results
│       ├── integration-test-instructions.md                # Integration test scenarios, setup, and execution
│       ├── performance-test-instructions.md                # Load/stress test configuration and execution (if performance NFRs exist)
│       ├── contract-test-instructions.md                   # API contract validation between services (if microservices)
│       ├── security-test-instructions.md                   # Vulnerability scanning and security testing (if security NFRs exist)
│       ├── e2e-test-instructions.md                        # End-to-end user workflow testing (if applicable)
│       └── build-and-test-summary.md                       # Overall build status, test results, and readiness assessment
│
└── operations/                                             # 🟡 OPERATIONS PHASE — placeholder for future expansion
```

## Notes

- `{unit-name}` is replaced with the actual unit name (e.g., `api-service`, `frontend-app`, `data-processor`). For single-unit projects, there is typically one unit directory under `construction/`.
- For simpler single-unit projects, the model may simplify naming — for example, `construction/plans/code-generation-plan.md` instead of `construction/plans/{unit-name}-code-generation-plan.md`, or place `application-design.md` as a single consolidated file without the individual component files.
- The `build-and-test/` directory always includes `build-and-test-summary.md`. The individual instruction files (`build-instructions.md`, `unit-test-instructions.md`, `integration-test-instructions.md`, etc.) are generated based on project complexity and testing needs.
- Plans in `inception/plans/` and `construction/plans/` contain `[Answer]:` tags where users provide input, and `[ ]`/`[x]` checkboxes that track execution progress.
- Application code is never placed inside `aidlc-docs/` — it goes to the workspace root. Only markdown documentation lives here.
- The `audit.md` file is append-only and captures every interaction with ISO 8601 IST timestamps (`+05:30`) and a **User** (actor) field using the user name only (no email).
- The `aidlc-state.md` file tracks which stages have been completed, skipped, or are in progress, along with extension configuration.
