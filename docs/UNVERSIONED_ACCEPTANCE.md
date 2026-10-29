# Unversioned acceptance review

This release now has a complete maintained source composition, its own exact
whole-ROM build and an evidence-bound inventory ledger. `make build
TARGET=us-unversioned` and `make source-audit TARGET=us-unversioned` reproduce
its checks. The ledger derives acceptance from the remaining concrete work;
matching bytes alone do not close a review decision.

| Completion item | Reviewed evidence and decision |
| --- | --- |
| Native banks and entries | All 21,381 native bytes have source-associated official instruction boundaries. All six vectors and all 191 nominal dispatch entries identify those boundaries. The two bank-1 transfers into bank 0 follow the common reset/NMI mapper writes. No missing native body remains. |
| Script successors | Own typed command declarations, literal branches, terminated lookup/remap tables, and indexed cases are integrated. The two indexed paths have six cases after clamp/divide and eight after the 0007 mask. A20A overlaps a record-load operand; the F209 alternative overlaps F20A/F20C before rejoining F20F. These views are preserved without counting their physical bytes twice. Saved pointers, retry paths and dynamic record inputs retain their native mechanisms. |
| Records and resources | The 123 descriptors, normal/compact/contact views and script words are reviewed against the own build. Nine descriptor indices retain FFFF: selection conditionally fetches one vector byte and nine RAM bytes. This is preserved behavior, not an invented ROM record or a requirement to enumerate RAM. Literal resource7C37 remains a CPU address below ROM; no FC37 conversion is inferred. |
| Data formats | Own 21-state tables, 12 map grids, 144 chunk slots, 30 position streams/420 records, 119 animations, 24 palettes and 298 bank-0 frames rebuild exactly. One position stream decreases at a stored key; its order is preserved. The 51 messages use ordinary PPU streams rather than the later packed decoder. |
| Audio | Own indexed voice tables, effects and music use the shared reviewed protocol. Literal starts, loop words and restoration contexts are accounted for. The F9 command retains its four source values and stale fifth register value. Later-revision runtime observations are not assigned to this release. |
| Editable inputs and complete build | Nine input groups decode and encode deterministically. A fresh decode reproduces every input payload, including all CHR tiles. The full ROM and components match; 26 isolated changed-source builds and all nine asset-group controls fail comparison as required. Inputs, binaries and local evidence remain ignored. |

The final native integration also recovered the split NMI sequence at
835F–83CF, the distinct 9D and B4 bodies, the absent later opcode35 rescan tail,
and the own 03 selected-field mask. These are readable native operations;
there are no output patches or raw instruction-byte replacements.

Retained storage decisions remain bounded:

- D640 is the single byte between the pointer-replacing 00/1E command and the
  independently targeted D641 entry, corresponding to the later D75D group.
- D5AB and EEF1 are fetched lookahead after nine selected record fields. EAA9–EAAA
  and EB29–EB2A are separate two-byte record tails; only their first byte is
  lookahead. Their neighboring normal/compact boundaries support the same
  retained-tail classification as the later EB08/EB8F groups.
- F209 preserves the conditional overlapping script view described above.
- F37E–F380 lie outside all fourteen menu payloads, matching the later F354
  boundary relationship. F602–F603 are separate from the nominal map grid;
  its first byte is discarded lookup lookahead, as in the later F623 group.
- FC37 stores the bank-relative word7C39. The five-byte frame-shaped view at
  FC39 is identical to the known bank-0 frame at BA8D. Its zero attribute at
  FC3D also begins the following zero-storage run. Source preserves that
  overlap and the complete editable tile/attribute pair. This supports a
  retained resource-data format; ordinary rendering and the intended meaning
  of literal CPU7C37 remain unproved.

Original names, historical toolchain, intended uses, dead-code reachability and
hypothetical execution from arbitrary injected state remain uncertain. None
exposes an unrepresented byte range, missing native implementation or unresolved
supported literal successor in this reviewed inventory. A future reinterpretation
can coexist with the current representation. It must not change the reference,
repair the literal addresses, or erase an existing supported view.

The final integration checkpoint runs all six identity audits, tooling tests,
current exact builds and reviewed inventories, then refreshes progress and checks
staged content/outgoing history before the authorised private push. The earlier
native-call batch remains bounded to its established verification scope.
