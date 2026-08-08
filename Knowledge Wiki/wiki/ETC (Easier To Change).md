# ETC (Easier To Change)

A design heuristic from The Pragmatic Programmer: good design is design that is **easier to change**. Whenever you add code, ask yourself: "Is this the easy-to-change path? Will this be easy to change later?"

## Core principle

ETC is the fundamental metric of good design. It's not about making things perfect — it's about making things adaptable. Every design decision should be evaluated by how easy it makes future changes.

## Practical application

- Get your IDE to remind you (e.g., a popup on every save: "ETC?")
- Before committing to a design, ask: "What happens when requirements change?"
- Prefer loose coupling, clear interfaces, and small focused modules
- It's not about predicting the future — it's about not painting yourself into a corner

## Related

- [[Maintenance Mindset]] — we are always in maintenance mode
- [[DRY Principle]] — DRY reduces the blast radius of changes

## Source

The Pragmatic Programmer (Hunt & Thomas)
