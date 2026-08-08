# Lexer

The **lexical analyzer** (lexer/scanner) is the first stage of a compiler or interpreter pipeline. It walks through raw source code character by character and groups characters into meaningful chunks called **tokens**.

## How It Works

Source code enters the compiler as a single massive string of characters. The lexer reads this string left-to-right, applying pattern-matching rules (typically regular expressions) to recognize lexical units: keywords, identifiers, numbers, operators, and punctuation.

When the lexer encounters a number like `42`, it does two things:
1. Keeps the raw text string (`"42"` as the lexeme)
2. Converts it into a live binary integer (`42`) stored as the literal value

## Key Insight

The compiler doesn't see `int age = 25;` — it sees a sequence of tokens:
```
KEYWORD("int") → IDENTIFIER("age") → ASSIGN_OP("=") → INTEGER("25") → SEMICOLON(";")
```

## Related
- [[Token]] — what the lexer produces
- [[Compiler]] — the broader pipeline
- [[Interpreter]] — also uses lexers for source processing
