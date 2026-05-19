# Nomia

**Keep your business rules and code aligned. Continuously.**

Nomia is a Python CLI tool that helps you track, validate, and maintain the relationship between **business rules** and their **implementations in code**.

Instead of letting domain knowledge drift across PRs, refactors, and quick fixes, Nomia makes that relationship **explicit, versioned, and observable over time**.

---

## Why Nomia exists

In most systems, business rules live in one of these places:

- someone's head  
- a Jira ticket from 6 months ago  
- scattered conditionals across the codebase  
- outdated documentation  

Meanwhile, modern development practices (CI/CD, linting, tests) continuously validate **technical correctness**, but not **business intent**.

Nomia focuses on that missing layer:

> Are we still implementing what the business actually meant?

---

## What Nomia does

Nomia introduces a simple workflow:

1. **Declare business rules**
2. **Link them to code**
3. **Validate the alignment**
4. **Detect changes over time**

It doesn’t try to model your domain.
It just makes the relationship between **intent** and **implementation** visible.

---

## A quick example

Define your rules:

```yaml
# nomia.yaml
rules:
  - id: discount.eligibility

sources:
  - my_app
```

Link them in your code:

```python
from nomia import rule

@rule("discount.eligibility")
def is_customer_eligible(customer):
    return customer.is_active and customer.balance == 0
```

Validate the current state:

```bash
nomia validate
```

Later, if the implementation changes:

```python
# new behavior introduced silently
return customer.is_active and (
    customer.balance == 0 or customer.has_payment_agreement
)
```

Nomia will detect the drift:

```bash
nomia check
```

Now you have a decision to make:

- the rule changed → update the config
- the code is wrong → fix the implementation

Nomia also fingerprints the declared rule content. If fields such as
`description`, `rationale`, `examples`, `severity`, `tags`, or other rule
metadata change after validation, `nomia check` reports that the rule definition
must be revalidated. This is content drift detection, not semantic proof that
the code behavior still matches the business intent.

---

## Core ideas

Nomia is built around a few simple principles:

### Business rules are explicit

Rules are declared in a config file, not hidden in code.

### Code is annotated, not inferred

Developers explicitly link implementations using a decorator.

### Alignment is versioned

Nomia stores a snapshot of rule definitions, code fingerprints, and rule–code
relationships, then compares that snapshot over time.

### Drift is visible

Implementation drift, rule definition drift, and mapping drift are detected,
even when tests still pass.

---

## Designed for real workflows

Nomia fits naturally into modern development practices:

- works with any Python project  
- integrates with CI pipelines  
- doesn’t require architectural changes  
- doesn’t enforce full coverage  

It only tracks what you decide is important.

---

## Commands

Nomia provides three main commands:

### `validate`

Creates a snapshot of current rule implementations.

```bash
nomia validate
```

Use it when:
- introducing new rules
- updating rule mappings
- accepting changes to a rule definition
- accepting changes to an implementation

---

### `check`

Compares current code with the last validated state.

```bash
nomia check
```

Use it in:
- CI pipelines
- pull requests
- pre-merge checks

`check` reports:

- implementation drift when a linked function changes
- rule definition drift when YAML rule content changes
- mapping drift when rules or linked functions are added, removed, or missing

---

### `audit`

Lists functions that are not linked to any rule.

```bash
nomia audit
```

Useful for:
- discovering missing rule mappings  
- exploring your codebase  

---

## What Nomia is not

Nomia is intentionally minimal.

It does **not**:

- enforce domain modeling  
- replace tests  
- require full rule coverage  
- infer business logic automatically  

It gives you visibility, not control.

---

## When to use it

Nomia is especially useful when:

- business rules change frequently  
- multiple developers touch the same logic  
- domain knowledge is critical (finance, billing, workflows)  
- you want to bring business awareness into code reviews  

---

## Philosophy

Nomia is based on a simple idea:

> If code evolves continuously, business rules should be tracked continuously too.

It treats **rule alignment** as a first-class concern in the development lifecycle, just like tests, linting, and security checks.

---

## Status

Nomia is currently an MVP.

It already supports:

- rule declaration via YAML
- decorator-based linking
- deterministic code discovery
- fingerprint-based implementation and rule definition change detection
- CI-friendly validation

---

## Documentation

Full documentation is coming soon.

This repository focuses on:
- the core concept  
- the CLI workflow  
- the alignment model  

---

## Summary

Nomia helps you answer a question most systems ignore:

> Does our code still reflect what the business intended?

## License

This project is licensed under the terms of the MIT License.
