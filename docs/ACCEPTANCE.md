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
source/asset controls. The five storage groups now have supported retained-data
representations. Once the current full build and derived audit accept v1.5,
continue directly to v1.4, v1.3,
v1.2, v1.1 and the unversioned release, sharing source and retaining each
version's own identity, layout, build and review evidence. None of those five
versions is rebuilt or accepted yet.
