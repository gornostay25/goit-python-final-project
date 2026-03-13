---
name: better-comments
description: Write and review code comments following Python best practices. Use when adding comments to code, reviewing code quality, or when the user asks about comments, documentation, or code readability.
---

# Better Comments

## Quick Start

**For writing new comments:**
1. Explain **why**, not **what** - code shows what, comments explain why
2. Focus on business logic, algorithms, and non-obvious decisions
3. Use docstrings for functions, classes, and modules
4. Keep comments concise and current

**For reviewing comments:**
1. Check if comments add value beyond the code
2. Verify comments match current code behavior
3. Look for outdated or redundant comments
4. Ensure docstrings follow Google/Numpy style

## When to Comment

**Comment:**
- Business logic requirements and rules
- Complex algorithms or mathematical formulas
- Non-obvious design decisions or trade-offs
- Workarounds and temporary solutions with TODOs
- Context that code alone cannot provide

**Don't comment:**
- Obvious code (e.g., `i += 1` # increment i)
- Code that can be made self-documenting (use better variable names)
- Duplicate information already in code
- Commented-out code (delete it, version control remembers)
- **Inline comments explaining code logic** (preserve these as they clarify non-obvious implementation details)

## Python Comment Styles

### Inline Comments
Use sparingly, only for non-obvious logic:

```python
# Calculate Euclidean distance between points
distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
```

### Block Comments
Use for sections of complex code:

```python
# Handle edge case where user has no permissions:
# 1. Check if user is admin (admin always has access)
# 2. If not admin, check specific resource permissions
# 3. Deny access if no permissions found
```

### Docstrings
Use for modules, classes, and functions. Follow Google style:

```python
def process_payment(user_id: int, amount: float) -> bool:
    """Process a payment for the specified user.

    Args:
        user_id: The ID of the user making the payment.
        amount: The payment amount in USD.

    Returns:
        True if payment succeeded, False otherwise.

    Raises:
        ValueError: If amount is negative.
        InsufficientFundsError: If user lacks sufficient balance.
    """
```

## Comment Anti-Patterns

**Avoid these:**
- ❌ "I'm fixing X" - explain the fix, not that you're fixing it
- ❌ Code that tells what: `x = x + 1` # increment x
- ❌ Obsolete comments - update or remove when code changes
- ❌ Commented-out code - use git history instead
- ❌ Ambiguous pronouns: "it", "they", "this" - be specific
- ❌ Emotional comments: "This is a hack", "Ugly but works"

**Good examples:**
```python
# Use round() instead of int() to handle floating-point errors
price = round(total * tax_rate, 2)

# Temporarily disable validation during migration
# TODO: Remove after Q3 2026 release (ticket #1234)
if MIGRATION_MODE:
    validate = False
```

## Review Checklist

For writing comments:
- [ ] Explains why, not what
- [ ] Adds value beyond readable code
- [ ] Concise and clear
- [ ] Uses appropriate style (inline, block, docstring)
- [ ] No obvious redundancies

For reviewing comments:
- [ ] Comments are accurate and current
- [ ] No outdated information
- [ ] No commented-out code
- [ ] Docstrings follow chosen style guide
- [ ] Comments handle edge cases and gotchas
