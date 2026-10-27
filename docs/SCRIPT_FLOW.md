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
is taken, a slot survives, or execution resumes. A nonzero-mode `$63` record
load preserves the script pointer; zero mode remains dynamic. The `$1E` slot
action yields, with mode 2 retaining the slot and other modes releasing it;
later reuse has an unknown entry. Opcode `$95` scans four-byte target/value
cases and a two-byte zero-target terminator; the walker records candidate matches
and the no-match continuation, stopping on bank boundaries or its record limit.
The handler still fetches four bytes for the terminator. Opcodes `$AB` and `$BF`
may retry when shared state is busy, or continue when it is available. Opcode
`$B1` consumes a similarly terminated value-remapping table without branching
to its values. Indirect writes continue only for the reviewed text-pointer bytes
`$55/$56`; native calls continue only for the reviewed decoder and palette fade.
The `$98` and `$99` main-state changes stop the walk because later scheduling is unproven.
Unknown, dynamically computed
and unreviewed handlers stop their paths. The walker rejects malformed lengths,
records that cross the physical bank boundary and invalid input, and reports
physical-byte overlaps and any nodes left by its traversal limit.

On the current pinned v1.5 input the bounded walk finds 1,808 candidate commands
starting from the descriptor-derived entries, with 48 nodes stopping at dynamic
or unreviewed handlers and no physical-byte overlaps. Those are static candidates,
not a complete script inventory, gameplay evidence or source ownership. The
ignored JSON retains operand bytes for local examination; none are added to the
tracked source or progress count by this tool.
