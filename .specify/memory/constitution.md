# Constitution

## Core Principles

### I. Pythonic Correctness and Readability

All code MUST follow modern, idiomatic Python practices.

The project MUST prioritize readability, explicitness, maintainability, and correctness. Code is read more often than it is written; therefore, clarity is a functional requirement, not a style preference.

The project MUST follow:

- PEP 8 for style and readability.
- PEP 257 for docstring conventions.
- PEP 484-compatible type annotations for public interfaces.
- PEP 621 for project metadata in `pyproject.toml`.
- PEP 440 for versioning.
- The Zen of Python as a general design reference.

Python 3.12+ SHOULD be used unless a runtime constraint requires otherwise.

Public functions, classes, modules, and packages MUST expose clear contracts through names, type hints, docstrings, and tests.

Code that is clever but difficult to understand MUST be rejected unless the complexity is necessary and documented.

### II. Clean Architecture Boundaries

The system MUST follow Clean Architecture principles.

Business rules MUST be independent from frameworks, databases, APIs, queues, storage engines, CLIs, and external services.

The project MUST be organized around explicit architectural layers:

- Domain Layer
- Application Layer
- Interface Layer
- Infrastructure Layer

Dependencies MUST point inward.

The Domain Layer MUST NOT import from application, interface, infrastructure, frameworks, ORMs, API libraries, database clients, or external service SDKs.

The Application Layer MAY define ports, use cases, commands, queries, DTOs, and transaction boundaries, but MUST NOT depend on concrete infrastructure implementations.

The Infrastructure Layer MUST implement application ports and contain framework-specific, database-specific, and external-service-specific code.

The Interface Layer MUST adapt external input and output to application use cases.

Architecture violations MUST be treated as defects.

### III. Object-Oriented Design and SOLID

Object-oriented code MUST be designed around behavior, invariants, and explicit responsibilities.

Classes MUST have a clear reason to exist. A class that only groups unrelated functions or data without behavior SHOULD be replaced with a module, dataclass, value object, DTO, or function.

The project MUST apply SOLID principles pragmatically:

- Single Responsibility Principle: each module, class, and function MUST have one primary reason to change.
- Open/Closed Principle: behavior SHOULD be extended through composition, protocols, strategies, or adapters instead of modifying stable code.
- Liskov Substitution Principle: subclasses or implementations MUST preserve the contract of the abstraction they implement.
- Interface Segregation Principle: clients MUST NOT depend on methods they do not use.
- Dependency Inversion Principle: high-level policy MUST depend on abstractions, not low-level implementation details.

Composition SHOULD be preferred over inheritance.

Inheritance is allowed only when the relationship is truly substitutable and the base class represents a stable abstraction.

Duck typing, protocols, abstract base classes, and dependency injection SHOULD be used to express replaceable behavior.

### IV. Testable Design and Quality Gates

Testing MUST be part of the design process.

New behavior MUST include tests before the work is considered complete.

The project MUST include:

- Unit tests for domain and application logic.
- Contract tests for ports, repositories, interfaces, and adapters.
- Integration tests for database, file system, queue, API, and external-service boundaries.
- End-to-end tests for critical user flows.
- Regression tests for every bug fix.

Tests MUST be deterministic, isolated, readable, and meaningful.

A test that only verifies implementation details instead of observable behavior SHOULD be rewritten.

Code without relevant tests MUST NOT be merged unless an explicit exception is documented.

### V. Simplicity, Observability, and Operational Reliability

The system MUST remain simple until real requirements justify additional complexity.

The project MUST avoid premature abstractions, unnecessary inheritance, excessive indirection, hidden global state, and framework-driven domain logic.

Every production-relevant operation MUST be observable through structured logs, metrics, traces, or clear error reporting.

External calls MUST have explicit timeout, retry, and failure-handling policies.

Errors MUST NOT pass silently. Exceptions MUST be handled intentionally, logged with useful context, or propagated through clear application-level errors.

## Python Language Standards

The project MUST use a standards-based Python toolchain.

Required baseline:

```text
pyproject.toml
src/ layout
type annotations
automated formatting
automated linting
automated tests
static type checking
pre-commit hooks
dependency vulnerability checks
```

````

Recommended tools:

```text
ruff
mypy or pyright
pytest
coverage.py
pre-commit
uv or poetry
pip-audit or equivalent
```

The project MUST use `pyproject.toml` as the central configuration file for packaging and tooling whenever possible.

Python code MUST follow these rules:

