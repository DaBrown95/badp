# Script-flow inventory notes

`make script-flow` starts from the candidate slot-record script pointers found
by `make script-entries`. It reads and audits the pinned v1.5 ROM, checks the
identical command length tables, and writes only ignored local analysis. The
encoded-pointer to physical-bank mapping follows the existing fetch and bank
selection code. Separate MesenCE opening runs observed the mapping after the
switch for all sampled command fetches; that is emulator evidence for those
paths, not verification of a physical cartridge.

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
`$19` similarly may retry after checking the current slot. Opcode
`$B1` consumes a similarly terminated value-remapping table without branching
to its values. Indirect writes continue only for the reviewed text-pointer bytes
`$55/$56`; native calls continue only for the reviewed decoder and palette fade.
Three `$44` indexed jumps have explicit candidate bounds of 11, 4 and 8
entries, derived from their immediately preceding clamp/divide or mask paths.
The walker follows those entries and marks their table bytes; other callers and
their index ranges remain unverified, and unbounded `$44` sites still stop.
The `$8A` stack-buffer operation has a possible normal-return successor. Its
`$FF` form clears `$0100-$011F`; a sufficiently deep stack could put a return
address in that range, so the walk does not model every possible outcome.
The `$79`, `$84`, `$8D/$8E`, `$A4`, `$BC` and `$BD` handlers also have normal
return successors; that does not prove their execution or termination.
The `$0F`, `$98` and `$99` main-state changes stop the walk because later
scheduling is unproven. In particular, treating the bytes after `$0F` as an
automatic continuation produced a speculative command decode over a
descriptor-linked record; the separately evidenced record is now data.
Unknown, dynamically computed
and unreviewed handlers stop their paths. The walker rejects malformed lengths,
records that cross the physical bank boundary and invalid input, and reports
physical-byte overlaps and any nodes left by its traversal limit.

On the current pinned v1.5 input the bounded walk finds 1,936 candidate commands
starting from the descriptor-derived entries, with 38 nodes stopping at dynamic
or unreviewed handlers and no physical-byte overlaps. Those are static candidates,
not a complete script inventory, gameplay evidence or source ownership. The
ignored JSON retains operand bytes for local examination; none are added to the
tracked source or progress count by this tool.

Separate execution probes sampled the command pointer and alternate-bank value
at the bank-0 fetcher, then inspected Mesen's mapped address after switching.
They confirmed 10,404 Noah, 10,822 Moses and 11,102 David fetches in PRG bank 1
with no mapping disagreement. Of the previously unowned observed commands,
194 in 18 contiguous, nonconflicting groups are now represented with named
command forms. Other paths and any conflicting interpretations remain local.
The captured command identities, mapping checks and probe scripts are kept in
ignored `analysis/us-v1.5/`; these opening sequences do not cover the full game.

A separate local walk from the 808 distinct observed command pointers found
1,444 possible nodes and no overlapping decodes within that walk. The reviewed
nonconflicting portions now include 249 additional candidate commands and
three `$95` lookup tables in source. The inputs and output of this second walk
remain in ignored local analysis. A successor of an observed command is still
only a static candidate until that path is exercised.

The longer 8,000-frame exploration provided 1,322 distinct command entries; a
separate walk found 2,016 nodes without internal overlapping decodes. A further
109 commands and the terminated `$95` table at `$D629` are represented as
source after checks against existing ownership and candidate records. The
three entries at `$F435` were each selected by the indexed-jump handler in
MesenCE. Their presence does not bound the handler's index.
