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

The v1.5 build now assembles and links to the exact reference, with 21,474 bytes
of source code and 19,687 bytes of structured data across the physical PRG banks.
It still includes 24,375 local PRG bytes and 65,536 local CHR bytes. A total of
1,306 independent source-change controls verify every listed reconstructed region.
Passing input audits or whole-ROM equality alone is not reconstruction
completion. The developer identifies BOGUS as the
state-machine engine in the [Vance Kozik interview](https://www.nesworld.com/kozik.php);
the original source language and toolchain remain unestablished.

## v1.5 opening-gameplay evidence

`make verify-gameplay` runs 6,340 NTSC frames each for Noah, Moses and David,
plus a separate Noah inventory scenario,
in pinned MesenCE 2.2.1, with zeroed power-on RAM and fixed mapper/alignment
settings. It compares the audited reference and verified build under the same
menu and movement inputs. All three reached their opening areas and showed a
change in scroll and screenshot after rightward input. The Moses sequence also
presses B to lift the baby, jumps past the first approaching enemy and crosses
the first water gap. It recovers him after a later collision, backtracks over the
position trigger, completes the first two levels and enters level three. There,
it picks Moses up after a series of jumps and carries him through further jumps
and movement to a higher position. Sampled slot fields show the link, its loss,
recovery and carried finish; pinned screenshot hashes check both success screens.
In David's opening, the verifier pairs native position-event writes for slot
descriptor `$6E` with mode-zero loads of encoded record `$6365`. It also pairs
controller requests for descriptor `$01` with their record loads: the Moses
sequence records 38 `$24` and four `$2D` matches, and the Noah inventory
scenario records one configured `$36` match, with no mismatches. The sixty-two
sampled frames, slot fields, state and cycle counts, mapper-write streams, NMI counts, OAM DMA and
APU-register write streams agreed between the reference and build. Both PRG
banks appeared in the emulator's mapper-write mapping; every observed write
value equalled the mapped ROM byte. This describes the emulator model and the
tested paths, not physical board behaviour or proof of timing on hardware.

Mesen reports uninitialized-read warnings in these runs, equally for the
reference and build; their causes remain to be investigated. Audio output and
complete progression have not been checked.
Screenshots, event streams and the proof remain under ignored
`reports/us-v1.5/runtime/`.

A separate reference-only execution callback for the Moses carry sequence
observed no instruction starts in the source map's remaining local PRG gaps.
This covers only the exercised path and does not classify every byte or establish
the behaviour of paths that were not reached. Its local trace remains in
`analysis/us-v1.5/unowned-carry-execution.json`.
A reference-only trace through the level-two pickup likewise found no native
instruction starts in local PRG gaps. All 676 observed script pointer/bank
pairs began inside source-owned regions; this does not verify their complete
paths or later level-two interactions. The trace remains under
`analysis/us-v1.5/*stage2-pickup-execution.json`.
A reference-only trace of the third-level pickup and movement to frame 6,340 found no native
instruction starts in local PRG gaps. Its 747 distinct script pointer/bank
pairs and 49 record pointer/bank/mode combinations all begin in source-owned
regions under the existing bank mapping. This checks entry addresses, not
every byte fetched or the mapping on physical hardware. The trace remains in
`analysis/us-v1.5/stage3-higher-carry-execution.json`.
The later second-level crossing trace observed 708 distinct script pointer/bank
pairs, all beginning in source-owned regions, and no native instruction starts
in local PRG gaps. The slot-record loader read `$36E5` in mode `$02`; a
post-switch mapping check confirmed PRG bank 1 for that fetch, among 327 checked
fetches without a mismatch. The resource pointer and five fields actually read
at `$B6E5` and `$B6E9` are now source, with separate source-mutation controls.
The two intervening bytes and pointed-to sprite remain local. This is evidence
for the exercised emulator route, not proof of all uses or physical hardware.
The trace files remain in ignored `analysis/us-v1.5/`.
The first 4,900-frame reference/build attempt reported differing Moses
runtime evidence without identifying a field. A subsequent focused comparison
matched; the cause of the initial discrepancy remains unestablished. The failure
log and focused comparison are kept locally in `reports/us-v1.5/runtime-failures/`
and `analysis/us-v1.5/compare-stage2-4900-diagnostics.json`, respectively.
Later parsed scenario failures retain both sides, screenshots and event streams
in `reports/us-v1.5/runtime/failures/`; the comparison remains strict.
Local jump-timing explorations beyond frame 2,800 lost the baby before the
frame-3,000 samples; the attempts and screenshots remain under
`analysis/us-v1.5/moses-second-*`. They are exploratory reference runs, not
successful reference-versus-build checks.
A further reference-only jump sweep carried him through the frame-3,000 sample
in one tested timing, but he was no longer linked at frame 3,100. The sweep
inputs and incremental results remain in `analysis/us-v1.5/moses-jump-sweep/`.
Later reference-only timing experiments paused before the soldier and recovered
Moses after a subsequent hit near the right edge. Backtracking and returning
then reached the first-level success screen. Inputs and results remain in
`analysis/us-v1.5/moses-pause-sweep/`, `moses-edge-pickup/` and
`moses-edge-recross/`.

The emulator archive matched the published SHA-256. On the test machine,
`codesign --verify` reported its bundled signature as invalid; the headless
run succeeded without changing system security settings. The emulator version,
SDL2 library hash and operating system version are recorded in the local proof.

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

The main-state initializer and transition into frame processing are now source.
They prepare slot, bank, palette, scroll and map state before the existing
position-stream initializer. On a nonzero horizontal reference difference,
the translation path uses the existing `$FF` scratch byte without first
calculating the vertical difference. An isolated instruction-subset check with
stubbed callees exercised that path, a vertical-only difference and unchanged
references; it is not hardware or gameplay verification. Temporary local
disassembly and check files were retired after integration.

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

Three indexed script jumps at bank-1 CPU addresses `$B62C`, `$D48F` and
`$E71C` have candidate table bounds of 11, 4 and 8 entries from their
immediately preceding arithmetic or mask operations. Their tables and nearby
slot, palette, audio and movement scripts are represented in source. These
predecessor bounds do not establish all possible callers or runtime behavior.
The temporary batch transcription script was retired after integration; the
maintained source and current build proof remain.

The inventory script indexes encoded pointer entries at `$D05F` and `$D09D`;
four entries at each base are represented as pointers to locally supplied list
and display data. The candidate `$FD05` script indexes five pointer entries at
each of `$FCE3` and `$FCED`, followed by five state bytes at `$FCF7`. Its
two-byte reads can cross an entry or the boundary into the following slot
record. These source entries preserve the observed layout without asserting
runtime index bounds; the pointed-to game assets remain local.
A Noah inventory comparison opened and closed the screen on both the reference
and a fresh matching assembly, observing index zero at both `$D05F` and `$D09D`.
The local trace and screenshots remain under `analysis/us-v1.5/inventory-*`;
this does not verify the other entries.

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

The 83 descriptor-linked slot records that fit within a physical bank now
express the nine bytes used by the loader as resource and script pointers,
mode flags and four slot fields. The loader actually fetches ten bytes, and
the tenth may belong to the next record or command. A separate descriptor
points across a bank boundary and remains unclassified. Resource payloads
remain local, and pointer roles and execution require runtime confirmation.
The temporary record transcription script was retired after integration;
the structured source and current build proof remain.

The [slot-record access inventory](SLOT_RECORD_FLOW.md) follows possible
script/descriptor contexts and distinguishes negative-mode compact entries from
zero-mode full records. Another 95 reviewed records are structured source;
ambiguous accesses remain local. These relationships are static candidates,
not proof of slot identity or gameplay execution. The temporary classification
and transcription files were retired after integration.

The merged contextual script trace exposes 13 physical bytes with conflicting
decodes across different possible entries in the existing `$BD1B` and `$DC35`
script regions. The competing entries depend on unverified descriptor
associations at `$DA40` and `$ED71`; those conflicts remain unresolved.
Another 35 physical bytes overlap possible record reads and candidate script
decodes, including nine in the existing `$ED71` script and six at `$ED4A-$ED4F`
in the existing `$ED45` script. The latter became visible after following a
possible `$18` audio-restart return; its descriptor association and all these
competing uses remain unverified. Twenty script regions were represented as
named commands after an earlier non-overlap review; the later candidate use
requires further investigation. Temporary transcriptions were retired after integration.

The map lookup uses 146 two-byte offsets, each a multiple of 68, into locally
supplied map-chunk data. The offset table and state-indexed vertical-base seeds
are source; map layouts and chunk contents remain local. Runtime bounds on
either table have not been established.
`make prg-inventory` combines the current verified source map with candidate
map, descriptor-context, native-event and direct-target scripts and records, palette setup,
candidate audio and PPU-stream uses, round-tripped packed text, and optional
validated audio and sprite traces. It counts physical bytes once while
retaining overlapping uses. With the current local traces, 1,022 PRG bytes have no use
in these inventories; that number is not a count of remaining code. The report
also retains 4,561 possible map/script overlap bytes and 516 possible record/script
overlap bytes across the combined inventories. The expanded field-setter walk
introduces many speculative competing decodes; it does not establish their
reachability. It also reports 4,257 source-owned bytes covered by candidate
data uses, which can include compatible uses as well as competing ones. The
report records its input identities and writes metadata only to
ignored `analysis/us-v1.5/prg-inventory.json`.
`make audio-flow` follows literal voice starts in reconstructed commands and the
native opcode-$18 start. It models both loop outcomes, stops at voice-stop
commands and follows the restore-to-start-plus-one path. The current static
walk has 36 starts, 790 command contexts and 1,293 distinct physical bytes,
with no conflicting decodes or five-byte fetches crossing a bank. Of the 706
bytes used by the existing audio trace, 605 also occur in these candidate paths.
Indexed or otherwise dynamic starts and unobserved playback remain open; the
decoded audio payloads stay local and do not count as reconstructed code.
`make ppu-streams` decodes 19 candidate inventory PPU streams from literal queues,
pointer tables and remap cases. Their logical commands cover 429 physical bytes;
the current candidates have no overlapping streams or possible bank-crossing
lookahead. Queue timing, other starts and reachability remain unverified, and
the text payloads remain local.
`make map-data` decodes 22 state-table entries into 14 distinct candidate
layouts and 146 chunk-table entries into 145 distinct referenced chunks. The
layouts and chunks round-trip to their local bytes; none of the decoded grid
indices exceed this table, and the decoded layouts and chunks do not overlap
one another. Runtime bounds remain unverified. The context script graph has
29 candidate entries overlapping 65 map bytes at bank-1 CPU `$80FF-$8104`
and `$8118-$8152`; these competing interpretations remain provisional.

A directed 16,000-frame emulator probe paired map header and first span fetches
after bank switching. Noah, Moses and David recorded 11, 11 and 5 layout
fetches; 130, 3,030 and 24 row spans; and 17,246, 8,169 and 9,554 column
spans, respectively, with no mapped-bank disagreement. The sampled spans were
in referenced bank-1 chunks, and Noah sampled reads within the `$8118-$8152`
map/script overlap. This is limited emulator evidence, not full map, PPU
timing or physical cartridge verification. `make trace-map` reproduces the
probe; its payloads and outputs remain local.

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
from those candidates. It finds 1,941 candidate commands and stops at 38 nodes
with dynamic or unreviewed handlers, with no physical-byte overlaps. Branches
and resumes remain unverified possibilities; this analysis adds no PRG credit.
The `$0F` state change now terminates a traced path rather than presuming a
later resume. This reclassified a speculative command decode at `$BDB6` as a
descriptor-linked slot record; its separately referenced script starts at
`$BDBF`. A possible additional use of those bytes remains unverified.

Fifteen additional connected script regions include menu-state, palette,
audio and slot operations. The `$8A` stack-buffer clear is followed only as a
possible normal return: its `$FF` form can overwrite low stack-page addresses.
The new candidate paths have not been verified in gameplay; some apparently
ambiguous successors remain local. Temporary transcription files were retired
after integration, leaving the maintained source and current matching proof.

Two descriptor-derived candidate graphs at PRG bank 1 CPU `$BCC0-$BCE2` and
`$BDBF-$BDCC` are now structured BOGUS source. Their command lengths and
successors follow the reconstructed interpreter, with branch targets expressed
as bank-relative labels. Their gameplay roles and execution remain unverified;
most of the script inventory is still local analysis.

Additional descriptor-derived entries at bank 1 `$B900`, `$B968` and `$BA53`
are structured, including the separately targeted command at `$B934`. The
nonzero-mode record load at `$B92E` preserves the script pointer, so its
continuation at `$B931` is also represented as a jump. Additional candidate
graphs at `$BDD6`, `$D6E0` and `$EFF0` are structured. These are static command
decodes; their gameplay roles and execution have not been established.

The interpreter's `$95` command selects an encoded target by a two-byte slot
value from inline four-byte cases, with a two-byte zero-target terminator.
Graphs at bank 1 `$BA75` and `$BE03` now express their lookup cases and
additional connected blocks as source; some referenced data and downstream
commands remain local. The fetch reads
four bytes even for the terminator, an important distinction for boundary checks.

Three opening-gameplay traces identified 194 previously unowned command entries
in 18 nonconflicting contiguous groups. They are represented by named commands,
with independent labels even where neighbouring bytes were also observed. Each
group has a source-change control; unclassified paths and lookup data remain local.
The same runs confirmed the script fetcher's bank mapping in the emulator as
described in [script-flow notes](SCRIPT_FLOW.md). The probes and logs remain in
ignored local analysis and do not establish full gameplay coverage.

Following the reviewed successor rules from 808 observed command entries
produced 1,444 candidate nodes, with no conflicting byte decodes within that
walk and no pending nodes. Another 249 commands in 25 groups and three
terminated `$95` lookup tables are now source. The selected bytes were checked
against the prior static walk, candidate record fetches, observed record
accesses and existing ownership. The new edges are static possibilities, not
evidence that their branches or gameplay paths were taken.

Longer reference-ROM exploration held right and periodically pressed A after
entering each adventure, ending at frame 8,000. It observed another 193 commands
in 21 nonconflicting groups and seven zero-mode records in five groups, now
represented as source. Separate probes checked the mapped bank after switching
for 61,995 Noah, 59,054 Moses and 63,651 David command fetches, and 882, 913
and 911 record fetches respectively, with no emulator mapping disagreements.
All seven added record addresses were included in those comparisons. These are
exploratory runs, not completion of any adventure. A subsequent reference/build
comparison of the same 8,000-frame inputs matched seven sampled screenshots and
state snapshots per adventure, mapper/NMI/APU/DMA activity counts, and the
observed script and record access counts. Its proof remains in ignored
`reports/us-v1.5/runtime-long/`. Other newly encountered records observed only
in different modes, or whose interpretations need review, remain local. The
probes, trace data and screenshots are ignored locally.

The record at bank 1 `$B936` was accessed in both zero and negative mode and
is now structured source. Byte 2 occupies the low script-pointer position in
zero mode, but the `$FF` high byte skips its read there; negative mode reads
byte 2 as flags. Both interpretations retain the same physical bytes.

The long-run command pointers also seed a separate static walk: 1,322 distinct
entries produce 2,016 candidate nodes with no internal byte overlaps or pending
nodes. Another 109 commands are source in 38 groups after excluding candidate
record and competing script overlaps. Six were observed in the long runs; the
remaining successors are static candidates. Every command entry observed in
those runs is now covered by a source region, without implying complete script
or gameplay coverage.

The slot-record loader was also observed reading 17 previously local records
in nine contiguous groups. Compact negative-mode records and full zero-mode
records are represented separately, with script-pointer labels where known.
When a resource pointer is `$FFFF`, later fields can be skipped by the loader;
their original bytes are retained without claiming they were read at runtime.
The records do not overlap any candidate command or table bytes in the current
static inventory. The traces establish only the tested opening paths.
The corrected mapping probe paired every sampled loader entry with the mapped
fetch: 124 Noah, 83 Moses and 145 David, including all 17 records, with no
mapping disagreement in MesenCE. An earlier probe mistakenly sampled the
script pointer at loader entry; its misleading generated output was retired.

Opcode `$9B` invokes a native routine using an encoded RTS address and restores
the default bank after return. Its observed bank-1 target at `$BEEA` decodes
five-bit symbols and queues a `$BF` update using a stack-page buffer. Its mask,
shift, advance and character tables are structured data. A local mathematical
check compared all 65,536 synthetic byte pairs at each of the eight phases with
an independent bitstream extraction; the phase advances total five bytes.
This confirms the bit extraction, not runtime bank switching or message rendering.

The decoder's indexed table has 52 ordered bank-1 text pointers. The local
`make packed-text` analysis decodes all 52 records through their terminating
symbols, each within the next record boundary, and finds 423 line-break commands.
It re-encodes each record byte for byte, retaining character-table choices and
padding bits. Decoded message content remains ignored locally. The pointer table is structured
source, while the message payloads are still local inputs and receive no PRG
credit. The connected script paths and their `$B1` remapping table are source.

The other observed `$9B` native target is a bank-0 palette fade at `$B51C`.
Its four palette passes, VBlank polling and register writes are reconstructed;
there is no runtime evidence yet for PPU timing or the resulting display.

The native-call wrapper at `$FD88-$FDA6` is identical in both physical PRG
banks and is now shared source. In the opening traces, bank 1 executed its
`$FD96` continuation after the bank switch: 16 times for Noah and 20 each for
Moses and David. Its one source mutation is checked against both bank copies.

Additional connected bank-1 scripts at `$B6EE`, `$B89C`, `$B999`, `$BB69`,
`$BDFF`, `$DC35` and `$DF0F` express their commands, branches and inline cases in source.
They include slot updates, linked-slot checks, map reads and waits. Their exact
gameplay roles remain unverified. The three `$B999` indexed byte regions are
now source; `$54` reads two bytes at each indexed address, and those reads can
cross region boundaries. The emulator observed offsets 1, 5 and 11 in Noah,
Moses and David respectively, including reads from the first region into the
second. The handler does not establish an index bound.

The three adjacent `$F435` indexed targets are source. Long-run probes observed
indices 0, 1 and 2 and verified their mapped PRG bank and targets in MesenCE.
The original handler does not bound the index, so other values may read beyond
these three entries. A separate terminated lookup at `$D629` is also source.

A further 12,000-frame reference-ROM exploration varied movement and pressed A
and B periodically. It reached another 40 previously local command entries and
five zero-mode records, now represented as source. Mapper checks paired every
sampled command and record fetch with its physical bank in MesenCE: 110,168,
94,256 and 110,353 command fetches, and 2,100, 1,388 and 2,071 record fetches,
for Noah, Moses and David respectively; none disagreed with the predicted bank.
The five added record addresses were directly checked. This is exploratory
evidence, not completion of the adventures or physical hardware verification.
The reference and matching build subsequently agreed on seven sampled frame
screenshots and state snapshots per adventure, hardware activity counts, and
script and record access counts for the same inputs. The local proof is in
ignored `reports/us-v1.5/runtime-interaction/`. Every command byte observed in
these inputs is covered by a source region; other gameplay inputs and later
paths remain unverified. Logs and screenshots remain ignored locally.

Following nine previously unowned literal branch targets in maintained source
found 104 candidate nodes with no internal overlaps or pending nodes. After
excluding existing ownership, candidate record reads and competing decodes,
81 commands in 12 groups are now source. Their reachability remains provisional.
The `$A4` command clears bit `$04` of slot field `$0630` when its operand is
`$FF` and sets that bit for every other operand.
A further walk from the 16,000-frame command entries and newly exposed literal
targets found 25 nonconflicting candidate commands in 13 groups. These use
reviewed handlers but remain static possibilities, not observed execution.
The walk also found an overlapping decode and other ambiguous entries, which
remain excluded from the new source.
The `$67` yield and `$89` relative-position path also allow possible later
resumes. Two continuations contain 24 further commands represented in source;
resumption, especially after `$89` changes state, is not guaranteed.
Reviewed return and conditional-branch rules for additional slot and voice
handlers exposed 100 more candidate commands in 12 nonconflicting regions.
The `$B8` chain scan can fail to terminate, so its next command is only a
possible successor. A new potential record/script conflict at `$D57C-$D580`
remains local; the descriptor association causing it is unverified.
Seventeen additional nonconflicting candidate record locations expose 69
consumed bytes. Where sentinels cause the loader to skip fields, those bytes
remain local. Their descriptor associations and runtime reachability are still
provisional.
The context walker now follows a possible normal return when a `$FF` script
pointer sentinel leaves the prior pointer in place. Forty nonconflicting
commands reached through those candidate continuations are source; a separate
decode overlapping map-chunk data remains excluded.
The direct `$16` loader now has an inventory that explores its possible mode
classes without assuming the inherited `$57` value. A probe of the directed
inputs paired 582, 503 and 587 `$16` calls with their mapped record fetches
for Noah, Moses and David, with no mapping disagreements. Modes `$00`, `$01`,
`$02` and `$FF` occurred across these runs. The source now includes the
observed zero-mode fields at `$AD18` and the resource pointer at candidate
direct target `$AD3C`. The low byte skipped by the `$AD18` sentinel and
mode-dependent `$AD3C` fields remain local. Twenty-five further commands are
source as possible continuations after direct record loads; their reachability
and inherited modes remain unverified. The direct-target inventory also
reports possible conflicts at `$B077` and `$F156-$F157`; neither conflict is
resolved by the tested inputs.
A different 16,000-frame input sequence reached 31 further commands and five
record locations. A separate mapping probe paired 136,835, 133,793 and 151,587
script fetches, and 2,451, 1,900 and 3,276 record fetches, for Noah, Moses and
David respectively; no mapped-bank disagreements were observed. These inputs
do not demonstrate complete playthroughs.
The reference and verified build agreed on seven sampled screenshots and state
snapshots per adventure, hardware activity counts, and script and record access
counts for this sequence. Its proof is kept under ignored
`reports/us-v1.5/runtime-directed/`.
Five records observed in modes `$01` or `$02` now represent only the resource
pointer and fields actually read in those modes; unexamined neighboring bytes
remain local rather than being assumed to be record fields.

A separate 16,000-frame exploratory input sweep reached 106 further command
entries, now source along with two inline lookup tables and 18 record locations.
The recorded inputs exercised all three adventures, but do not demonstrate
complete progression. No previously unowned native instruction addresses were
observed in these runs. A follow-up probe checked every script and record fetch
after bank switching: 144,150 and 2,794 for Noah, 137,694 and 2,083 for Moses,
and 154,156 and 3,113 for David; no mapped-bank disagreements were observed.
One record is used in four loader modes, which interpret its bytes differently.
For records observed only in modes `$01` or `$02`, fields not read in those
modes remain local. These observations describe the tested emulator paths.
The reference and verified build also agreed for these inputs on seven sampled
frame screenshots and state snapshots per adventure, hardware activity counts,
and script and record access counts. The comparison proof remains local under
`reports/us-v1.5/runtime-sweep/`; it does not demonstrate full gameplay.

Three further connected state-machine regions at `$DE0D`, `$E118` and `$EC2B`
and four entry points into `$E120` are structured source. They retain the
observed slot, coordinate, audio and timing operations; their object identities
and in-game execution remain to be verified. Their temporary local transcription
files were retired after integration; the maintained source and build proof remain.

The `$B3EE`, `$E47C`, `$E9BA`, `$ED71` and `$F176` regions extend the script
source with map-value cases, slot updates, indexed audio and state setup. Some
branch destinations and referenced assets remain local, and the object roles
and gameplay effects are provisional. Temporary local transcriptions were
retired after integration; the maintained source and matching proof remain.

A possible saved-state restoration exposes 412 additional physical bytes as
structured script and record source. The connected paths at `$B1F5`,
`$B399-$B3C7`, `$D25A-$D3AE` and `$FD56-$FD65` include a 50-case value
remapping table and candidate direct record `$D3AE`. Opcode `$98` marks slots
disabled and yields; a later restore can re-enable a retained slot, but that
restoration and these particular paths have not been observed in gameplay.
The direct record may be read in several inherited modes, with byte 2 serving
as a negative-mode flag or a skipped low byte of a `$FFFF` script sentinel.

Possible native contact events expose 131 additional structured bytes: five
record fragments or records and connected scripts at `$B787`, `$BCE3`, `$BD4D`,
`$D237`, `$FC81` and `$FC9F`. Four resource sentinels cause the loader to skip
other fields, which remain local. The associations depend on candidate flag
clears and contact; none of these paths has been observed in gameplay. The
`$FC81` fallthrough also creates a possible record interpretation over the
existing `$FC6A` script, so that competing use remains unresolved.

Following flag clears in later descriptor-associated scripts exposes another
128 structured bytes. These include a possible contact path at `$D67C`, its
mode-dependent direct record at `$D68F`, a possible preserved-pointer jump at
`$D735`, and three position-event records. The `$D68F` fields cover candidate
loader modes; its tenth fetched byte is the following script opcode. The new
paths and record associations remain static candidates, not observed gameplay.

Another 41 candidate record accesses are represented by 183 consumed bytes.
Twenty-six are possible contact records: two include all nine fields and 24
include only the resource sentinel and installed script pointer. Fifteen more
use loader modes zero, one or two; their source contains only fields selected
by the examined mode and sentinel checks. The skipped bytes remain local.
The descriptor associations and contact conditions are static candidates, not
observed gameplay. The reviewed extents did not overlap competing candidate
script, map, sprite, audio or PPU uses in the current inventory.

Four zero-terminated byte lists at `$FCA7-$FCE2` are structured source. The
candidate `$FD05` script selects their bases through `$FCE3`, reads each value
with a two-byte indexed fetch and masks to the low byte. Each nonzero value
appears as a key in the `$D27E` remap table. Selection, list meaning and the
relationship between the two scripts remain unverified at runtime; the fetch
also reads beyond each zero terminator.

The `$B532`, `$BD58`, `$D3C9`, `$DB81`, `$E691`, `$EF7E` and `$F24C`
continuations are structured source, connecting earlier map selection, slot,
audio, palette and input state paths. Indirect jump tables and some referenced
data remain local; their runtime behaviour is not established. Temporary local
transcriptions were retired after integration and verification.

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

The local sprite probe observed 83 distinct resource headers and 132 frame
headers in bank 0 during the 16,000-frame exploratory inputs. None of these
observed frames wrap the eight-bit index or cross the bank, although the frame
reader permits wrapping and zero dimension nibbles produce 256 loop iterations.
The resource and frame data remain local, not source-progress credit.
`make trace-sprites` captures the observations with the pinned emulator;
`make sprite-inventory` checks them against the audited ROM and describes the
headers in ignored local analysis. These checks do not verify rendered animation
or establish a complete inventory of sprite assets.
`make prg-inventory` also follows candidate resource pointers from descriptor
records and possible record accesses, assuming the default bank-0 mapping. It
finds 235 possible resource headers and 341 distinct frame headers; their
candidate reads cover 7,080 physical bytes, including 1,600 bytes also covered
by the existing runtime sprite trace. Seventy-three distinct non-ROM resource
addresses and 59 non-ROM frame addresses are excluded; 13 candidate frame reads
cross a bank boundary and remain unresolved.
Animation counts bound these particular candidate table entries, while other
computed indices and unobserved contexts remain open. These are possible uses,
not reachability or exclusive data ownership; graphics payloads stay local and
receive no source-progress credit.

The sprite animation update now advances timers and handles loop or hold-on-
last-frame behavior. The audio voice start, stop, arbitration and command
interpreter are source, along with instrument register pairs, special-note
presets and overlapping windows into the period table. Wider instrument and
special-note indices are possible in the instructions; their valid runtime
bounds remain unverified.
Focused instruction-subset checks on synthetic records exercise animation,
audio commands, APU register writes, voice bounds and pointer carry; they do
not verify hardware timing or sound playback.

A local audio-fetch probe observed 4,639, 4,188 and 4,507 command reads for
Noah, Moses and David respectively in the 16,000-frame exploratory inputs.
All 279 distinct observed entries were in physical PRG bank 1. Their decoded
command extents cover 706 bytes without conflicting observed entries. The probe
checked the mapped physical address after the bank switch; it does not identify
complete streams or establish audio playback correctness. Audio payloads stay
local and receive no source-progress credit. `make trace-audio` reproduces the
probe with the pinned emulator; `make audio-inventory` validates its local
`analysis/us-v1.5/audio-sweep.json` observations against the audited ROM and
writes the decoded inventory to ignored local analysis.
The command decoder has synthetic tests for dispatch, lengths and truncated
inputs, including the original five-register write behavior.

In separate MesenCE opening runs, bank-0 reads included instrument-pair bytes
at `$8F92-$8F93` and `$8FAE-$8FAF` and entries in the period-pointer and
period-value ranges. No reads in the special-note preset range were observed
in these sequences. Mesen's read callbacks can also include CPU dummy or
instruction reads, so these observations do not establish index bounds or
prove that all table entries are used. The probe scripts and logs remain in
ignored local analysis.

The original five-register audio command reads its fifth value from the sixth
stack-buffer byte, although its caller copies only five bytes total. A synthetic
check confirms the resulting stale stack value and five-byte pointer advance;
the matching source preserves this apparent bug.

A local decoder reads both pointer tables, deduplicates aliases and round-trips
32 streams containing 523 eight-byte records plus four-byte terminators through
`$B51C`. The streams and labelled pointer targets are source: keys, the high-bit
range flag, type bytes and five parameters are represented without guessing the
remaining semantics. Its JSON remains ignored under `analysis/`. Each stream has
its own changed-source control. The two empty streams retain their type-zero
record and terminator rather than assuming they are interchangeable.

The [source map](../config/source-us-v1.5.json) records bank, CPU address, size,
classification and control for every owned region. `make build` retains the
actual link map, debug information, source snapshots, local inputs, control
outputs and hashes under `build/us-v1.5/`. The assembler and linker are built
from the checksum-pinned cc65 V2.19 release; V2.19 reports itself as V2.18 with
the release's Git build ID, as documented upstream.

Each accepted source-change control retains its mutated source and candidate
ROM; the control's reproducible object, listing, map and debug intermediates
are retired after its byte check. This keeps the previous full proof intact
until its replacement passes while avoiding a second multi-gigabyte set of
intermediate files. The primary build's map, listing and debug data are retained.

The repository retains the Sims project's MIT licence, AI disclosure,
owner-run contribution policy and strict matching standard. The GitHub
repository was created private on 2026-10-27, with issues, discussions, projects
and wiki disabled.