- Prefer simple functions over unnecessary classes.
- Prefer explicit names over abbreviations.
- Prefer immutable data structures when mutation is not required.
- Prefer `pathlib.Path` over raw string path manipulation.
- Prefer context managers for resource lifecycle management.
- Prefer standard-library solutions before adding dependencies.
- Prefer dataclasses for simple structured data.
- Prefer protocols for structural abstractions.
- Prefer enums for constrained symbolic values.
- Prefer typed exceptions for domain/application failures.
- Avoid mutable default arguments.
- Avoid broad `except Exception` blocks unless re-raising or translating the error intentionally.
- Avoid hidden I/O in constructors.
- Avoid import-time side effects.
- Avoid global mutable state.
- Avoid boolean flags that create multiple behaviors inside one function.

Public APIs MUST be stable, typed, documented, and tested.

## Architecture and Project Structure

The project SHOULD follow this structure unless an approved architectural decision record defines another layout:

```text
src/
  [project_name]/
    domain/
      entities/
      value_objects/
      services/
      events/
      exceptions.py

    application/
      use_cases/
      ports/
      dto/
      commands/
      queries/
      services/
      unit_of_work.py

    interface/
      api/
      cli/
      schemas/
      controllers/
      presenters/

    infrastructure/
      database/
      repositories/
      sqlalchemy/
      external_services/
      messaging/
      files/
      config/

    observability/
      logging.py
      metrics.py
      tracing.py

    shared/

tests/
  unit/
  integration/
  contract/
  e2e/

docs/
  adr/
  architecture/
  runbooks/

scripts/
```

Layer responsibilities:

### Domain Layer

The Domain Layer MUST contain enterprise rules and core business concepts.

Allowed:

- Entities
- Value objects
- Domain services
- Domain events
- Domain exceptions
- Business invariants
- Pure business policies

Forbidden:

- SQLAlchemy models
- API schemas
- HTTP clients
- CLI parsers
- Framework decorators
- Environment variable access
- Database sessions
- Serialization concerns
- Infrastructure-specific code

### Application Layer

The Application Layer MUST orchestrate use cases.

Allowed:

- Commands
- Queries
- Use cases
- DTOs
- Ports
- Application services
- Transaction boundaries
- Authorization checks
- Application exceptions

Forbidden:

- Direct database queries
- Framework request/response objects
- Concrete infrastructure implementations
- Vendor-specific SDK calls

### Interface Layer

The Interface Layer MUST translate external input into application calls and application output into external responses.

Allowed:

- API controllers
- CLI commands
- Request schemas
- Response schemas
- Presenters
- Input validation
- Serialization
- HTTP status mapping

Forbidden:

- Business rules
- Direct persistence logic
- Transaction orchestration beyond calling application use cases

### Infrastructure Layer

The Infrastructure Layer MUST contain replaceable technical details.

Allowed:

- SQLAlchemy models
- Repository implementations
- Unit of Work implementations
- External API clients
- Queue clients
- File storage
- Configuration loading
- Framework-specific adapters

Infrastructure code MUST implement contracts defined by the application layer.

## Object-Oriented Programming Rules

Classes MUST model cohesive concepts.

A class SHOULD be created when at least one of these is true:

- It protects invariants.
- It groups state and behavior that change together.
- It implements a stable abstraction.
- It represents a meaningful domain concept.
- It coordinates a technical boundary behind an interface.
- It improves testability through dependency injection.

A class SHOULD NOT be created only to hold one stateless method. Prefer a function instead.

Constructors MUST leave objects in a valid state.

Constructors MUST NOT perform network calls, database queries, file reads, or expensive operations. Use factories or application services for those operations.

Methods MUST preserve object invariants.

Domain objects MUST not expose internal mutable state directly.

Equality, hashing, ordering, and string representation MUST be intentional.

Use `@dataclass(frozen=True)` for immutable value objects when appropriate.

Use regular classes for entities with identity and lifecycle.

Use `Protocol` when behavior matters more than inheritance.

Use `ABC` when a nominal abstraction is required.

Example application port:

```python
from typing import Protocol

from project.domain.entities.payment import Payment
from project.domain.value_objects.payment_id import PaymentId


class PaymentRepository(Protocol):
    def get_by_id(self, payment_id: PaymentId) -> Payment | None:
        ...

    def save(self, payment: Payment) -> None:
        ...
```

## SOLID Design Rules

### Single Responsibility Principle

Each unit MUST have one primary responsibility.

A module, class, or function that mixes business logic, persistence, formatting, validation, logging, and transport concerns MUST be refactored.

### Open/Closed Principle

Stable behavior SHOULD be extended through abstractions.

Use strategies, adapters, factories, dependency injection, or configuration-driven composition instead of editing central conditional blocks repeatedly.

