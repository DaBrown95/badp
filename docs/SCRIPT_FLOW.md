# Script-flow inventory notes

These notes record observations and candidate analyses from reconstruction.
Counts refer to the checkpoints described here. Use the [README](../README.md)
and `config/inventory-review-*.json` for the current acceptance decisions.

`make script-flow` starts from the candidate slot-record script pointers found
by `make script-entries`. It audits the pinned v1.5 ROM, checks that the
command length tables are identical, and writes its analysis to ignored local
files. It maps encoded pointers to physical banks using the existing fetch and
bank selection code. Separate MesenCE opening runs observed that mapping after
the switch for every sampled command fetch. Those observations support the
mapping on the tested emulator paths. They do not verify a physical cartridge.

## Walker rules

The walker follows explicit rules only for reviewed handlers in
[`src/us-v1.5/rom.s`](../src/us-v1.5/rom.s). Simple setters and examined
helpers fall through. Opcodes that call `ScriptSetPointerFromOperands`
conditionally produce both a target and a fallthrough candidate. Opcode `$04`
produces only a target. Commands that yield produce a possible later resume,
while some helpers may either yield or return normally. Opcode `$67` yields
after updating a slot. Opcode `$89` has a possible resume through its
relative-position path; its other path can change the main state, so its
scheduling is not assumed. Opcode `$18` stops and restarts voice 4 and can
return to the next command; `$9D` is an empty handler and also falls through.
The graph keeps competing decodes. Its edges do not prove that an entry
executes, a branch is taken, a slot survives or execution resumes. A
nonzero-mode `$63` record load preserves the script pointer; zero mode remains
dynamic. The `$1E` slot action yields. Mode 2 retains the slot, and other
modes release it. The entry used by later slot reuse remains unknown.

Opcode `$95` scans four-byte target/value cases and a two-byte zero-target
terminator. The walker records candidate matches and the no-match
continuation. It stops at bank boundaries or its record limit. The handler
still fetches four bytes for the terminator. Opcodes `$AB` and `$BF` may retry
when shared state is busy, or continue when it is available. Opcodes `$19` and
`$83` may also retry after checking the current slot. Opcode `$B1` consumes a
similarly terminated value-remapping table without branching to its values.

The walker follows indirect writes only for the reviewed text-pointer bytes
`$55/$56` and the literal slot field `$05E2`. It follows native calls only
for the reviewed decoder and palette fade.

Three `$44` indexed jumps have explicit candidate bounds of 11, 4 and 8
entries, derived from their immediately preceding clamp/divide or mask paths.
The walker follows those entries and marks their table bytes. Other callers
and their index ranges remain unverified. It reports each jump as partial and
records which preceding instructions its edges depend on. Those bounds do not
cover every target that independent entry might select. At `$F434`, it
follows the three indices observed in emulator traces and separately marks
indices 3-31 as conditional on the `$F432` predecessor and unchanged slot
value. Independent entry can use other indices, so the jump remains
incomplete. Unbounded `$44` sites without reviewed indices still stop.

The `$8A` stack-buffer operation may return normally. Its `$FF` form clears
`$0100-$011F`. A sufficiently deep stack could put a return address in that
range, so the walk does not model every possible outcome. The `$79`, `$84`,
`$8D/$8E`, `$A4`, `$AA`, `$BC-$BE` handlers may also return normally. Those
graph edges do not prove execution or termination.

The `$11/$12` selectors may continue or yield. `$65`, `$A2`, `$AF`, `$B2`
and `$B8-$BA` can return to the next command. Opcodes `$70`, `$71` and `$AD`
can write into the active stack page, so only their normal-return edges are
modeled. The field setters `$37-$3A` and `$88` can return normally.

The `$3C`
field comparison uses the last two operands as its conditional target; the
selector and comparison byte are not part of that address. `$73`, `$75`,
`$7E`, `$97`, `$B0`, `$B4/$B5` and `$C1` may return normally. `$59` and
`$7C` can return or yield. `$74` restores the last saved command pointer and
yields, so it can retry without falling through. `$57` may fall through, but
its possible branch target uses a stale high operand and remains unresolved.
`$7F` may retry when `$E7` is nonzero or continue after a normal indexed read
and state setup. Its 8-bit doubled index has 128 possible even byte offsets.
The selected data and physical mapping remain unresolved. The `$B8`
linked-slot scan can loop indefinitely, so its graph edge assumes a return.
The `$77` voice check can branch to its encoded target or continue.

Opcode `$17` can continue if its saved-pointer high byte is `$FF`. Otherwise
it restores a dynamic pointer whose target the walker does not infer. The
`$98` state-save handler marks slots disabled before yielding. A later `$99`
restoration can re-enable retained slots, so the walker records a possible
resume after `$98`. It does not guarantee slot survival or restoration. The
`$0F` and `$99` main-state changes stop the walk because their later
scheduling is unproven. In particular, treating the bytes after `$0F` as an
automatic continuation produced a speculative command decode over a
descriptor-linked record. Separate evidence supports the record's data
representation. Unknown, dynamically computed and unreviewed handlers stop
their paths. The walker rejects malformed lengths, records that cross the
physical bank boundary and invalid input, and reports physical-byte overlaps
and any nodes left by its traversal limit.

