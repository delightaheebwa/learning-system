# Delegation Pattern

A structural design pattern where one method hands off its work to another helper method rather than doing the work itself.

## Core idea

Instead of duplicating logic across methods, the "delegator" says: "I don't know how to do this, but I know who does." It calls the "delegate" — the method that actually performs the work.

## Example

```java
// Delegator — does NOT do the work itself
private void addToken(TokenType type) {
    addToken(type, null);  // delegates to the longer version
}

// Delegate — the one that actually does the work
private void addToken(TokenType type, Object literal) {
    // actual token creation logic here
    tokens.add(new Token(type, lexeme, literal, line));
}
```

The short `addToken` doesn't know how to create tokens. It delegates that responsibility to the longer version.

## Relationship to method overloading

Method overloading is the *language feature* that enables this pattern. The Delegation Pattern is the *architectural intent* — the design decision to separate concerns and hand off work.

## Also known as

- **Method Chaining** (casual)
- **Telescoping Methods** — when multiple overloaded methods stack like a collapsible telescope, each filling defaults and calling the next longer version

## Related

- [[Single Responsibility Principle (SRP)]] — delegation is how SRP is often implemented; each method keeps one job
- [[Convenience Method]] — the short delegator is usually a convenience method
- [[Strategy Pattern]] — a different kind of delegation (delegating to interchangeable algorithm objects rather than overloaded methods)
