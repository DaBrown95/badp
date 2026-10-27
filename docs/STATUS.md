# Reference identities and version strategy

The owner requests a complete reconstruction of every variant supplied in
`baseroms/`, completing one version before adapting the work to the others.
There are six files: the unversioned USA release and v1.1 through v1.5.

All six full-file and combined PRG/CHR SHA-1 values match No-Intro metadata
distributed in libretro/libretro-database, DAT version `2026.10.07`, commit
`9a899f5b13ed1c355491e342203be29bc573323b`. The source and relevant catalogue
facts are pinned in `config/catalogues/no-intro-nes.json`. No ROM was modified.
The unversioned release is not labelled v1.0 without supporting evidence.

Each input is 131,088 bytes: a 16-byte NES 2.0 header, 65,536 bytes of PRG ROM
and 65,536 bytes of CHR ROM, with no trainer or trailing bytes. The common
header is `4e45531a0408b1080000000000000001`. It declares mapper 11, submapper 0
and NTSC timing. These are header claims; hardware behaviour and reset-bank
mapping remain unverified. Each manifest keeps hardware verification separate
from its exact reference identity.

## Reconstruction order

`config/project.json` selects `us-v1.5` first, followed by `us-v1.4`, `us-v1.3`,
`us-v1.2`, `us-v1.1` and `us-unversioned`. v1.5 is the latest numbered supplied
release, not a claim that it fixes every bug. v1.4 shares its complete CHR data
with v1.5, making it a useful first adaptation target. Other CHR payloads differ.
All six PRG payloads differ. Raw byte differences at the same physical offsets
do not measure semantic changes, because relocated code/data can inflate them.

Complete the primary version's source inventory, matching build and runtime
checks before expanding reconstruction to the next. Reuse shared source and
structured data definitions, with explicit version differences. Do not fork six
independent source trees or treat one version's evidence as verifying the rest.
`make audit-all` checks reference integrity for all targets without requiring
simultaneous reconstruction. Keep progress and completion evidence per target.

