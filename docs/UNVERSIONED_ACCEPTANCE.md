# Unversioned acceptance work

v1.5 through v1.1 have separate accepted matching builds and reviewed
inventories. This release remains unaccepted. No isolated component contributes
to the full-build progress table. Original names, intended uses, unused entries
and arbitrary injected RAM states are not separate completion requirements.

## Decisions supported by recovered source

- The actual dispatch loads establish 191 nominal entries: low table `$D0B1`,
  high table `$D170`, and length table `$FDA0`, followed by native code at
  `$FE5F`. BF–C3 are absent nominal entries; conditional byte indices remain
  separate views.
- `$9B` at `$E3E4` pushes the complete supplied RTS word directly. The later
  banked wrapper and high-bit OR are absent. Supported callers and physical
  mappings belong to the target's eventual script inventory.
- Separate word operations at 37/38/39, 57 and 8D/8E, the 5C mask operation,
  and separate PPU operations at 6D/70/74/75/7C have matching native source.
  Shared flag, initialization, controller and queue differences are explicit.
- Sprite consumers read flags/width/height in three separate bytes. The region
  `$B2F1–$C581` contains 119 animation records, 24 palette streams and 298
  frames. Animation pointers close on frame starts; the frames end at the
  native `InitializeMainState` entry. This does not establish exclusive uses.
- The own 21-entry vertical-seed, bank-selector and palette-pointer tables
  match their consumers at `$A487–$A504`. The bank-selector table is also the
  negative-fourth-operand fallback of 6D; all 42 palette pointers identify the
  recovered palette boundaries.
- The message caller, 51 encoded pointers and ordinary AB PPU streams occupy
  bank 1 `$B77B–$CF06`. The later packed decoder and 52-message format do not
  apply. Source retains destinations, pointer relationships and terminators;
  editable tile payloads remain local.

[The component verifier](../tools/verify_unversioned_components.py) checks these
whole components and meaningful changed-source/asset controls against this
release's pinned reference. Run `python3 -m tools.verify_unversioned_components`.
Its receipt is local at `analysis/us-unversioned/components/proof.json`; it
explicitly grants no full-ROM match or acceptance. The manifests and source are
maintained, while local asset inputs remain under ignored `extracted/`.

## Remaining acceptance blockers

| Blocker | Location or mechanism and actual unknown | Why it prevents completion | Evidence that closes it |
| --- | --- | --- | --- |
| Shared source layout | Bank 0 native windows before `$9EFB`, `$C582–$F9C5`, and both fixed tails from `$FE5F`; source correspondence is not a linked target build. | Own addresses, all references and complete emitted extents are not yet integrated. | Maintained target profile assembling all native source, own dispatch/vector entries and actual bank transitions exactly; meaningful source controls cover the resulting regions. |
| Common data and incoming relationships | Bank 0 `$9EFB–$B2F0`: audio prefix, descriptors, map/state tables and resource pointers. | The 21-state palette/seed relationships are recovered; descriptor, map, audio and other field relationships still need source integration. | Readable target differences sharing the existing formats where supported; exact full extents and actual descriptor/map/palette/sprite relationships. |
| Remaining bank-1 source | `$8000–$B77A` and `$CF07–$FC3C`: scripts, records, audio and other structured data. | Own command lengths, word operations and successors must replace later assumptions; retained storage must be classified from its own context. | Connected shared-source adaptation and reviewed script/record/audio relationships. Account for the storage groups through consumers and revision evidence, including absence or changed extents. Preserve justified uncertainty and overlapping uses. |
| Remaining local asset formats | Map chunks/layouts, menu and other PPU payloads, CHR, and the connection of the recovered message/sprite assets to the full source. | No complete editable-input build exists for this target yet. | Decode and re-encode its own inventoried assets with exact gap coverage and meaningful edits; no reference-byte fallback for a missing extent. Reuse existing codecs within their demonstrated format. |
| Full acceptance and publication | Whole container, physical PRG inventory, mechanism review and own build receipts. | Components do not establish complete ownership, whole-ROM equality or current controls. | Current exact complete build, source/symbol/asset controls, finite evidence-backed inventory decisions with zero concrete blockers, all six input audits, tooling checks, refreshed progress, privacy/outgoing review, commit and verified private push. |

Use focused component checks while integrating. Re-run complete gates at the
next substantial integration checkpoint. Preserve valid earlier evidence within
its own scope. Add runtime investigation only when a concrete source, format or
mapping decision remains unresolved after static evidence; do not search every
possible state or require level completion.