### Liskov Substitution Principle

Implementations MUST honor the contracts they claim to implement.

A subclass or adapter MUST NOT surprise callers with weaker guarantees, incompatible return types, hidden side effects, or different exception semantics.

### Interface Segregation Principle

Interfaces MUST be small and role-specific.

A client MUST NOT be forced to depend on methods it does not use.

Large service interfaces MUST be split into focused ports.

### Dependency Inversion Principle

High-level policy MUST not depend on low-level details.

Use cases MUST depend on repository, gateway, service, clock, ID generator, transaction, and notification abstractions instead of concrete implementations.

## Design Patterns

Design patterns MUST be used intentionally.

Patterns are allowed when they improve clarity, testability, replaceability, or consistency.

Recommended patterns:

### Creational Patterns

- Factory Method for creating objects behind abstractions.
- Abstract Factory for families of related implementations.
- Builder for complex object construction.
- Prototype only when copying complex configured objects is safer than rebuilding them.

### Structural Patterns

- Adapter for external services, frameworks, databases, and incompatible APIs.
- Facade for simplifying complex subsystems.
- Proxy for access control, lazy loading, caching, or remote communication.
- Composite for tree-like domain structures.
- Decorator for adding behavior without modifying the original object.

### Behavioral Patterns

- Strategy for interchangeable algorithms or business policies.
- Command for explicit application actions.
- Observer for event publishing and subscriptions.
- State for lifecycle-dependent behavior.
- Template Method only when inheritance is clearly justified.
- Chain of Responsibility only when ordered handler pipelines are truly needed.
- Specification for reusable business predicates.

Project-specific default patterns:

- Repository for persistence boundaries.
- Unit of Work for transaction management.
- DTO for data transfer across boundaries.
- Mapper for conversion between domain and persistence/interface models.
- Domain Event for meaningful business occurrences.
- Application Service / Use Case for orchestration.
- Value Object for immutable domain values.

Discouraged patterns:

- Singleton as a dependency-management mechanism.
- God Object.
- Service Locator.
- Active Record for complex domains.
- Anemic domain model when business rules are non-trivial.
- Inheritance-heavy hierarchies.
- Overuse of factories for simple constructors.
- Generic `Manager`, `Helper`, or `Util` classes without clear responsibility.

Every non-obvious pattern MUST be documented in code comments, architecture docs, or ADRs.

## Design System for Code Consistency

The project MUST maintain a consistent internal design language.

Naming conventions:

- Use cases MUST be named by intent: `CreatePayment`, `ApproveInvoice`, `GenerateReport`.
- Commands MUST represent state-changing intent: `CreateUserCommand`.
- Queries MUST represent read-only intent: `GetUserByIdQuery`.
- Ports MUST describe required capability: `PaymentRepository`, `EmailSender`, `Clock`.
- Adapters MUST describe concrete implementation: `SqlAlchemyPaymentRepository`, `SmtpEmailSender`.
- DTOs MUST be explicit: `PaymentSummaryDTO`.
- Exceptions MUST describe failure meaning: `PaymentNotFoundError`, `InvalidPaymentStateError`.

Module conventions:

- Domain modules MUST use business language.
- Application modules MUST use use-case language.
- Infrastructure modules MUST use technology language.
- Interface modules MUST use transport language.

Boundary conventions:

- Domain models MUST NOT be reused as API request/response schemas.
- ORM models MUST NOT be reused as domain entities unless the project is intentionally CRUD-oriented and this exception is documented.
- DTOs MUST NOT contain behavior beyond validation or simple transformation.
- Mappers MUST be explicit when crossing architectural boundaries.

Consistency matters more than personal preference. Existing project conventions SHOULD be followed unless they violate this constitution.

## SQLAlchemy Rules

SQLAlchemy MUST be isolated inside the infrastructure layer.

The application layer MUST interact with persistence through repository ports and Unit of Work abstractions.

Use cases MUST NOT directly manipulate:

- SQLAlchemy sessions
- Engines
- Connections
- ORM models
- Raw SQL
- Database-specific query objects

Mandatory SQLAlchemy practices:

- Use SQLAlchemy 2.x style APIs.
- Use explicit session lifecycle management.
- Treat the session as a Unit of Work boundary.
- Use context managers for transaction scopes.
- Commit and rollback behavior MUST be explicit.
- Avoid leaking ORM models outside infrastructure.
- Avoid implicit lazy-loading across application boundaries.
- Prevent N+1 queries with explicit loading strategies.
- Use migrations for schema changes.
- Validate indexes against query patterns.
- Use raw SQL only when justified by performance, reporting, database-specific features, or migration needs.
- Test repositories with real database behavior where practical.

