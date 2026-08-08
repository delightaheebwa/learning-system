# Java Class Body Rules

## Key Insight

Inside the main body of a Java class, you are **only allowed to declare things** (variables and methods). You are **not allowed to run action statements** (loops, prints, method calls, assignments outside declarations).

## The Golden Rule

**Declarations are allowed; actions must be inside a "box" (method, constructor, or static block).**

### Illegal (actions in open class body)

```java
class Scanner {
    int age = 5; // Allowed! (This is a declaration)

    System.out.println("Hello"); // FORBIDDEN! This is an action.
    age = 10;                     // FORBIDDEN! This is an action.
}
```

### Legal (actions inside a method box)

```java
class Scanner {
    void myMethod() {
        System.out.println("Hello"); // Allowed inside a method box!
    }
}
```

## Why This Matters

This rule is the root reason why Java needs `static {}` blocks for complex static initialization. When initializing a static `Map` or `List`, calling `.put()` or `.add()` is an **action statement** — it cannot sit in the open class body. The static block provides the required "box" for these actions.

## Related

- [[Java Static Initializer Block]]
- [[Modern Java Collection Factory Methods]]
