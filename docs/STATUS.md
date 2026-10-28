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
of source code and 21,912 bytes of structured data across the physical PRG banks.
It still includes 22,150 local PRG bytes and 65,536 local CHR bytes. A total of
1,619 independent source-change controls verify every listed reconstructed region.
Passing input audits or whole-ROM equality alone is not reconstruction
completion. The developer identifies BOGUS as the
state-machine engine in the [Vance Kozik interview](https://www.nesworld.com/kozik.php);
the original source language and toolchain remain unestablished.

## v1.5 opening-gameplay evidence

`make verify-gameplay` runs 6,740 NTSC frames each for Noah, Moses and David,
plus a separate Noah inventory scenario,
in pinned MesenCE 2.2.1, with zeroed power-on RAM and fixed mapper/alignment
settings. It compares the audited reference and verified build under the same
menu and movement inputs. All three reached their opening areas and showed a
change in scroll and screenshot after rightward input. The Moses sequence also
presses B to lift the baby, jumps past the first approaching enemy and crosses
the first water gap. It recovers him after a later collision, backtracks over the
position trigger, completes the first two levels and enters level three. There,
it picks Moses up after a series of jumps and carries him through further jumps
and movement to the upper platforms. Sampled slot fields show the link, its loss,
recovery and carried finish; pinned screenshot hashes check both success screens.
In David's opening, the verifier pairs native position-event writes for slot
descriptor `$6E` with mode-zero loads of encoded record `$6365`. It also pairs
controller requests for descriptor `$01` with their record loads: the Moses
sequence records 38 `$24` and four `$2D` matches, and the Noah inventory
scenario records one configured `$36` match, with no mismatches. The sixty-four
sampled frames, slot fields, state and cycle counts, mapper-write streams, NMI counts, OAM DMA and
APU-register write streams agreed between the reference and build. Both PRG
banks appeared in the emulator's mapper-write mapping; every observed write
value equalled the mapped ROM byte. This describes the emulator model and the
tested paths, not physical board behaviour or proof of timing on hardware.

End-of-frame samples of the first controller slot also observe descriptor `$09` during the
Moses and inventory scenarios: 354 and 1,088 samples respectively have event
flags and configured action `$FF`, with no other sampled values. This does not
establish its state under other inputs or guarantee that it cannot receive an
action between samples.

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
The later 6,740-frame Moses reference trace records 748 script pointer/bank
pairs and 49 record pointer/bank/mode combinations. Under the recorded emulator
bank selection, their fixed-length command extents cover 2,147 source-owned
physical bytes, and fields selected by the record loader cover 280 source-owned
bytes. It also traces the actual `$95` and `$B1` inline lookup fetches; the
sampled `$95` fetches cover 180 source-owned physical bytes, including
terminator lookahead. No `$B1` fetch was observed. No native instruction starts
were observed in local PRG gaps. The check does not account for every byte in
the loader's ten-byte fetch, and it does not establish unobserved paths or
physical cartridge mapping. `make trace-runtime-extents` captures the route;
`make runtime-extents` checks its current trace against the matching source map.
The later second-level crossing trace observed 708 distinct script pointer/bank
pairs, all beginning in source-owned regions, and no native instruction starts
in local PRG gaps. The slot-record loader read `$36E5` in mode `$02`; a
post-switch mapping check confirmed PRG bank 1 for that fetch, among 327 checked
fetches without a mismatch. The resource pointer and five fields actually read
at `$B6E5` and `$B6E9` are now source, with separate source-mutation controls.
The two intervening bytes and pointed-to sprite remain local. This is evidence
for the exercised emulator route, not proof of all uses or physical hardware.
The trace files remain in ignored `analysis/us-v1.5/`.
A reference-only third-level sweep branched from frame 6,340 into 162 input
sequences. Several kept Moses carried at frame 6,500, but an 81-sequence
follow-up from a farther-right position did not keep him carried through frame
6,740. A second route kept him carried at frame 6,740 on the upper platforms;
that route is included in the maintained reference/build comparison. The local
exploration scripts and results remain in `analysis/us-v1.5/stage3-early-branch.*`,
`analysis/us-v1.5/stage3-farther-branch.*` and `analysis/us-v1.5/stage3-left-branch.*`.
A further 81-sequence reference-only sweep from frame 6,740 kept Moses carried
in 60 cases at frame 6,980, but none ended as high as the earlier checkpoint.
A finer 243-sequence sweep kept him carried in 207 cases at frame 6,900;
none ended as high as frame 6,740. The attempts remain local in
`analysis/us-v1.5/stage3-upper-sweep.*` and `stage3-upper-fine.*`.
Two further reference-only sweeps tried 143 short left/jump combinations and
242 combinations including upward input. All ended at world Y 352 while still
carrying Moses, rather than retaining the upper-platform height. Their scripts
and results remain in `analysis/us-v1.5/stage3-targeted-jump.*` and
`analysis/us-v1.5/stage3-ladder-sweep.*`.
A separate 243-case steering sweep from frame 6,500 found 59 carried positions
at frame 6,660; a 243-case continuation from one of them did not retain Moses
through frame 6,820. Those attempts remain local in
`analysis/us-v1.5/stage3-platform-brake.*` and `stage3-brake-second.*`.
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
4. Complete the reviewed source and data inventory for v1.5, then repeat the
   reconstruction and acceptance for each remaining version in the recorded
   order. Preserve useful gameplay checks; use further runtime investigation
   to resolve specific source, data-format or mapping uncertainties.

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
points at `$FFFF`; its fetch wraps into CPU RAM and remains unclassified.
Resource payloads remain local, and pointer roles and execution require runtime
confirmation.
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
and layout dimensions are source; map grids and chunk contents remain local.
Runtime bounds on either table have not been established.
`make prg-inventory` combines the current verified source map with candidate
map, descriptor-context, native-event and direct-target scripts and records, palette setup,
candidate audio and PPU-stream uses, round-tripped packed text, and optional
validated audio and sprite traces. It counts physical bytes once while
retaining overlapping uses. With the current local traces, 757 PRG bytes have no use
in these inventories; that number is not a count of remaining code. The report
also retains 7,633 possible map/script overlap bytes and 864 possible record/script
overlap bytes across the combined inventories. The expanded field-setter walk
introduces many speculative competing decodes; it does not establish their
reachability. It also reports 8,065 source-owned bytes covered by candidate
data uses, which can include compatible uses as well as competing ones. The
report records its input identities and writes metadata only to
ignored `analysis/us-v1.5/prg-inventory.json`.
`make audio-flow` follows literal voice starts in reconstructed commands and the
native opcode-$18 start. It models both loop outcomes, stops at voice-stop
commands and follows the restore-to-start-plus-one path. The current static
walk has 52 starts, 1,303 command contexts and 1,677 distinct physical bytes,
with no conflicting decodes or five-byte fetches crossing a bank. All 706 bytes
used by the existing audio trace also occur in these candidate paths.
Indexed or otherwise dynamic starts and unobserved playback remain open; the
candidate audio payloads were still local at this checkpoint.
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
one address, referenced five times, wraps from the cartridge window into RAM.
The inspected records yield 71 distinct candidate script entries whose first
command lengths are valid. Bank mapping is a static inference and the tool does not follow
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
possible successor. A potential record/script conflict at `$D57C-$D580` was left local at that
checkpoint; its descriptor association is unverified.
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

Forty-two additional compact negative-mode records represent 126 bytes. The
candidate loader reads a resource pointer and a flag byte for each; it does not
install a script pointer in that mode. Their descriptor and script associations
are provisional and the extents were checked for competing candidate uses.

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
complete streams or establish audio playback correctness. The observed audio
payloads were local at this checkpoint. `make trace-audio` reproduces the
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

A reference-only v1.5 exploratory run used inputs adapted from
[DrD2k9's v1.3 tool-assisted recording](https://tasvideos.org/5223S); see its
[attribution notice](../licenses/tasvideos-5223.md). The input stream did not
reproduce the published run in MesenCE. During its first 20,000 frames, the
loader entered zero-mode record `$5B1B` eight times with bank byte `$0D`.
The resource high-byte sentinel and script pointer at bank 1 `$DB1C-$DB1E`
are source, with the latter resolving to the existing `$E764` script. The
record's uninspected neighbours remain local. A static candidate graph also
interprets `$DB1D-$DB1E` as a script command, reached through a path that has
not been established as executable; this observation establishes the record
use, not that the competing interpretation is impossible. The same trace saw
1,019 script-pointer/bank pairs and 86 record-pointer/bank/mode combinations;
all sampled script instruction extents were already source, and the record
fragment was the only sampled used extent still local. No native instruction
entry in a local gap was observed. These counts describe this emulator input,
not a complete execution inventory or a completed gameplay run.

A direct replay of the v1.3 recording on each local v1.3 and v1.5 reference
did not finish the recorded route. A 20-frame input delay selected Noah on
v1.3, but the run remained in that adventure at frame 20,000. A separate
243-case continuation of the best third-level Moses checkpoint lost the
carried baby in every case by its final checkpoint. These are failed route
experiments, not gameplay verification.

A checkpoint search from the existing third-level route explored short movement
and jump sequences while requiring the baby to remain linked. A selected path
was replayed from power-on on the v1.5 reference and build. At frame 7,020 it
reaches world x=281, compared with x=143 at frame 6,740, with the player and
baby still linked. The permanent verifier now checks intermediate and final
carried states and rightward movement, along with the existing screenshot and
hardware-event comparisons. The carried sprite trails the player horizontally
by four pixels at frame 6,780; the assertion allows that observed offset.
This checkpoint does not complete the level. Search branches that continued
farther descended toward the water, and no successful continuation was found.
The refreshed reference-only interpreter trace through frame 7,020 sampled
58,401 script fetches, 632 record loads and 47,266 inline lookup fetches. All
sampled command extents, consumed record fields and inline bytes were already
source-owned; no native instruction entry in a local gap was observed. This is
coverage of the selected route, not proof of a complete inventory.

The gameplay comparison now retains direct `$2000`–`$2007` write events with the CPU
cycle, PPU scanline and dot, register value and rendering-enabled state. The
individual `$2004` writes generated by OAM DMA are excluded; the DMA trigger
is checked separately. In a reference-only Moses probe through frame 7,020,
all observed `$2007` data writes occurred with background and sprite rendering
both disabled. The same probe saw 6,843 `$2000` writes during visible scanlines
with rendering enabled. A separate PC probe attributed 6,834 of those callbacks
to the return point after `EnablePpuNmi`'s write, three to `RestorePpuCtrl`,
and six to `FadeOutPalettes`. The probes are in ignored local analysis. These
measurements use MesenCE's callback state and do not establish physical PPU
timing or prove unobserved paths safe.

The momentum-aware third-level search retained states with different velocities
and flags, but all surviving branches from the tested frame-6,900 checkpoint
were eliminated by its carry and height filters after 110 simulated frames. This is a
search failure, not proof that the level cannot be completed.
The successful reference/build comparison recorded 83,159, 139,322, 78,517
and 84,312 timed PPU events in the Noah, Moses, David and inventory scenarios,
respectively. None of those scenarios recorded a visible-scanline `$2007`
write while rendering was enabled. These are sampled emulator results only.

The NES serial input order and the `ROL $038F` loop place Right, Left, Down,
Up, Start, Select, B and A in bits 0 through 7 of `$038D`. A reference/build
probe held each button separately and observed the expected eight masks. It
also found that dispatch gates on `changed AND held` but then rotates the
unmasked changed byte: releasing A as B is pressed invokes both action entry
points, as does releasing B as A is pressed. The matching engine preserves
this original behavior and its source comment labels the quirk. The
`make verify-controller` command repeats these checks in the pinned emulator;
they do not establish the timing of a physical controller.

The attributed long reference-only exploratory input described above was
extended to 65,810 frames. It sampled 484,780 script fetches and 6,566 record
loads, with no unowned native instruction entries, script extents or consumed
record fields in this run. It does not reproduce the original movie or finish
Noah's adventure, and does not establish complete reachability.

An alternate third-level route branches from frame 6,500 and uses jump and
upward inputs to reach the roof. Reference and build replays landed on the roof
with Moses still linked, then carried him right to world x=617 by frame 7,100.
A separate `moses-roof` gameplay scenario retains the previous platform route
and checks this route's roof height, later distance, carried slot and identical
reference/build evidence. Straight rightward input beyond that point loses the
baby near the descending stairs, so this is not a third-level completion.
A failed intermediate comparison also exposed that failure retention did not
accept the PPU event stream added earlier. The retention path now saves that
stream for both sides, with a synthetic mismatch test; the failed comparison
remains local for investigation.
A separate reference-only probe of the roof and first stair continuation
through frame 7,220 sampled 61,026 script fetches and 700 record loads. Their
fixed command extents and consumed record fields were already source-owned;
no native instruction entry in a local gap was observed. This probe did not
trace inline lookup payloads and is not an inventory of later levels.
The maintained Moses trace was also refreshed after adding the second route.
Through frame 7,100 it observed 59,261 script fetches, 643 record loads and
47,928 inline lookups, with no sampled extents in local gaps.

The roof branch has been extended through a deterministic sequence of jumps
and pickup actions to frame 7,400. Both reference and build replays carried the
baby to world x=1,295, past the midpoint of the third-level layout. The updated
scenario retains both the earlier route and this later checkpoint; it does not
complete the level. A reference-only trace of this branch sampled 63,362
script fetches and 725 record loads, with no unowned command extents, consumed
record fields or native instruction starts. Inline lookup payloads were not
included in that particular trace.
The maintained lower-route trace was refreshed through frame 7,400 as well:
it observed 60,596 script fetches, 668 record loads and 48,974 inline lookups,
with no sampled extents in local gaps.

The roof route now reaches the end of the third Moses level. An independent
reference-only link probe observed the player and baby linked at every end of
frame from 7,800 through 7,945; the success state began at frame 7,946. The
reference and build replays both showed the success screen at frame 8,000 and
entered the fourth level by frame 8,100. Releasing the controls on that level's
entry leaves the player and baby at their spawn points at frame 8,200. The
permanent scenario checks the carried link through the transition, the success
screen and the new level's spawn, in addition to reference/build event and
screenshot comparisons. It does not complete the fourth level.
A reference-only interpreter probe through frame 8,200 sampled 71,491 script
fetches and 845 record loads, with no sampled unowned command extents,
consumed record fields or native instruction starts. Inline lookup payloads
were not included in that probe. These samples are not a complete inventory.
The maintained lower-route trace through frame 8,200 observed 64,243 script
fetches, 736 record loads and 51,851 inline lookups. All sampled command,
record and inline extents were source-owned, and no native instruction starts
were observed in local gaps.
A fourth-level pickup search found an input that linked the baby to the player
by frame 8,280. Reference and build power-on replays matched at the sampled
frames, but the route reached state 17 by frame 8,600 after the player fell.
This is a failed continuation, not a fourth-level gameplay completion.

The candidate opcode-$89 script at bank 1 `$B27B` points to encoded address
`$332E`. When its alternate mapping selects bank 1, the interpreter reads
seven-byte indexed entries beginning at CPU `$B32E`. The four entries before
the next known script at `$B34A` are now structured as a state selector, two
vertical bytes and two little-endian horizontal values. Their exact gameplay
roles, bank selection at this call site and valid index range remain unverified;
the adjacent script does not prove a four-entry runtime bound. The previous
physical-use inventory showed no competing category for these 28 bytes. The
updated source matches the reference, and a coordinate mutation fails the
whole-ROM comparison.

A reference-only trace through the fourth-level pickup attempt sampled 75,057
script fetches and 866 record loads. Its separately paired bank check found no
mapping disagreements at any of those sampled fetches, all of which mapped to
physical PRG bank 1. All sampled command extents and consumed record fields
were already source-owned, and no native instruction starts in local gaps were
observed. Inline lookup payloads were not traced in this probe. It is not a
complete execution inventory.
A wider fourth-level checkpoint search found a different pickup and jump
sequence. Separate power-on reference and build replays agreed at the sampled
frames: the baby was linked by frame 8,280, and at frame 8,500 the player was
at world x=305 with the baby still linked. These are discrete samples, not a
continuous carry check. With neutral input after the selected sequence, a later
sample at frame 8,600 showed the player falling; this route is not a completed
fourth level. The local search and replay evidence remain under `analysis/`.

A longer fourth-level route was replayed from power-on on both the reference
and build. The maintained reference/build comparison observed the baby linked for all 733
end-of-frame samples from frame 8,268 through 9,000; at the final sample the
player was at world x=854. All five scenarios matched their synchronous frame
pixels and recorded hardware events. This is not a completed fourth level.
The maintained lower-route trace was also refreshed through frame 9,000. It
sampled 67,784 script fetches, 807 record loads and 54,583 inline lookups; all
sampled command, record and inline bytes were source-owned, and no native
instruction start in a local gap was observed.

A gameplay comparison retained a mismatch at frame 3,900 even though its state
and hardware-event streams matched. The differing PNG matched frames 3,898 and
3,899 in a focused reference replay, and four repeated reference/build roof
runs agreed at all sampled frames. In the pinned MesenCE revision,
[`takeScreenshot`](https://github.com/nesdev-org/MesenCE/blob/20ba206cef5ba207c21203176d02cb9f43dda9fb/Core/Debugger/LuaApi.cpp)
uses the video decoder, which has a
[separate decode thread](https://github.com/nesdev-org/MesenCE/blob/20ba206cef5ba207c21203176d02cb9f43dda9fb/Core/Shared/Video/VideoDecoder.cpp).
The verifier now compares canonical run-length encodings of the complete
synchronous `getScreenBuffer` pixels at every sampled frame. PNG screenshots
remain visual observations: differing reference and build PNGs are recorded
and retained rather than used as a substitute for the pixel comparison. Static
success-screen checks still require their pinned screenshots. This evidence is
from the pinned emulator and does not establish physical PPU behavior.
A separate continuation search from the frame-9,000 checkpoint produced a
reference/build power-on replay with the baby linked at world x=1,081 at frame
9,200. Later samples showed the player falling, so the maintained scenario
ends at the earlier 9,000-frame checkpoint; the continuation remains local
exploratory evidence.

Two indexed audio-control tables at bank 1 `$A6D0-$A6F3` now express ten
voice-4 pointers and two four-voice pointer records as source. In directed
reference-only Noah and David runs, the `$B3` handler fetched table indices
0, 2 and 8, and the `$78` handler fetched both four-voice records. The probe
paired all 168 observed accesses with their mapped physical addresses and
found no bank disagreements. The unobserved entries are static candidates;
the instruction behavior does not establish a runtime index bound. The
individual audio payloads remain local. Each source table has a separate
changed-source control. The local probe scripts, observations and input hashes
remain under `analysis/`.

Additional fourth-level route searches were replayed from power-on on the
reference and matching build. The sampled state and screenshots agreed through
frame 10,200. The baby was linked at world x=1,539 at frame 9,800 and at
world x=1,802 at frame 10,100; a later sample at frame 10,200 showed the link
lost. These are discrete samples from exploratory routes, not continuous-link
verification or a completed level. The maintained scenario still checks the
previous frame-9,000 checkpoint.

A fourth-level route was replayed from power-on on both ROMs. The baby stayed
linked in all 2,178 end-of-frame samples from frame 8,268 through 10,445;
the success state began at frame 10,446. Seven samples found the player slot
temporarily marked `$FF`; a focused write trace paired each with the existing
`SlotRecordAllocate` clear and restore path. The maintained check verifies
those writes and the separate main-state reset, requires the success screen,
and presses A to reach the fifth-level spawn. The fourth-level path, its
transient observations and the new spawn are emulator evidence, not proof of
all game paths or cartridge behavior.

An alternate fourth-level exit and fifth-level opening observed the slot loader
consume a three-byte compact record at bank 1 `$D581` in mode `$FF`. A mapper
probe paired 98,466 script fetches and 1,192 record loads with physical bank 1
without a mapping disagreement. The record is now structured source; the five
preceding bytes at `$D57C`–`$D580` retain competing interpretations, now
represented together as described below. The observation does not establish
the meaning of the resource pointer.

At the fifth-level spawn, a further route picks up the baby at frame 10,786
and keeps its slot linked through frame 11,150, reaching world x=364. Both ROMs
matched in an independent continuous-link probe. Four one-frame player-slot
transients were paired with the same record-loader clear and restore writes;
the maintained scenario checks those writes and the uninterrupted baby link.
The five-scenario reference/build comparison passed with this extension. The
then-current reference-only runtime trace observed 77,869 script fetches, 997
record loads and 62,601 inline reads without finding sampled local extents.
That collector selected the lower Moses route, not this fifth-level route.

The observed audio commands at bank 1 `$AB10`–`$AC3F` are now structured
source: 45 delays, 42 five-register commands and one loop. All 88 command
starts were observed in the Noah, Moses and David reference runs, and the
current PRG inventory found no competing use for those 304 bytes. The loop
target is the observed command at `$AC10`. `$F9` retains the original stale
fifth stack byte behavior; its source representation has four payload values.
This is a partial stream and does not establish audio playback correctness or
the bounds of neighboring streams.

A further 167 observed audio commands occupy 14 partial regions totaling 362
bytes in bank 1 `$A6F4`–`$AC9D`. Each command was observed in at least one of
the Noah, Moses and David reference traces; 52 were observed in all three.
The current inventory reports no competing use for these selected bytes. The
source records channel selection, notes, instruments, control commands and
loops, while the intervening bytes remain local. Each partial region has its
own changed-source control; this evidence still does not establish complete
stream boundaries or correct sound on hardware.

The static audio walk also finds 294 unobserved candidate commands across
23 currently uncontested regions totaling 430 bytes. Their decoded fields
round-tripped locally at that checkpoint and remained uncredited: the stack-copy routine selects
its physical bank using state-dependent `$03C2`/`$03C3`, and the mapping for
these unobserved paths has not been established. The candidate report and
decoded blocks are retained in ignored local analysis for further investigation.

The longer Moses route through frame 11,650 recorded 3,210 audio fetches on
each ROM with identical mapped addresses and bytes. Among the commands not in
the earlier sweep, 47 occupy four unowned, uncontested regions totaling 57
bytes at bank 1 `$AC58`–`$AC86` and `$B7A3`–`$B7B4`. These commands are now
structured source, with one changed-source control per region. Other newly
observed audio commands overlap candidate script uses and remain local. The
route probe and its reference/build observations are retained in local analysis.
`make trace-audio-route` reproduces these 47 command starts through frame 4,300
using the maintained Moses input and validates the physical-bank reads on both
ROMs. It does not establish all audio paths or cartridge behavior.

An extended fifth-level route was replayed from power-on on both ROMs. The
baby remained linked for 1,115 consecutive end-of-frame samples, from frame
10,786 through 11,900, with the player reaching world x=1,252. The same four
one-frame player-slot transients were observed as in the shorter route. The
maintained comparison now checks this longer carry; it does not yet reach a
fifth-level success screen. A reference-only trace recorded 81,516 script
fetches, 1,064 record loads and 65,536 inline reads without finding sampled
local extents, but selected the lower Moses route rather than this roof route.
The collector has been corrected to select and validate the roof route.
The corrected reference-only roof-route trace reached frame 11,900 and recorded
109,402 script fetches, 1,331 record loads and 80,392 inline reads. It found no
sampled native instruction starts or decoded script, record or inline bytes in
the current local PRG gaps.

An independent Noah pickup route was replayed from power-on on the reference
and matching build. The selected animal stayed linked for 571 consecutive
samples, from frame 1,530 through 2,100, while Noah reached world x=1,004.
Two one-frame player-slot transients were paired with the existing allocator's
clear and restore writes; the maintained comparison checks those writes and
the continuous animal link. This route does not yet verify animal delivery or
completion of a Noah level. A separate power-on reference/build replay kept the
animal linked through frame 3,300 and reached world x=3,054; animal delivery
remains unverified. The maintained check now samples the link through frame
3,300, including the same two verified allocator transients.

The extended Moses replay completed the fifth level on both ROMs. The baby
remained linked for 1,901 consecutive end-of-frame samples, from frame 10,786
through 12,686; the success state began at frame 12,687. Five one-frame player
slot transients were attributed to the existing allocator, and the transition
reset was traced separately. The success screen advanced to a sixth-level
spawn at frame 12,950. An independent reference trace through frame 13,050
recorded 119,818 script fetches and 1,474 record loads without sampled local
script, record or native instruction gaps; it did not trace inline lookups.
The maintained roof-route collector reproduced those counts and captured
86,824 inline lookups without finding sampled local inline bytes.
The sixth-level spawn does not establish completion of that level or adventure.
A reference-only search reached the upper staircase near the baby, but its
bounded beam hit the emulator time limit and a 72-case pickup-timing sweep did
not observe a linked baby. The attempts remain in local analysis and do not
rule out other routes or interaction timings.

The audio bank question was investigated with controlled CPU and RAM inputs in
the pinned emulator. The byte-matched selector routine was exercised for all
128 nonnegative input values with both incoming carry states on each ROM. Its
usual selector values `$00`–`$0F` produce the eight mapper bytes `$0D`–`$7D`;
each mapped a tested audio fetch to physical bank 1. Values with bit `$10` set
index beyond the 16-byte bank-value table. Among the 16 resulting mapper bytes,
`$8D`, `$BD` and `$FD` selected physical bank 0 in the controlled probe due to
the byte present at the write address. The full input range is not claimed to
be reachable in normal gameplay, and this is emulator evidence, not hardware
proof. `make verify-audio-bank` reproduces the checks.

With the normal bank-1 mapping established as a conditional interpretation,
247 further audio commands in 22 uncontested partial regions (373 bytes) are
now structured source. Their bytes and command decoding match the audited ROM,
and each region has its own changed-source control. They remain labelled as
static candidates: execution, stream boundaries and the bank selected in every
possible context are not established. The separately observed 57 bytes were
already accounted for; competing uses remain local.

The static slot-record inventory also supports seven possible contact entries
at `$EEAF`, `$EEC1`, `$EED9`, `$EF1B`, `$EF2D`, `$EF3F` and `$EF75`. Each
associated descriptor has a candidate script path that clears the contact
inhibit bit, and each selected record's script pointer targets `$F00F`. Only
the three bytes actually consulted in zero mode are claimed here; their
execution remains unverified. A candidate direct record at `$AD3C` has been
expressed in its nine-byte layout because the union of its possible loader
modes reads those fields. The negative-mode flag at `$AD1A` and four fields at
`$ED6D`–`$ED70` are also represented from their candidate contexts. Loader mode,
slot identity and whether these candidate paths execute remain separate from
the byte-match proof. Competing record/script interpretations remain open.

Five possible three-byte script jumps at `$EE65`, `$EE7F`, `$EECD`, `$EEE5`
and `$EEFD` coincide with possible negative-mode compact records. They are now
expressed as shared script/record overlays. The possible script/record views at
`$D57C-$D580` and `$B077-$B078` are expressed the same way. Each form asserts
that its two interpretations encode the same bytes; these checks do not prove
that either candidate context executes. Fields outside the asserted extents
retain their existing source or local status. Synthetic assembler checks reject
inconsistent views, and each extent has its own changed-source control.

Twenty-four more bytes in eight extents have two aligned candidate decodes:
individual audio notes and reviewed one-byte BOGUS commands. Their source uses
symbolic script opcodes and asserts that each matches its note encoding. The
selection excluded other catalogued data uses and competing script boundaries.
The audio view is conditional on bank 1, while script descriptor associations
and execution of both views remain unverified. Synthetic assembler tests reject
a disagreement, and every extent has a changed-source control.

The `$33`/`$34` handler review adds possible successor paths to the BOGUS
inventory. The expanded walk includes candidate script entries within existing
candidate audio extents at `$A9BA` and `$AA78`, and alternative entries in the
existing script extent near `$B638`. It also reaches locally supplied data.
These additional paths do not prove either view is used and do not change the
byte-match evidence; their descriptor contexts and overlapping command
boundaries remain unresolved.

Sixty-five further candidate BOGUS commands occupy 177 bytes that also decode
as individual audio notes, across sixteen source extents. The script forms use
reviewed handler macros, while note duration and pitch values are checked
against every command byte. At that checkpoint selection required a unique
candidate script boundary and excluded other catalogued data uses. Both script context and
bank-1 audio execution remain provisional; the assertions establish compatible
encodings, not reachability. Synthetic assembler checks cover the operand
layouts and reject inconsistent notes, and each extent has a separate
changed-source control.

Naming the individual candidate entries broadens the separate direct-target
walk to 1,822 seeds, 7,942 candidate nodes, 25 possible direct commands and
23 distinct direct targets. It now reports 2,784 bytes with overlapping script
decodes and 36 possible record/script overlap bytes. These are conservative
static possibilities, not evidence of execution. The combined PRG inventory's
physical script and record coverage did not expand at that checkpoint. A later
handler review exposes additional script boundaries, as described below.

The `$45` handler compares the supplied value to slot field `$07C0` and can
branch to its supplied pointer or continue. Modelling both possibilities raised
the merged native-event walk to 11,382 nodes. Graph traversal now has a
separate 65,536-node limit, covering the encoded 16-bit address space, and the
inventory rejects incomplete per-context walks as well as incomplete merged
walks. The broader walk finds alternative candidate script boundaries at
`$A9FF/$AA01` and `$AA90/$AA91`, overlapping eight bytes in the previously
represented `$AA00` and `$AA8F` extents. Those bytes still match, but their
script interpretation is no longer unique. No additional catalogued data
category covers the previously selected 177 bytes.

Three additional four-byte script commands at `$AA0B`, `$AA8B` and `$AC82`
are represented alongside their possible audio-note views. The `$38` command
preserves its third operand even though the shared handler does not inspect it.
Candidate contexts and bank selection remain unverified; changed-source
controls and the whole-ROM comparison verify the emitted bytes.

The widened inventory also supports a partial candidate `$DA40` slot record;
its final visual fields overlap the existing record at `$DA46`. The possible
mode-1 flag at `$DB64` is represented separately. Three candidate contact
pointers at `$DA50`, `$E012` and `$E0FE` share their pointer bytes with a
possible two-byte BOGUS command; assembly checks both views. Four adjacent
three-byte script candidates use bytes that resemble fields skipped by the
zero-mode contact loader. Associations and execution remain unverified.

A further candidate command sequence at `$EC20` branches to the existing
`$EC2B` script. Its known static predecessors come from speculative graph paths,
including paths through bytes otherwise represented as native code; no runtime
entry is established. Its command forms and emitted bytes are represented,
but this is weaker evidence than an observed script entry. Each added extent
has a changed-source control.

Two candidate mode-2 slot records at `$E01A` and `$E023` share all nine bytes
with possible BOGUS voice-pointer commands. The source asserts the word layout
of both interpretations. Other possible script starts within those bytes
remain unresolved, including `$E01B`, `$E020` and `$E029`. For candidate record
`$E106`, only the resource pointer and five mode-2 fields are represented;
the intervening two bytes remain local. All three associations are static
candidates, not evidence of execution. The added source has per-extent
changed-source controls and synthetic consistency checks.

The audio inventory now reads voice pointers from the shared audio/script and
record/voice forms as well as direct commands. It validates each overlay's
fields and note encoding before accepting its literal starts. Five additional
starts add 234 candidate audio bytes: 230 overlap existing source around
`$B12C-$B1BE` and `$B835-$B887`, while four at `$CA3F-$CA42` overlap locally
supplied packed-text data. These are conditional static decodes, not evidence
of audio playback or of a particular bank mapping. No additional bytes are
credited as reconstructed source by the inventory change.

A controlled MesenCE probe exercised the `$3F/$24` selector over all 256 slot
field values and both incoming carry states on the reference and matching
build. It returned the high nibble plus twice bit 3, yielding 0-31. A second
probe exercised `$44` over all 256 low-byte values and both carry states; its
8-bit shift discards bit 7 before adding the index to the pointer. The adjacent
`$F432` path therefore permits 32 table positions if the same slot continues
without an intervening write. An independent `$F434` entry may use any of 128
positions, with inputs differing only in bit 7 aliasing the same position.

Under the assumed bank-1 mapping, positions 0-2 are the three represented table
entries, positions 3-11 overlap existing script bytes, and positions 12-127
overlap candidate map layouts. These are possible reads, not evidence that
out-of-range positions execute or that their words are intended script targets.
`make indexed-jump-inventory` repeats the controlled probes and keeps the table
analysis locally. Mapping, slot state and runtime reachability remain separate
uncertainties.

The static script and record walks now follow the 29 additional `$F434`
positions only as predecessor-conditioned candidates, distinct from the three
observed indices. The jump remains incomplete for independent entry. The
merged native-event walk now contains 580 candidate contexts and 858 possible
record/script overlap bytes. Paths introduced by the additional edges depend on
the condition; the merged graph does not retain complete provenance or prove
execution. The observed-index comparison adds 79 candidate script bytes and
303 candidate record-field bytes, with shared roots potentially hiding other
conditional paths. Source aliases and assertions describe the already
known overlapping entries at `$A9FF`, `$AA01`, `$AA90` and `$AA91` without
claiming another physical byte or a unique interpretation.

The remaining local `$F354-$F400` region contains candidate menu text and tile
data; the `$F357` entry is referenced by a BOGUS display command. It remains
local game data rather than reconstructed code. The `$FC87-$FC9E` bytes follow
a `$00` record-load command at `$FC85`, but the known `$FC61` contact context
selects an installable script pointer in its overlapping candidate record, so
that context does not establish a fallthrough to `$FC87`. Other entries or
contexts are not excluded. The zero-filled `$FD6A-$FD87` region is also left
local: zero content alone does not prove padding or exclude another use.

The candidate graph now also follows the reviewed `$3C` field comparison,
eight additional normal-return operations, two possible yields, the `$74`
saved-pointer retry, and the `$57` fallthrough with its dynamic target still
unresolved. The engine saves the script pointer after each dispatched
command at `$DACE`; `$74` restores that saved pointer before yielding. These
additional edges expose competing script and data interpretations, not proven
execution. The unowned, uniquely decoded candidate script extents identified
by this wider walk fall in local map, sprite, palette or menu data, so this
review adds no source ownership.

The wider record walk also identifies a negative-mode compact record at
`$DB63`, reached by candidate `$DB66`/`$E764` contexts. Its resource high byte
is the already-represented mode-1 field of the overlapping `$DB60` record.
At `$E055`, a candidate mode-2 access for descriptor `$E043` reads a resource
pointer and two fields; the following fields have competing candidate script
uses. At `$E087`, the candidate contact record's resource sentinel and script
pointer are represented; its high byte also starts the possible `$E08A`
script command. The same `$E764` path also gives partial negative-mode records at
`$E040` and `$EB10`; their noncompeting resource or mode bytes are represented
and their competing script bytes remain local. These associations are static
candidates, not evidence of execution.

The `$D52B` contact-script candidate can reach the record load at `$D75B`
through reconstructed command edges. Its mode-zero target `$D549` overlaps a
previously represented position sentinel; its `$00FF` resource and script
pointers are retained as provisional interpretations, including the possible
resource use of a region also catalogued as map data. The mode-2 candidate at
`$E090` also supplies its previously local final field.

At `$F156`, the candidate record-load command shares its `$2C` operand with the
dispatch-counter opcode at `$F157`. The source represents the first byte once
and asserts that the following opcode supplies that operand. Under the candidate
`$F00F` interaction path, the five records at `$EEAE`, `$EEC0`, `$EF2C`,
`$EF3E` and `$EF74` inspect resource-high sentinel bytes that are also skipped
low bytes of neighboring contact records. Those bytes are now represented;
neither the paths nor the competing record interpretations are proved to run.

The `$7F` handler's busy path retries from the saved pointer; its other path
fetches a pair using an eight-bit doubled slot value, then can normally return
after setting shared state. The graph now records both possible successors and
the 128 distinct even offsets while leaving the indexed data and bank mapping
unresolved. This adds candidate paths, largely over map data, without adding
source ownership or proving that the paths execute.

The graph's `$B62C`, `$D48F` and `$E71C` index counts are now explicitly
marked as predecessor-conditioned and incomplete for independent entry. The
same table bytes and candidate edges remain in the inventory; this change does
not claim that other targets execute or add source ownership.

The candidate `$F00F` interaction path can also reach the negative-mode load
at `$F009` with descriptor base `$EF48`. Its target `$EF45` is now represented
as a compact record; the `$0000` resource pointer may select map data. The
same interaction path's `$F156` command can read one field each at `$EED9`
and `$EF1B` from candidate records based at `$EED2` and `$EF14`; those bytes
are also skipped low bytes of neighboring contact records. All of these
descriptor/path associations remain static candidates.

`make indexed-jump-inventory` now inventories all 128 distinct read positions
at each of the three predecessor-bounded sites as well as `$F434`. Outside the
predecessor ranges, 5 of 117 reads at `$B62C` and 36 of 124 at `$D48F` touch
locally included bytes; all 120 at `$E71C` read source-owned bytes. Under the
candidate encoded-bank mapping, some resulting words point into native source,
script/data source or local regions. These are possible indexed reads and
candidate targets, not evidence that independent entries or targets execute.

The candidate `$D52B`/`$D912` context can reach a mode-zero record load at
`$D928`, selecting the nine-byte record at `$D558`. Those bytes also contain
candidate script entries at `$D559`, `$D55C` and `$D55F`; a candidate branch
starting at `$D555` uses the record's first byte as an operand. The source now
emits the record once and checks the shared opcode and operand relationships.
The surrounding script bytes remain local, and neither interpretation is
established as executed.

The candidate contact record at `$E087` points to `$E764`. Its encoded
pointer's high byte is also the opcode of the candidate command at `$E08A`;
the source asserts this shared byte and emits it once. The contact and script
entries remain independent possibilities, not observed execution.

The candidate mode-2 records at `$E090` and `$E099` also begin with possible
branch opcodes. Their prefixes now preserve both interpretations, including
the otherwise skipped pointer bytes used by the candidate branches. The
record modes, script entries and resulting branch targets remain unverified.

The `$DC23` contact record and candidate `$DC26` command share a pointer-high
byte in the same way as `$E087`/`$E08A`. At `$EB00` and `$EBAD`, candidate
pair-bit commands begin on resource-pointer high bytes and use the otherwise
skipped script-pointer bytes as operands. The source asserts these shared
opcodes and leaves execution and descriptor associations provisional.
The incomplete temporary proof from the smaller interrupted batch was retired
after the larger matching build and its controls completed. The final controls
cover the affected regions from that earlier preflight.

The candidate `$B900` descriptor script can select the mode-2 record at
`$B8F7`; its otherwise skipped pointer bytes also supply operands to the
possible `$B8F6` branch. The source now represents that record and the shared
opcodes in the preceding descriptor. The mode-2 fields at `$E05B-$E05D`
also overlap possible record-load commands.

The candidate `$E764` path identifies negative-mode compact records at
`$E002`, `$E005`, `$E03D`, `$E078`, `$E07B`, `$E0B3`, `$E0B6`, `$E0EE`,
`$E0F1` and `$EB0D`. Their bytes also participate in possible BOGUS commands,
including the voice command at `$E002` and the add-fields command at `$EB0D`.
The source emits each physical byte once and asserts shared opcodes; record
associations, candidate commands and their execution remain provisional.
The record low byte at `$E040` remains local. This replaces 42 local PRG
bytes with structured source and does not establish original names or prove
which overlapping interpretations execute.

The audio/script overlap review now represents 104 further bytes at `$A790`,
`$A7AF-$A7B2`, `$A823-$A82B`, `$A8C5-$A8D0`, `$A8FF-$A90C`,
`$A91F-$A934`, `$AA27-$AA34`, `$AA64-$AA6A`, `$AA85-$AA8A`,
`$AB0B-$AB0F` and `$AC40-$AC48`. The source describes audio register
writes, notes, loop and delay forms as well as candidate BOGUS entries that
share their opcodes or operands. The branches at `$AA27-$AA34` have several
competing entries, expressed as aliases and checked opcode relationships.
The audio at `$A823-$A82B`, `$AA64-$AA67`, `$AB0B-$AB0F` and
`$AC40-$AC48` was present in the retained emulator audio observations; those
observations do not establish the candidate BOGUS execution, physical board
mapping or unobserved audio paths. The other audio and script views are static
candidates. The first three bytes of the audio command at `$A78D` were initially left local;
they are now represented as described below.

The 73 bytes at bank-0 `$FD3F-$FD87`, between the controller mode gate and
the shared native-call wrapper, are all zero in the pinned v1.5 reference.
There is no established use or padding boundary for that span; it remains a
local inclusion and is not credited as code or structured data.

The candidate `$B082` direct record load can inspect the `$B077` record's
script-pointer sentinel and mode-selected fields. The sentinel and the next
five fields are now represented. `$B079` is skipped as a script-pointer low
byte in zero mode, but a negative mode can inspect the same byte as a record
flag; a possible `$B072` voice command also uses it as an operand. Its source
representation retains both candidate views. Candidate commands at `$B07B` and
`$B07E` share the following fields. The
candidate `$AF00`, `$D228` and `$D555` paths now describe branches whose
opcodes or operands overlap a neighboring command, contact pointer or record.
The `$DA56`, `$DB22`, `$E018` and overlapping `$E104`/`$E105` entries continue
existing candidate script decodes. These paths and record modes remain static
possibilities, not execution evidence.

Further overlapping audio and script commands are represented at `$A9B9`,
`$A9F2-$A9F5`, `$AA77`, `$AA9E-$AAAE` and `$AAD4-$AAD7`. Mixed note, restore,
channel and instrument forms now check the shared branch fields. The existing
audio observations cover `$AAA3-$AAAE`; they do not establish the candidate
script paths. The current static audio graph covers 1,677 unique PRG bytes,
of which 1,673 are source-owned. The four remaining local bytes are the possible
audio sequence at `$CA3F-$CA42`, which overlaps packed-text payload. This is not
an inventory of every possible audio stream.

The chunk-offset table contains aligned offsets for 145 distinct slots between
zero and its largest referenced offset, leaving slot 22 at bank-1
`$85D8-$861B` unreferenced by that table. The inventory now records this
68-byte interval separately as a possible unreferenced map slot. It overlaps
49 bytes in the candidate script graph; both labels are retained, and the span
remains local. Alignment alone does not establish that it is map data, padding,
or executable script, and independent or out-of-range indexing remains open.

The 19 candidate inventory PPU streams now have their 32 absolute-address
commands, 26 relative-address commands and 19 terminators in structured source.
These 193 physical control bytes are emitted independently of the 236 local
tile/text payload bytes. The refreshed PRG inventory confirms all 193 control
bytes are source-owned and none of these payload bytes are. Candidate BOGUS
entries that overlap the controls remain labelled, and shared opcode bytes are
checked where their positions are known. The PPU stream inventory distinguishes control and payload extents
without exporting their contents; it retains overlaps if different stream
entries interpret the same byte differently. The logical stream layout does not
establish queue timing, runtime reachability or physical cartridge mapping.

The two-byte dimensions of all 14 identified map layouts are now structured
source. The inventory counts all 28 header bytes as source-owned and all
2,131 chunk-index grid bytes as local game data. The earlier map trace
observed headers at `$A302`, `$A32A`, `$F44D`, `$F625` and `$F965` under the
recorded emulator mapping; the other layout selections remain static
candidates. Four bank-0 headers also have possible sprite-frame reads, and
several headers have candidate BOGUS interpretations. At `$F44D` the same
bytes can additionally form an indexed-jump entry and a mode-zero record field.
The source retains these alternative views without asserting they execute.

All 52 known packed-text records now represent their two-byte PPU destinations
as structured source. The native decoder places those bytes after an absolute
PPU command; the inventory counts all 104 destination bytes as source-owned
and all 3,873 compressed message bytes as local. Some destinations
also overlap candidate BOGUS commands or inline lookup cases, which are
labelled separately. Static table coverage and matching bytes do not establish
message reachability or the runtime bounds of the selecting index.

The candidate audio write at `$A78D` is now represented by its three-byte
prefix and the two operands shared with the candidate BOGUS record load at
`$A790`. The shared opcode is asserted in source and both regions have their
own changed-source controls. The two decodes are static candidates; their
execution, active bank and higher-level purpose remain unverified. The four
candidate audio bytes at `$CA3F-$CA42` still overlap local packed-text payload.

The six previously numeric native calls now use source labels. Twenty-one
candidate BOGUS calls also name `FadeOutPalettes` instead of its encoded
`$B51B` operand; the label identifies the bank-0 address under the candidate
mapping, while reachability and active bank remain separate questions. `make
native-control-flow` checks source-associated debug spans against the retained
matching build and inventories direct branches, calls and jumps by physical bank.
It covers all 21,474 source-owned native bytes and finds 2,237 direct transfers.
Two shared-tail transfers in physical bank 1 have same-bank targets in local bytes;
their bank-0 address alternatives are source-owned. Bank switches precede these
transfers, but this static scan does not establish the active bank or physical board
mapping. No other inventoried same-bank direct target is outside source-owned code, and all
such code targets have a debug span boundary. Span boundaries do not prove
runtime reachability or instruction boundaries. The 197 nominal BOGUS dispatch
entries now refer to named handlers rather than numeric addresses. Their 183
unique bank-0 target addresses are all source-owned debug span starts; the
scanner also records the alternative bank-1 classifications. The length tables
match in both banks, but runtime index bounds and active mapping remain
unestablished. Other returns, interrupt vectors and computed or dynamically
constructed transfers require separate review.

Source comments now name the reconstructed map row, audio, deferred PPU and
division helpers. Their higher-level semantics and runtime coverage remain
provisional; matching bytes alone do not validate those interpretations.

The 145 table-referenced map chunks can now be exported to an ignored local
file with `make extract-map-chunks`. Each is represented as eight tile rows and
two attribute rows; the unreferenced slot 22 remains opaque. The encoder checks
the audited reference identity, reviewed table geometry, slot types and row
dimensions. The v1.5 assembler consumes the encoded local file when present,
or generates the same local input from the reference when it is absent. A
retained asset control changes one tile in an isolated copy before assembly;
the full ROM comparison observes exactly that physical byte changing. Editing
the local asset or its retained evidence invalidates progress until the build
is reverified. Neither the decoded assets nor the opaque slot are credited as
source; possible overlapping script uses and mapper assumptions remain open.

The map query and scroll implementation now uses 16 named RAM symbols in
274 instruction operands. The names describe the observed coordinate, width,
scroll target, current scroll and work-state uses; shared scratch use and
higher-level roles remain provisional. Sixteen retained include-file controls
independently change each symbol and verify the resulting physical operands
within reconstructed code. The expected operand counts are reviewed alongside
the source and must be updated if later reconstruction adds a use. These names
replace numeric addresses in already-owned code and do not add PRG coverage.

A direct-record script walk also finds ten unreviewed possible `$9B` native
calls beyond the two established forms. Their entry bytes are in local regions or inside existing native
instructions. They are candidate
overlapping decodes, not evidence of additional reachable native calls; their
active bank and target interpretation remain open. The candidate addresses and
both physical-bank alternatives remain in ignored local analysis at
`analysis/us-v1.5/native-script-call-candidates.json`.

The candidate state-change command at `$F408` saves its advanced pointer at
`$F40A`. If the state transition retains the slot and later resumes it, those
six bytes decode as three commands. The `$F40A` and `$F40D` entries also have
possible negative-mode compact-record interpretations; `$F40D` can additionally
start a candidate OR command whose operand overlaps the next state command.
The source emits these bytes once and asserts the shared opcode relationships.
Slot retention, record contexts, bank mapping and execution remain unverified.
The neighboring all-zero `$FD6A` continuation remains local and unclassified.

The 14 identified map layout grids can now be exported to ignored local storage
with `make extract-map-layouts`. Their 2,131 grid bytes are encoded into the
local gap inputs, while the already-owned dimension headers remain in source.
A retained control edits one cell in each layout before assembly and verifies
exactly the corresponding 14 physical ROM bytes change. Local grid data is not
counted as source; possible script and record overlaps are preserved rather than resolved by this format.

The refreshed descriptor-rooted walk has 691 candidate record accesses and no
unowned bytes among the fields those selected modes inspect. It has no pending
contexts, but it does not exhaust native-event contexts, dynamic entries or
unbounded indices. In the broader inventory, 19 local bytes have only a
candidate-record label; that absence of other labels does not establish their
use or make them code. The metadata-only comparison is retained locally at
`analysis/us-v1.5/descriptor-record-ownership-review.json`.

All 52 known packed messages can now be exported to ignored local storage with
`make extract-packed-text`. The editable text retains each original one- or
two-symbol encoding slot and the original padding; character edits must fit the
same slot width and preserve the record length. The source-owned PPU destination
headers remain separate. A retained control changes one character in each
record before assembly and checks all 52 physical payload changes against the
fixed reference. Text remains an extracted asset and receives no source credit;
possible audio, script and record overlaps remain unresolved, and decoding does
not establish message reachability or intended presentation.

A source-span review of the combined candidate graph finds 184 local physical
bytes labelled only as possible script by the current inventory. Twelve
fully covered candidate starts have a source-owned graph predecessor; the 25
incoming edges examined do not start at a debug span associated with a declared
BOGUS source command. Some instead decode native instructions or other data.
This is a bounded static classification, not proof that the candidates are
unreachable or that the inventory finds every asset use. The reviewed addresses,
source associations and proof identity remain in ignored
`analysis/us-v1.5/exclusive-script-candidates.json`.

The four bytes at bank 1 `$CA3F-$CA42` are now expressed as candidate audio
commands while retaining their overlapping packed-text interpretation. The
candidate pointer comes from an already represented possible BOGUS voice
command; neither that path nor audio playback is established. The final restore
command uses the `$E6` encoding, whose low bits the dispatcher ignores; it is
not the canonical `$E4` encoding. The build checks the local text against the
source-owned overlap, and its text control changes the first and last primary
characters in each record to exercise all 53 local text gaps. Conflicting
edits to the shared bytes are rejected. Each of the four source bytes has an
independent changed-source control.

The default and secondary mapper value/index fields now have provisional RAM
names and independent operand-change controls, alongside the existing NMI save
fields. `ConfigureBanksFromValue` produces an even default value and an even
index from zero through 30. Indices above 15 address bytes beyond `BankValues`; two
of those ROM bytes differ between the physical banks. On both the reference and
matching build, a controlled MesenCE probe tested every selector byte with both
incoming carry states and applied each default write from both PRG banks: all
1,024 writes per ROM selected PRG bank 0. This observation is specific to the
emulator's mapper model and those controlled producer values. It does not
establish physical cartridge wiring, CHR mapping, arbitrary RAM values, or
execution of the NMI path. In particular, startup clears the default value but does not by itself
prove the index is initialized before every possible interrupt.

The shared record-fetch pointer, slot-record mode and first five record-buffer
bytes now have provisional zero-page names in 392 physical instruction
operands. These locations also serve arithmetic and general scratch uses; the
names do not imply exclusive ownership by the script engine. Independent
include-file controls check each symbol's changed bytes, including instructions
whose original absolute addressing must remain three bytes. This improves
readability of already-owned source without claiming additional PRG bytes.

`make native-script-calls` now inventories candidate BOGUS `$9B` calls from
the source-labelled script graph, calculating the CPU destination from the
actual OR, stack and RTS sequence and classifying both physical-bank targets.
At this checkpoint it finds 35 candidates: 24 encode the address of the reviewed
bank-0 palette fade, one encodes the bank-1 text decoder's address, and ten have
unreviewed targets. The actual selected bank remains unproven. Of the ten, six
candidate command starts are local bytes and four overlap source-owned
native spans without a debug span starting at that byte. The possible target
at `$CA04` remains local in both banks. These counts describe the incomplete
static candidate graph, not reachability, an instruction-boundary proof, a
mapper guarantee, or a complete inventory of dynamically constructed calls.
The metadata and input identities are retained locally in
`analysis/us-v1.5/native-script-calls.json`.

Five v1.5 descriptor entries (`$40`, `$41`, `$46`, `$47`, `$4C`) contain
`$FFFF` as their record pointer. If the caller takes the zero-offset load path,
the reconstructed fetch copies its first byte from CPU `$FFFF` and its next
nine from internal RAM `$0000-$0008`. The field values are therefore dependent
on runtime RAM, not fixed bytes in another PRG bank. The existing crossing
status stays unresolved; the inventory now records the effective-address
segments without decoding the RAM-dependent record.

`make verify-record-boundary` exercises four controlled fetch cases and six
controlled descriptor indices on both the audited ROM and matching build. A
single RAM-byte change affects exactly the corresponding copied byte. The
descriptor probe injects its entry point and bypasses the caller's outer gate;
neither probe establishes gameplay reachability, original cartridge mapping, or
all CPU bus cycles. In particular, the effective-address plan does not model
page-crossing dummy reads. The direct path reaches `SharedReturn`; the secondary
path returns through the mapper-switch helper after restoring the default bank.
The retained verification is local under
`analysis/us-v1.5/record-boundary-verification.json`. Superseded exploratory
replay scripts and their duplicate log were retired after the maintained probe
passed.

For later adaptation, the audited v1.4 input has the same 61 bytes as the v1.5
helper at `$FE6C-$FEA8` in both PRG banks. The 78-byte v1.5 descriptor fragment at
bank 0 `$A086` occurs once in v1.4 bank 0 at `$A070`. These are byte comparisons
only; they do not establish v1.4 callers, mapping or a matching build. The
comparison script and metadata remain under `analysis/us-v1.5/`.

The 132 observed bank-0 sprite frames now have a local editable representation
of their headers and row-ordered tile/attribute pairs. The address manifest
records observed frame starts; it does not assert that the list is complete or
that each asset has no other use. `make extract-sprite-frames` exports the
reference data under ignored `extracted/`, and `make build` consumes the local
file when present. Dimensions, header flags, ordering and bank boundaries must
remain consistent with the reference, while tile and attribute bytes are
editable. A retained build control changes one tile index in each frame and
verifies exactly 132 changed ROM bytes. These are locally supplied graphics
metadata, not additional source ownership; CHR graphics remain separate.

The 132 complete observed frame byte sequences each occur exactly once in the
audited v1.4, v1.3, v1.2 and v1.1 PRG images. Their physical offsets differ
from v1.5 by -22, +615, +618 and +540 bytes respectively, consistently within
each version. None of those complete sequences occurs in the unversioned PRG.
These byte searches do not establish target-version pointers, bank selection,
reachability or builds. The metadata-only comparison is retained locally at
`analysis/us-v1.5/sprite-version-comparison.json`.

Sprite and audio record accesses now use provisional names for the eleven-byte
sprite records and eight-byte voice records. The names reflect fields read by
allocation, frame loading, animation, audio dispatch and related helpers. The
sprite OAM offset temporarily holds allocation flags, and the tile-count byte
also carries a state bit; the names do not imply exclusive semantics. The bulk
clear loops use separate array-base aliases. Independent symbol-change controls
cover 150 renamed field operands and seven record-stride operands; the matching
build preserves the original addressing encodings. No additional PRG bytes are
credited by these readability changes.

The descriptor index, script wait and encoded script pointer arrays also use
provisional per-slot names. Their access patterns include slot initialization,
record loading, interpreter save/restore and wait handling; the names do not
establish every higher-level use. Four additional symbol-change controls cover
42 physical instruction operands.