Repository methods MUST express business intent, not database mechanics.

Good:

```python
class PaymentRepository(Protocol):
    def get_pending_payments(self, limit: int) -> list[Payment]:
        ...

    def save(self, payment: Payment) -> None:
        ...
```

Avoid:

```python
class PaymentRepository(Protocol):
    def execute_query(self, sql: str) -> object:
        ...
```

Transactions MUST be coordinated by a Unit of Work or application-level transaction boundary.

Example:

```python
class UnitOfWork(Protocol):
    payments: PaymentRepository

    def __enter__(self) -> "UnitOfWork":
        ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
```

## Error Handling

Errors MUST be explicit, meaningful, and recoverable where possible.

The project MUST define error categories:

- Domain errors
- Application errors
- Infrastructure errors
- Validation errors
- Authorization errors
- Configuration errors

Domain errors MUST describe business rule violations.

Application errors MUST describe use-case failures.

Infrastructure errors SHOULD be translated before crossing into the application layer.

Do not expose raw database, framework, or provider exceptions through public application interfaces.

Rules:

- Do not swallow exceptions silently.
- Do not use exceptions for normal control flow when a result type is clearer.
- Do not raise generic `Exception`.
- Do not return `None` for error cases unless absence is a valid domain result.
- Include enough context for debugging without leaking sensitive data.
- Preserve original exception context with exception chaining when translating errors.

## Configuration and Security

Configuration MUST be explicit, validated, and environment-aware.

Rules:

- Secrets MUST never be committed.
- Secrets MUST come from environment variables, secret managers, or secure runtime configuration.
- Required configuration MUST be validated at startup.
- Defaults MUST be safe for local development.
- Production configuration MUST be explicit.
- Logs MUST redact secrets, tokens, credentials, and sensitive data.
- External input MUST be validated at boundaries.
- File paths, SQL inputs, request payloads, and configuration values MUST be treated as untrusted.
- Dependency vulnerabilities MUST be checked in CI.

Configuration objects SHOULD be typed and immutable after startup.

## Observability

Production behavior MUST be observable.

The project MUST use structured logging for meaningful events.

Logs SHOULD include:

- Correlation ID
- Request ID
- Use case name
- Operation name
- Duration
- Outcome
- Error category
- Relevant non-sensitive identifiers

Logs MUST NOT include:

- Passwords
- Tokens
- Secrets
- Full personal data
- Raw credentials
- Sensitive payloads

Metrics SHOULD be added for:

- Request count
- Error count
- Latency
- Database query duration
- External service duration
- Queue processing time
- Retry count
- Transaction failures

Tracing SHOULD be used for workflows that cross process, network, or persistence boundaries.

## Performance and Reliability

Performance requirements MUST be measurable.

The project SHOULD define expectations for:

- API latency
- Database query time
- Batch throughput
- Memory usage
- Startup time
- External service timeout
- Queue processing time

Reliability rules:

- External calls MUST define timeouts.
- Retries MUST be bounded.
- Retries MUST use backoff when appropriate.
- Non-idempotent operations MUST be protected against accidental duplication.
- Database writes MUST be transactionally safe.
- Background jobs MUST be recoverable.
- Partial failures MUST be handled explicitly.
- Resource cleanup MUST be deterministic.
- Long-running operations MUST expose progress, state, or traceability.

## Testing Standards

The project MUST use `pytest` unless another test framework is explicitly approved.

Test categories:

```text
tests/unit/
tests/integration/
tests/contract/
tests/e2e/
```

Unit tests:

- MUST be fast.
- MUST not require network, filesystem, or database unless explicitly scoped.
- MUST focus on domain and application behavior.

Integration tests:

- MUST validate real infrastructure behavior.
- SHOULD use disposable databases, containers, or isolated test resources.
- MUST verify transaction behavior when persistence is involved.

Contract tests:

- MUST verify that infrastructure adapters satisfy application ports.
- MUST be updated when ports change.

End-to-end tests:

- MUST cover critical user-facing flows.
- SHOULD remain minimal and high-value.

Bug fixes MUST include regression tests.

Tests MUST be named by behavior, not implementation.

Good:

```python
def test_rejects_payment_when_amount_is_negative() -> None:
    ...
```

Avoid:

```python
def test_payment_method_1() -> None:
    ...
```

## Documentation and ADRs

Documentation MUST evolve with the code.

The project MUST maintain:

- `README.md`
- Local development guide
- Architecture overview
- Testing guide
- Deployment guide when applicable
- Runbooks for operational workflows
- ADRs for significant decisions

