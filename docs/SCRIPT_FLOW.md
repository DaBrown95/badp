# Script-flow inventory notes

`make script-flow` starts from the candidate slot-record script pointers found
by `make script-entries`. It reads and audits the pinned v1.5 ROM, checks the
identical command length tables, and writes only ignored local analysis. The
encoded-pointer to physical-bank mapping is an inference from the existing
fetch and bank-selection code; mapper behavior has not been verified at runtime.

The walker has explicit rules only for reviewed handlers in
[`src/us-v1.5/rom.s`](../src/us-v1.5/rom.s). Simple setters and examined helpers
fall through. Opcodes that call `ScriptSetPointerFromOperands` conditionally
produce both a target and a fallthrough candidate; opcode `$04` produces just a
target. Commands that yield produce a possible later resume, while some helpers
may either yield or return normally. These edges do not establish that a branch
is taken, a slot survives, or execution resumes. Unknown, dynamically computed
and unreviewed handlers stop their paths. The walker rejects malformed lengths,
records that cross the physical bank boundary and invalid input, and reports
physical-byte overlaps and any nodes left by its traversal limit.

On the current pinned v1.5 input the bounded walk finds 653 candidate commands
starting from the descriptor-derived entries, with 78 nodes stopping at dynamic
or unreviewed handlers and no physical-byte overlaps. Those are static candidates,
not a complete script inventory, gameplay evidence or source ownership. The
ignored JSON retains operand bytes for local examination; none are added to the
tracked source or progress count by this tool.
