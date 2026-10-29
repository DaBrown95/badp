# Unversioned acceptance review

This release has a complete source implementation, an exact whole-ROM build
and an inventory review tied to its evidence files. Run `make build
TARGET=us-unversioned` and `make source-audit TARGET=us-unversioned` to repeat
the checks with the required local inputs. Acceptance depends on both the
matching build and the review decisions.

## Native banks and entries

Source accounts for all 21,381 native bytes, with checked boundaries for official
instructions. All six vectors and all 191 nominal dispatch entries identify
those boundaries. The two bank-1 transfers into bank 0 follow the common
reset/NMI mapper writes. No missing native body remains.

## Script successors

This release has typed command declarations, literal branches, terminated
lookup/remap tables and indexed cases. The two indexed paths have six cases
after clamp/divide and eight after the 0007 mask. A20A overlaps a record-load
operand. The F209 alternative overlaps F20A/F20C before rejoining F20F. Source
preserves these views without counting their physical bytes twice. Saved
pointers, retry paths and dynamic record inputs retain their native mechanisms.

## Records and resources

The review checks all 123 descriptors, normal/compact/contact views and script
words against this release's build. Nine descriptor indices retain FFFF.
Selecting them conditionally fetches one vector byte and nine RAM bytes. Source
preserves that behaviour without inventing a ROM record or requiring an
inventory of RAM contents. Literal resource7C37 remains a CPU address below
ROM. The review does not infer a conversion to FC37.

## Data formats

This release's 21-state tables, 12 map grids, 144 chunk slots, 30 position streams
with 420 records, 119 animations, 24 palettes and 298 bank-0 frames rebuild
exactly. One position stream decreases at a stored key. Source preserves its
order. The 51 messages use ordinary PPU streams rather than the later packed
decoder.

## Audio

This release's indexed voice tables, effects and music use the shared reviewed
protocol. The review accounts for literal starts, loop words and restoration
contexts. The F9 command retains its four source values and stale fifth register
value. Runtime observations from later revisions do not verify this release.

## Editable inputs and complete build

Nine input groups decode and encode deterministically. A fresh decode reproduces
every input payload, including all CHR tiles. The full ROM and components match.
All 26 isolated changed-source builds and all nine asset-group controls fail
comparison as required. Inputs, binaries and local evidence remain ignored.

The final native integration also recovered the split NMI sequence at 835F to
83CF, the distinct 9D and B4 bodies, the absence of the later opcode35 rescan
tail, and this release's 03 selected-field mask. Source uses readable native
operations. It has no output patches or raw instruction-byte replacements.

## Retained storage

- D640 is the single byte between the pointer-replacing 00/1E command and the
  independently targeted D641 entry. It corresponds to the later D75D group.
- D5AB and EEF1 are lookahead bytes fetched after nine selected record fields.
  EAA9 to EAAA and EB29 to EB2A are separate two-byte record tails. Only their
  first byte is lookahead. Their neighbouring normal/compact boundaries support
  the same retained-tail classification as the later EB08/EB8F groups.
- F209 preserves the conditional overlapping script view described above.
- F37E to F380 lie outside all fourteen menu payloads, matching the later F354
  boundary relationship. F602 to F603 are separate from the nominal map grid.
  The first byte of the pair is discarded lookup lookahead, as in the later
  F623 group.
- FC37 stores the bank-relative word7C39. The five-byte frame-shaped view at
  FC39 is identical to the known bank-0 frame at BA8D. Its zero attribute at
  FC3D also begins the following zero-storage run. Source preserves that
  overlap and the complete editable tile/attribute pair. This supports a
  retained resource-data format. Ordinary rendering and the intended meaning
  of literal CPU7C37 remain unproved.

## Limits of the review

Original names, the historical toolchain, intended uses and dead-code
reachability remain uncertain. Behaviour under arbitrary injected state also
remains uncertain. None of these questions exposes an unrepresented byte range,
missing native implementation or unresolved supported literal successor in the
reviewed inventory. Later interpretations may coexist with the current source.
They must preserve the reference, literal addresses and existing supported views.

The integration checks cover all six input identities, synthetic tooling tests,
exact builds and inventories tied to their evidence files. Supporting binaries,
editable assets and review files remain local. The native-call probes verify
only their established controlled inputs. Runtime results from other versions
do not verify this release.
