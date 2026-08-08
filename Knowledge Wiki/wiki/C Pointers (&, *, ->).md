# C Pointers (&, *, ->)

## Overview

`*` and `&` are **pointer operators** — they control how you read, write, and reference memory addresses directly. Think of RAM as a giant row of post-office boxes: a regular variable holds the *contents inside* a box; a memory address tells you *which box number* a variable lives at.

## The Address-of Operator (&)

"Where does this variable live?" — placing `&` before an existing variable yields its **memory address** (box number), not its value:

```c
int age = 25;
printf("%d\n", age);   // 25       (the value inside)
printf("%p\n", &age);  // 0x7ffd… (the memory address of age)
```

Why the lesson used it: calling `parse_meminfo(input, &memory)` passes the *address* of the caller's `struct memory`, letting the function modify that struct directly.

## The Pointer / Dereference Operator (*)

The `*` symbol wears **two hats** depending on placement:

**Hat A — type declaration (creating a pointer):** in a declaration, `*` says "this variable doesn't hold data directly; it holds a memory address."

```c
int *ptr = &age;  // ptr stores the memory address of age
```

**Hat B — dereferencing (opening the box):** before an existing pointer in executable code, `*` means "go to the address stored inside this pointer and read/write the value inside."

```c
int age = 25;
int *ptr = &age;
*ptr = 30;              // follow ptr to age's location, write 30 there
printf("%d\n", age);    // 30
```

## The Arrow (->)

For pointers to structs, `->` is shortcut syntax for dereference-then-field: `out->total_kb` is shorthand for `(*out).total_kb`. It follows the address to modify the original struct back in the caller:

```c
int parse_meminfo(const char *text, struct memory *out)
{
    // ...
    out->total_kb = value;   // ≡ (*out).total_kb = value;
}
```

## Key Insight

- C passes function arguments **by value**. A plain `struct memory memory` argument would be copied, and mutations would vanish when the function returns. Passing the address (`&memory`) is how C simulates pass-by-reference.
- `*p = 20` writes *through* the pointer — the pointed-to variable changes (x becomes 20), not the pointer itself.

## Self-Check

```c
int x = 10;
int *p = &x;
*p = 20;
```

`x` holds **20**: `p` holds x's address, and dereferencing (`*p`) reaches that memory location and overwrites its value.

## Sources

- Gemini Socratic tutoring on C pointers (notebook: https://gemini.google.com/app/8870dcd71e2919f5)

Related: [[Testable Seam]], [[Sentinel Values vs Presence Flags]]
