# Nomia

Nomia is a Python CLI for tracking alignment between business rules and code.

It lets you declare business rules in `nomia.yaml`, link those rules to Python
functions with a decorator, capture a validated alignment snapshot, and later
check whether the repository has drifted from that snapshot.

Nomia does not prove that code is semantically correct. It makes rule-code
alignment explicit and reports when declared rules, linked implementations, or
validated mappings have changed.

## Core Workflow

Nomia has two main workflow commands:

- `nomia validate` captures or updates the validated alignment state after you
  have reviewed and accepted the current rule-code associations.
- `nomia check` checks the current repository against the validated state and
  reports alignment issues.

A typical workflow is:

```bash
nomia validate
```

Review and accept the current rule-code associations. Nomia writes the validated
state to `.nomia/state.json`.

Later, after code or rule changes:

```bash
nomia check
```

Nomia compares the current repository to the last validated state and reports
anything that needs review. If there are no issues, the default output is:

```text
Nomia check completed.
Tracked rules: 3
No alignment issues found.
```

The tracked rule count is based on the configured rule IDs discovered from the
current Nomia config.

## Quick Example

Declare rules and source packages in `nomia.yaml`:

```yaml
sources:
  - my_app

rules:
  - id: discount.eligibility
    description: Customer must be active and have no outstanding balance.
```

Link code to a rule:

```python
from nomia import rule


@rule("discount.eligibility")
def is_customer_eligible(customer):
    return customer.is_active and customer.balance == 0
```

Capture the reviewed state:

```bash
nomia validate
```

Check for changes later:

```bash
nomia check
```

If the function body changes, the rule definition changes, a configured rule has
no implementation, or a previously validated implementation is removed, `check`
reports an alignment issue.

## Commands

Nomia provides three commands:

```bash
nomia validate
nomia check
nomia audit
```

Global options:

```bash
nomia --config path/to/nomia.yaml check
nomia --verbose check
```

`--config` selects a Nomia config file. `--verbose` shows detailed discovery and
import output.

## `nomia validate`

```bash
nomia validate
```

Validates Nomia rule tracking and refreshes the local validation snapshot.

Use `validate` after you have reviewed the current rule-code associations and
want to accept them as the new baseline.

On success, Nomia prints a compact summary:

```text
Validation snapshot created. Rules tracked: 3, functions tracked: 3
```

If a declared rule has no discovered implementation, validation fails and reports
the missing implementation.

## `nomia check`

```bash
nomia check
```

Runs repository checks and reports findings.

By default, findings are informational and the command exits with code `0` when
execution succeeds. Use `--strict` to exit with code `1` when findings are found:

```bash
nomia check --strict
```

Available output formats:

```bash
nomia check --format default
nomia check --format compact
nomia check --format detailed
nomia check --format json
```

`check` can report:

- linked function code changed since the last validated snapshot
- rule content changed since the last validated snapshot
- a declared rule has no discovered implementation
- a previously validated rule was removed from the config
- a previously validated linked implementation was removed
- a discovered rule-code association has not been validated yet

## `nomia audit`

```bash
nomia audit
```

Lists discovered project functions that are not linked to a Nomia rule.

If no untracked functions are found, Nomia prints:

```text
No untracked functions found.
```

## Configuration

Nomia looks for a config file such as `nomia.yaml`.

```yaml
sources:
  - my_app

rules:
  - id: orders_above_credit_limit_must_be_blocked
  - id: high_risk_customers_require_manual_approval
    title: High-risk customers require manual approval
    severity: high
```

`sources` tells Nomia where to discover Python functions. `rules` declares the
business rule IDs that should be tracked.

## What Nomia Is Not

Nomia does not:

- infer business rules automatically
- replace tests
- require full rule coverage
- enforce a domain model
- prove that implementation behavior matches business intent

It gives you a lightweight way to notice when accepted rule-code alignment has
changed and needs review.

## License

This project is licensed under the terms of the MIT License.