`make indexed-jump-inventory` also records the 128 possible physical-bank-1
read positions for `$B62C`, `$D48F` and `$E71C`. It separates entries
bounded by preceding instructions from the source classification of candidate
targets. The physical mapping and any use of independent-entry indices remain
unproven.

## Observed commands

An earlier bounded walk of the pinned v1.5 input found 1,941 candidate
commands starting from the descriptor-derived entries, with 38 nodes stopping
at dynamic or unreviewed handlers and no physical-byte overlaps. Those are
static candidates, not a complete script inventory, gameplay evidence or
source ownership. The ignored JSON retains operand bytes for local
examination. The tool adds none of them to tracked source or the progress
count.

Separate execution probes sampled the command pointer and alternate-bank value
at the bank-0 fetcher, then inspected Mesen's mapped address after switching.
They confirmed 10,404 Noah, 10,822 Moses and 11,102 David fetches in PRG bank
1 with no mapping disagreement. Of the previously unowned observed commands,
194 in 18 contiguous, nonconflicting groups are now represented with named
command forms. Other paths and any conflicting interpretations remain local.
The captured command identities, mapping checks and probe scripts remain in
ignored `analysis/us-v1.5/`. These opening sequences do not cover the full
game.

A separate local walk from the 808 distinct observed command pointers found
1,444 possible nodes and no overlapping decodes within that walk. The reviewed
nonconflicting portions now include 249 additional candidate commands and
three `$95` lookup tables in source. The inputs and output of this second walk
remain in ignored local analysis. A successor of an observed command is still
only a static candidate until that path is exercised.

The longer 8,000-frame exploration provided 1,322 distinct command entries; a
separate walk found 2,016 nodes without internal overlapping decodes. A
further 109 commands and the terminated `$95` table at `$D629` are represented
as source after checks against existing ownership and candidate records. The
three entries at `$F435` were each selected by the indexed-jump handler in
MesenCE. Their presence does not bound the handler's index.

## Audio and script overlaps

Twenty-four candidate bytes also decode as single audio notes under bank-1
selection. Each of these bytes is represented once in eight shared extents,
with an assembler assertion equating the note and reviewed BOGUS opcode views.
The selection excludes other catalogued uses and competing script boundaries.
It does not establish which path executes or whether every context selects the
bank-1 audio mapping.

Opcodes `$33` and `$34` call the selected-field helpers with negative-mode
slot updates, then either yield or return. The selector can also abort the
handler. The static walk retains the following command as a possible next or
resumed entry in each case. This is a possible control-flow edge, not proof of
slot selection, resumption or execution.

A further 65 candidate multi-byte BOGUS commands share 177 bytes with possible
single-byte audio notes. Their source emits the reviewed script form and
asserts the note values for every byte, including little-endian branch and
voice-pointer operands. The candidate inventory at that checkpoint found no
other script boundary or catalogued data use in those selected extents. The
later `$45` expansion found alternate candidate boundaries within eight of
those bytes. Both the interpretations and the bank selection remain
conditional. They do not prove that either path executes.

Opcode `$45` conditionally branches using its first two operand bytes after
comparing the third with `$07C0,x`. The walk records both target and
fallthrough. The widened walk also finds three further four-byte script/audio
overlays and alternative candidate boundaries at `$A9FF`, `$AA01`, `$AA90`
and `$AA91`. This is conservative static evidence, not proof of reachability.

The possible `$EC20` command sequence branches to the existing `$EC2B` script.
Its known predecessors arise in speculative static paths, including possible
script decodes over native-code bytes. The sequence is represented as a
candidate. No runtime entry or descriptor association is established.

At `$E01A` and `$E023`, two possible nine-byte voice-pointer commands share
bytes with candidate mode-2 slot records. The source checks both layouts and
also records the unresolved alternative script boundaries inside those ranges.

## Conditional indexed jumps

The `$F432` predecessor uses `$3F/$24` to compute a value from `$0550,x` in
the range 0-31. If the same slot reaches `$F434` without an intervening write,
those are the possible indices. Independent entry may supply any low byte.
`$44` discards bit 7 when it doubles that byte, giving 128 distinct read
positions. The controlled reference/build probes and bank-1 table inventory
are available via `make indexed-jump-inventory`. Positions beyond the first
three overlap script or candidate map-layout bytes. That overlap does not
prove execution as table entries. The general script walk follows the three
observed indices plus the other 29 candidates that depend on the preceding
instructions. It reports the site as incomplete. Paths reached through those
edges depend on the same condition. The merged graph does not retain every
path's conditions, so it includes paths that may never execute.

`make prg-inventory` compares this expansion with a candidate graph using only
the observed indices and the same roots. In the current scan it adds 79 script
bytes and 303 record-field bytes. Shared roots can obscure further conditional
paths, and neither graph proves execution.

The source now labels the alternate candidate entries at `$A9FF`, `$AA01`,
`$AA90` and `$AA91`. Their overlapping opcode relationships are checked at
assembly time. The labels do not prove runtime entry or exclude other decodes.
