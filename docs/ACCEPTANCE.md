# v1.5 acceptance

The maintained decisions are in `config/inventory-review-us-v1.5.json`.
`make source-audit` validates their reference/source/map bindings and evidence
hashes, retains competing uses, and derives acceptance from the remaining work.
Missing or stale reviews block acceptance. Closing a flag cannot hide opaque
local bytes. Rebuilding identical source does not invalidate still-applicable
scoped evidence merely because the build proof changed.

| Requirement | Decision | Remaining reconstruction question |
| --- | --- | --- |
| Native banks, vectors and supported transfers | Closed | None identified; arbitrary injected destinations are conditional behavior. |
| Bank switching, reset/NMI and shared tails | Closed | None identified; preserve physical-cartridge uncertainty. |
| BOGUS commands, roots and successors | Closed | Dynamic pointers and speculative asset decodes expose no additional missing handler. |
| Slot records and resource relationships | Closed | Supported field classes, directories and frame extents are represented. |
| Audio engine, tables and command formats | Closed | No concrete opaque executable region identified. |
| Necessary local assets and deterministic encoding | Closed | Artwork and decoded asset values stay local and outside source credit. |
| Bank 1 `$D75D` | Closed | Retained storage between the pointer-replacing command and next known entry; no invented opcode or padding role. |
| `$EB08-$EB09` | Closed | Separate retained storage; first-byte lookahead, no extra selected field. Original purpose remains unknown. |
| `$EB8F-$EB90` | Closed | Same supported boundary/consumer decision, preserved across resource relocation. |
| `$F354-$F356` | Closed | Separate retained prefix outside the fourteen menu payloads; original purpose unknown, no artwork/PPU format assigned. |
| `$F623-$F624` | Closed | Separate retained suffix outside the grid; first byte is discarded lookahead, no extra-cell interpretation. |

Each item records its exact unknown, completion effect and closing evidence
in the ledger. Unknown original names, intended roles, dead-code reachability,
and hypothetical execution under arbitrary RAM state are not independent gates.
A concrete new source/format gap must be named before adding an investigation.

Acceptance also requires a current byte-identical full build and meaningful
source/asset controls. v1.5 has no remaining reconstruction blocker in this
checklist and is accepted by its current build and derived audit.

## v1.4 adaptation

`config/inventory-review-us-v1.4.json` applies the same six mechanism gates and
five storage decisions to its own reference, generated source, physical regions
and evidence. The last storage group is at `$F621-$F622`; the other four retain
their primary addresses. Its reset prefix is separately readable assembly,
including the original unused `$0F` load / uninitialized `$00` countdown bug.
Bank-0 resource addresses relocate by 22 bytes and the shorter brand payload
moves later bank-1 data by two bytes. Packed-text CPU addresses, PPU addresses
and RAM/arithmetic constants keep their own namespaces.

The full target build encodes every local gap through the shared asset formats,
then checks whole-ROM equality, every source and symbol control, and eight
asset edits. Its own native entries, dispatch tables, script successors, record
views and audio starts are inventoried. Eight primary incidental script aliases
are not carried over when their relocated resource bytes no longer support the
opcode. This preserves the actual data and the conditional interpretation; it
does not invent another missing routine. Primary gameplay observations are not
credited to v1.4. Scoped wrapper/loader rules are reused where their code is
unchanged, with target operands and boundaries checked separately.

v1.4 is accepted: its current full build and evidence-bound review close every
gate, with zero opaque PRG bytes and no remaining source/format blocker. The
v1.3 adaptation below continues with shared source and its own identity,
layout, build and review evidence.

## v1.3 adaptation

The maintained variant restores the shorter reset dispatcher, second-controller
NMI work, the 32-entry conflict table and its reset-state selector. Later helper
calls become their original inline instructions, with the original loop and
fallthrough order. Typed relocation keeps native RTS operands, script CPU
addresses, encoded resources, text pointers and numeric/RAM words distinct.
Palette streams precede sprite frames; opcode $18 selects the moved bank-0
stream. All necessary local inputs use the same eight decoded asset formats.

The aligned bank-1 `PLA / PLA / RTS` fragment is retained as a conditional
native view. v1.1 through v1.3 repeat it at the exact bank-0 mode-gate return
address as that gate moves. This supports its representation without asserting
an ordinary bank-1 caller or another complete routine. Changed incidental
script predicates are recorded explicitly; they do not override actual record,
resource or music fields. The five retained storage groups preserve their
values at D755, EB00–EB01, EB87–EB88, F34C–F34E and F619–F61A.

v1.3 is accepted: its own fresh decoded full build and evidence-bound review
close all six mechanism and five storage decisions, with zero opaque PRG bytes.
All 197 nominal handler entries, supported native calls, script successors,
record/resource relationships and audio starts have their target inventory.
All physical source regions have meaningful changed-source evidence. Eleven
obsolete primary controls have explicit retirement reasons; five controls cover
new source components. This is not a transfer of primary gameplay evidence.

No v1.3 reconstruction blocker remains. The v1.2 adaptation below continues
with separate source, geometry, build and inventory evidence. Unknown original
names or arbitrary-state reachability do not add gates to accepted versions.


## v1.2 adaptation

v1.2 is accepted by its own fresh decoded-input build and input-bound review.
All six mechanism and five retained-storage decisions are closed, with zero
opaque PRG bytes. The original reset pulses use three explicit ROM conflict
constants; the later reset validator/countdown is absent. Mapper writes and
selected default-bank restores are inline, while the supported standalone
helper remains. Two main-state callers use a separate nineteen-byte unrolled
shift, alongside the retained generic coordinate helper.

The skipped audio pop and the mirrored secondary branch/pop/return retain
conditional native views without an invented ordinary caller or whole routine.
The menu consumers retain the same bounded fifteen-byte brand stream; those
native bytes are not artwork. The five retained storage groups use their own
placements and evidence, preserving uncertainty about original purpose. Three
record-format consumer regions reuse prior rules only through explicit
instruction and same-label target comparisons. No other-version gameplay
observation verifies v1.2.

All 197 nominal handler entries, 25 declared native calls, script successors,
record/resource relationships and audio starts have their target inventory.
Incidental decodes remain conditional and expose no concrete missing source.
Fourteen obsolete primary controls have specific retirement reasons; replacement
components have their own meaningful edits. Every physical source region is
controlled, and all eight local asset formats re-encode exactly.

No v1.2 source/format blocker remains. v1.1 and the unversioned release still
need their own shared-source adaptations, exact full builds and reviewed
inventories, in that order.
