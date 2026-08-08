# Interdeveloper Duplication

A form of DRY violation where different programmers on the same team unknowingly write the same code. Unlike representational duplication (external interfaces), this is about **internal** redundancy across team members.

## The problem

Code doesn't clearly belong to one person or department, so multiple developers independently solve the same problem. A government audit once found 10,000 different programs that all contained unique versions of code to validate a Social Security Number.

## Solutions

- **Talk constantly**: Short daily stand-ups, team chat (Slack/Discord), and open discussion about what you're building.
- **Assign a librarian**: One person responsible for tracking common utilities and helping teams share knowledge. They curate the shared codebase.
- **Centralize utilities**: A single, shared folder in the codebase for common scripts and helpers. Make it easy to discover.
- **Read each other's code**: Code reviews aren't just for quality — they're for awareness. Know what your teammates are building so you don't rebuild it.

## Root cause

Interdeveloper duplication happens because of **communication gaps**, not technical failures. The fix is organizational and cultural, not tool-based (though tools help).

## Related

- [[DRY Principle]] — interdeveloper duplication is a DRY violation at the team level
- [[Communication for Developers]] — the antidote is better communication

## Source

The Pragmatic Programmer (Hunt & Thomas)