ADRs MUST include:

```text
Title
Status
Context
Decision
Alternatives considered
Consequences
Migration plan when applicable
Date
```

Significant decisions MUST NOT live only in chat history, commit messages, or issue comments.

## Commit, Branching, and Review Standards

Commits MUST be atomic, meaningful, and reviewable.

A commit is atomic when it contains one coherent change that can be understood, tested, reverted, or cherry-picked independently.

Rules:

- One logical change per commit.
- Commit messages MUST describe intent.
- Formatting-only changes SHOULD be separate from behavior changes.
- Refactors SHOULD be separate from feature changes when practical.
- Tests SHOULD be committed with the behavior they verify.
- Broken commits MUST NOT be pushed to shared branches unless explicitly marked as work-in-progress.
- Generated files MUST be committed only when required.

Recommended commit format:

```text
<type>(<scope>): <summary>

<body>

<footer>
```

Allowed types:

```text
feat
fix
refactor
test
docs
chore
perf
build
ci
revert
```

Examples:

```text
feat(payments): add payment approval use case
```

```text
refactor(database): isolate SQLAlchemy models from domain entities
```

```text
test(users): add contract tests for user repository
```

Pull requests MUST include:

- Problem statement
- Summary of changes
- Tests added or updated
- Architecture impact
- Database impact, if any
- Migration impact, if any
- Security impact, if any
- Observability impact, if any
- Known limitations
- Follow-up work

## Quality Gates

A change MUST NOT be considered complete until all relevant gates pass.

Required gates:

- Formatting passes.
- Linting passes.
- Static typing passes.
- Unit tests pass.
- Integration tests pass when affected.
- Contract tests pass when interfaces change.
- End-to-end tests pass when critical flows change.
- Documentation is updated.
- ADR is added or updated for significant architectural decisions.
- No secrets are detected.
- Dependency checks pass.
- Coverage does not decrease without justification.
- Architecture boundaries are preserved.
- Public interfaces remain backward compatible or breaking changes are documented.

## Spec Kit Workflow

This project MUST use the Spec Kit workflow as the primary development path.

Required flow:

### `/speckit.constitution`

Define or update project principles, architectural boundaries, engineering rules, and governance.

The constitution MUST be reviewed before generating specifications, plans, tasks, or implementation.

### `/speckit.specify`

Define functional requirements.

The specification MUST include:

- Problem statement
- Goals
- Non-goals
- Users
- Use cases
- Inputs
- Outputs
- Business rules
- Acceptance criteria
- Constraints
- Success metrics

The specification MUST avoid implementation details unless they are hard constraints.

### `/speckit.plan`

Define the technical plan.

The plan MUST include:

- Architecture
- Affected layers
- Data model
- Ports and adapters
- Main classes/functions
- Error handling
- Transaction boundaries
- Testing strategy
- Migration strategy when applicable
- Risks and trade-offs

The plan MUST verify compliance with this constitution.

### `/speckit.tasks`

Break the plan into atomic, reviewable tasks.

Each task MUST include:

- Goal
- Affected files or modules
- Expected tests
- Acceptance criteria
- Dependencies
- Quality gates

Tasks SHOULD be independently testable where practical.

### `/speckit.implement`

Implement only approved tasks.

Implementation MUST:

- Preserve architecture boundaries.
- Keep commits atomic.
- Add or update tests.
- Update documentation.
- Avoid unrelated changes.
- Record significant decisions in ADRs.
- Pass all relevant quality gates.

## Governance

This constitution supersedes informal practices, local preferences, and ad hoc implementation decisions.

All specifications, plans, tasks, implementations, reviews, and generated code MUST comply with this constitution.

Amendments require:

1. Written proposal.
2. Rationale.
3. Impact analysis.
4. Migration plan for affected code.
5. Approval by the project owner or maintainers.
6. Version update.

Compliance review is mandatory for:

- New features
- Architecture changes
- Database changes
- Public interface changes
- Security-sensitive changes
- Production deployment changes
- Dependency changes with runtime impact
- Performance-sensitive changes

Any violation MUST be handled in one of three ways:

- Fix before merge.
- Document as a temporary exception with owner and expiration date.
- Amend the constitution if the rule is no longer valid.

Complexity MUST be justified.

Simple, explicit, well-tested code is preferred over abstract, generic, or overly clever code.

When this constitution conflicts with generated plans, generated tasks, implementation shortcuts, or local preferences, this constitution wins.

**Version**: 1.0.0 | **Ratified**: 2026-06-25 | **Last Amended**: 2026-06-25
````
