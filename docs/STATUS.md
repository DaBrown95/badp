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
of source code and 16,732 bytes of structured data across the physical PRG banks.
It still includes 27,330 local PRG bytes and 65,536 local CHR bytes. A total of
1,012 independent source-change controls verify every listed reconstructed region.
Passing input audits or whole-ROM equality alone is not reconstruction
completion. The developer identifies BOGUS as the
state-machine engine in the [Vance Kozik interview](https://www.nesworld.com/kozik.php);
the original source language and toolchain remain unestablished.

## v1.5 opening-gameplay evidence

`make verify-gameplay` runs 2,100 NTSC frames each for Noah, Moses and David
in pinned MesenCE 2.2.1, with zeroed power-on RAM and fixed mapper/alignment
settings. It compares the audited reference and verified build under the same
menu, start, right and A inputs. All three reached their opening areas and
showed a change in scroll and screenshot after rightward input. The six sampled
frames, state and cycle counts, mapper-write streams, NMI counts, OAM DMA and
APU-register write streams agreed between the reference and build. Both PRG
banks appeared in the emulator's mapper-write mapping; every observed write
value equalled the mapped ROM byte. This describes the emulator model and the
tested paths, not physical board behaviour or proof of timing on hardware.

The respective Noah, Moses and David runs recorded 70,517, 71,604 and 78,016
mapper writes; 2,028, 2,027 and 2,027 NMIs; and 1,314, 1,262 and 1,245 APU
register writes. Mesen reported 180, 181 and 188 uninitialized-read warnings
respectively, equally for the reference and build; their causes remain to be
investigated. Audio output and complete progression have not been checked.
Screenshots, event streams and the proof remain under ignored
`reports/us-v1.5/runtime/`.

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
Another 24 physical bytes overlap possible record reads and candidate script
decodes, including nine in the existing `$ED71` script; these associations
also remain unverified. Twenty non-overlapping script regions are now
represented as named commands; their context and gameplay roles remain
provisional. Temporary transcriptions were retired after integration.

The map lookup uses 146 two-byte offsets, each a multiple of 68, into locally
supplied map-chunk data. The offset table and state-indexed vertical-base seeds
are source; map layouts and chunk contents remain local. Runtime bounds on
either table have not been established.

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
from those candidates. It finds 1,936 candidate commands and stops at 38 nodes
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
`reports/us-v1.5/runtime-long/`. Newly encountered records observed only in
other modes, or in multiple modes, remain local pending review. The probes,
trace data and screenshots are ignored locally.

One such record at bank 1 `$B936` was accessed in both zero and negative mode.
The negative path interprets byte 2 as flags, while the zero path checks it as
part of the script pointer. The same bytes can therefore have different uses;
the record remains local until those uses and its neighbours are reviewed.

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
gameplay roles remain unverified, and `$B999`'s indexed tables are still local.

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

The sprite animation update now advances timers and handles loop or hold-on-
last-frame behavior. The audio voice start, stop, arbitration and command
interpreter are source, along with instrument register pairs, special-note
presets and overlapping windows into the period table. Wider instrument and
special-note indices are possible in the instructions; their valid runtime
bounds remain unverified.
Focused instruction-subset checks on synthetic records exercise animation,
audio commands, APU register writes, voice bounds and pointer carry; they do
not verify hardware timing or sound playback.

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