The v1.5 build now assembles and links to the exact reference, with 20,575 bytes
of source code and 1,838 bytes of structured data across the physical PRG banks.
It still includes 43,123 local PRG bytes and 65,536 local CHR bytes. A total of
660 independent source-change controls verify every listed reconstructed region.
Passing input audits or whole-ROM equality alone is not reconstruction
completion. The developer identifies BOGUS as the
state-machine engine in the [Vance Kozik interview](https://www.nesworld.com/kozik.php);
the original source language and toolchain remain unestablished.

## Next work

1. Trace reset, NMI/IRQ vectors, bank transitions and indirect dispatch. Separate
   native instructions, BOGUS state-machine data, other data and unknown bytes.
2. Verify mapper behaviour, bus conflicts, timing and reset mapping with runtime
   evidence. Map physical banks separately from CPU/PPU addresses.
3. Reconstruct connected routines and data formats, retaining changed-source
   negative controls and one current full-build proof. Build the progress map
   from verified ownership with no invented denominator.
4. Establish repeatable runtime checks for all three adventures and shared
   menus, controls, rendering, audio and progression. Finish source accounting
   and gameplay verification for v1.5, then repeat acceptance for each remaining
   version in the recorded order.

## First v1.5 source evidence

The same reset entry at `$FFE9` appears in both 32 KiB PRG banks. It initializes
the stack, loads `$0C`, writes that value to `$FFB7`, then jumps to `$8000`.
Both banks contain `$0C` at `$FFB7`. Under the documented Color Dreams mapper,
the low PRG-select bits choose bank 0 and writing the value already present at
the address avoids conflicting ROM bus values. This is static evidence, not a
runtime verification of power-on bank state or board behaviour.

Bank 0 begins by disabling interrupts, clearing PPUCTRL, calling the `$9ED0`
PPUSTATUS polling routine twice, and setting PPUMASK. The following reset-state
dispatcher checks a byte against its stored complement and selects timed mapper
write sequences. Several writes target their own immediate operand bytes, so
the write value matches the value driven by ROM during a bus conflict.

The reconstructed bank-0 NMI work handles OAM DMA, PPU update queue flushing,
controller serial reads and dispatch, workspace swapping and PPU scroll/control
updates. Handler targets and several called engine routines remain untraced;
these are static findings, not runtime or cycle-timing verification.

The shared `$FE6C-$FFB2` routines are identical in both PRG banks. They include
bank switching around copies to the stack and RAM, strided and bitwise buffer
copies, and a record fetcher. The fetcher selects a length from a table at
`$FDA7` when X is zero, then copies that many bytes from `($53),Y` to `$60,Y`.
The NMI handlers use different RAM source locations in the two banks.

## Script command dispatch

The bank-0 command loop at `$D54E` calls the record fetcher with X=0, advances
the `$53/$54` pointer by the returned length in `$FE`, and calls `$D57A`. That
dispatcher indexes split low/high address tables using the copied first byte at
`$60`, pushes the encoded address and returns into the handler. The tables at
`$D585` and `$D64A` each contain 197 entries through `$D70E`; the handler entry
is the encoded address plus one because `RTS` increments it. The length table at
`$FDA7` has the corresponding 197 entries and is identical in both PRG banks.
The combined source descriptors preserve each observed record length and handler
entry while emitting the three original tables in their original layouts.

The first decoded handler group includes setting the script pointer from
operands `$61/$62`, conditional pointer changes, per-slot state updates, and
yield/restore paths. Handler meanings are recorded only as supported by the
instructions; many calls and higher-level state names remain unresolved. The
table boundary follows the adjacent native code; no runtime bound check has
been established, and no link to the named BOGUS engine is claimed yet.

All 197 handler table entries now target reconstructed source, including `$18`,
which is located separately near the end of bank 0. These include an eight-entry
single-bit mask table, a four-pair operand loop and searches over sixteen slots. The slot
search skips the current slot and records marked `$FF`; opcode `$36` either
searches by fields or scans another flag before calling `$D4DA`. Those higher-
level slot meanings and the downstream calls are still unverified.

The following handlers include a selector that reads slot fields or calculates
values, 16-bit slot operations and accesses to single-byte or paired arrays at
`$0140` and `$0120`. One slot-counting loop contains two successive identical
conditional branches; both are preserved. These are static observations and
byte-matching results, not runtime or gameplay verification.

Later handlers share slot initialization, busy-state waiting, indexed record
fetching and value-array operations. Two helpers deliberately remove a return
address before returning or jumping; the matching source preserves their stack
behavior. Names and higher-level roles remain provisional.

The later handlers include seven-byte indexed records, indirect byte access,
slot scans and coordinate comparisons. Opcode `$B0` enters the `$8C` scan after
its initialization, and `$BF` shares the `$AB` handler. Some handlers still
call unconverted routines, so covering their entry points does not establish
the behavior of all commands. The loop entry at `$D4F8` restores the pointer,
updates counters and handles pending slot state. The `$F2CC` helper increments
the 16-bit script pointer twice; `$95` and `$B1` invoke it twice per record.

Shared routines now include arithmetic, bit shifts, field selection and
conditional stack unwinding, slot coordinate calculations, and field update
modes. An isolated instruction-subset check executed the assembled arithmetic
against all 65,536 eight-bit multiplication pairs, 4,080 valid division cases
and all 256 byte negations. This is focused arithmetic evidence, not an NES
emulator or gameplay test.

The slot-record loader at `$F0D8` fetches ten bytes, reads packed dimensions
and calls several still-unconverted placement routines. Its table-address
helper computes `$9F06 + 4*index + low(2*index)`; for indices at or above
`$80` this differs from six times the index because the first carry is lost.
That is an observed arithmetic property, not evidence those indices are used.
Coordinate selection and the related direction-flag update are now source.

The post-dispatch path now includes slot eligibility, signed-field adjustment
and limits, linked-slot position calculation, direction-bit updates and change
tracking. The unlinked movement path includes split-step collision probes
and retries. Its slot-position query, stack-buffer comparison and banked map
chunk lookup are now source; several downstream calls and map data remain
local input. Slot-record validation also preserves its early-return stack
behavior. Names and intended gameplay effects still need runtime verification.

The initializer at `$CF02` reads six-byte descriptors at `$9F06`: a two-byte
encoded pointer and four bytes copied to `$05D0`, `$0610`, `$05E0` and `$0520`.
There are 114 entries before `$A1B2`, where a separate 22-entry address table
is read at `$CB9A-$CB9D`; `$A1DE` begins the next lookup table. The runtime
index bounds and higher-level meanings of these fields remain unverified.

The slot allocator scans for a free slot, otherwise choosing the last eligible
replacement or a slot passing its distance check. A focused instruction-subset
check exercised free slots, replacement, distance fallback and exhaustion on
synthetic RAM, with cleanup stubbed. The current-slot path also builds and
scans contact bounds before entering the script loop; runtime gameplay effects
remain unverified.

Two parallel position-record searches use the same control flow with different
zero-page pointers. Focused instruction-subset checks on synthetic RAM covered
both copies, traversal in both directions, page crossing, a missing key and
a high-bit range case. These are not gameplay or mapper tests.

Frame setup reads starting pointers for those searches from parallel 22-entry
tables at `$A3EC` and `$A418`. The frame dispatcher and its position-record
caller are also source, including the `$F0` record-type path that prepares a
slot. Record streams, other frame callees, PPU timing and runtime index bounds
remain unverified.

Sprite placement and record helpers now update shadow OAM coordinates and
attributes, including the original `$FC` offset skip. A focused instruction-
subset check on synthetic RAM covered grid placement, coordinate saturation,
the offset skip, invalid indices and two record modes. The frame loader now
selects direct or indexed frame pointers and writes tile and attribute data
for all four flip combinations. A separate synthetic instruction-subset check
covered those paths and the reserved offset. PPU timing and gameplay still
need separate verification.

Palette-stream setup and animation now queue the matching background and sprite
palette writes. The scroll dispatcher, target clamps and both axis workers are
also source, together with the scroll mirror, chunk-pointer helpers and tile
row/column redraw queues including attributes. Synthetic checks covered palette
timing, scroll boundaries, queue capacity, tile and attribute copying,
nametable splits and attribute-bit merging. They do not verify PPU timing,
mapper behavior or gameplay.
The background palette loop retains Y from its offset calculation, unlike the
sprite loop; a high-offset synthetic case preserves that original behavior.

The split-screen setup and sprite-zero initialization are source. State bank
selectors and two palette-stream pointer tables are structured metadata; the
palette data itself remains local. Synthetic checks covered the setup fields,
original extra borrow, saved-state gate and pointer selection.

A local script-entry inventory follows the 114 observed slot descriptors to
84 distinct record addresses: 83 fit entirely within the inferred bank, while
one address, referenced five times, crosses the bank boundary. The inspected
records yield 71 distinct candidate script entries whose first command lengths
are valid. Bank mapping is a static inference and the tool does not follow
branches or prove execution. Its output is ignored local analysis and does not
count as reconstructed PRG.

The [script-flow inventory](SCRIPT_FLOW.md) follows reviewed successor rules
from those candidates. It finds 703 candidate commands and stops at 69 nodes
with dynamic or unreviewed handlers, with no physical-byte overlaps. Branches
and resumes remain unverified possibilities; this analysis adds no PRG credit.

Two descriptor-derived candidate graphs at PRG bank 1 CPU `$BCC0-$BCE2` and
`$BDBF-$BDCC` are now structured BOGUS source. Their command lengths and
successors follow the reconstructed interpreter, with branch targets expressed
as bank-relative labels. Their gameplay roles and execution remain unverified;
the rest of the script inventory is still local analysis.

Controller handlers now express slot actions, pause toggling and signed motion
updates, including the original stack-unwinding gates and overflow checks. The
frame motion and slot draw-coordinate paths are source, with synthetic checks
for direction gates, fractional components, bounds and slot selection. Position
record lookups were stubbed in those checks; gameplay remains unverified.

The deferred PPU update handler, its stream command processing and decimal
formatting are source. Synthetic checks covered fill and banked-copy requests,
absolute and relative stream addresses, pauses, queue pressure, the timer and
number formatting. The checks execute instruction subsets and do not establish
real PPU timing or bank-switch behavior.

Map initialization now reads dimensions, prepares the PPU and draws initial
columns. Its original zero-width case enters the 8-bit column loop 256 times;
a synthetic check preserves that behavior without asserting a real map uses it.
Scroll requests, palette pointer setup, OAM rotation and sprite allocation are
source. Synthetic allocation checks covered direct and animated headers,
occupied records, OAM exhaustion, reserved entries and sprite size.

The sprite animation update now advances timers and handles loop or hold-on-
last-frame behavior. The audio voice start, stop, arbitration and command
interpreter are source; instrument, note-preset and period tables remain local.
Focused instruction-subset checks on synthetic records exercise animation,
audio commands, APU register writes, voice bounds and pointer carry; they do
not verify hardware timing or sound playback.

The original five-register audio command reads its fifth value from the sixth
stack-buffer byte, although its caller copies only five bytes total. A synthetic
check confirms the resulting stale stack value and five-byte pointer advance;
the matching source preserves this apparent bug.

A local decoder reads both pointer tables, deduplicates aliases and round-trips
32 streams containing 523 eight-byte records plus four-byte terminators through
`$B51C`. Keys, the high-bit range flag, type bytes and five parameters are
represented without guessing the remaining semantics. Its JSON is ignored
under `analysis/`; no position-stream bytes are credited as reconstructed PRG.

The [source map](../config/source-us-v1.5.json) records bank, CPU address, size,
classification and control for every owned region. `make build` retains the
actual link map, debug information, source snapshots, local inputs, control
outputs and hashes under `build/us-v1.5/`. The assembler and linker are built
from the checksum-pinned cc65 V2.19 release; V2.19 reports itself as V2.18 with
the release's Git build ID, as documented upstream.

The repository retains the Sims project's MIT licence, AI disclosure,
owner-run contribution policy and strict matching standard. The GitHub
repository was created private on 2026-10-27, with issues, discussions, projects
and wiki disabled.
