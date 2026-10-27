# Project guidance

This is an owner-run, AI-driven matching reconstruction of *Bible Adventures*
for the NES. The goal is the complete game as readable, rebuildable source.
The target release is not selected; its pending identity is recorded in
`config/targets/nes.json`. Follow the user's instructions over this file.

## Matching

- Identify the owner's ROM before selecting a revision, mapper, bank layout or
  timing model. Record full-file SHA-1/SHA-256, exact header bytes and separate
  PRG/CHR identities. Header metadata is evidence to investigate, not proof of
  cartridge hardware. Never silently repair, strip or replace a reference header.
- Keep the reference ROM and expected hashes fixed once selected. Investigate
  mismatches; never change the reference to make a candidate pass.
- Accepted code must assemble and link to identical bytes at the original bank
  and CPU address. Preserve addressing modes, branch encodings, vectors, layout
  and alignment. No output patches, masks, fabricated code or raw instruction
  bytes disguised as reconstructed code.
- Keep unconverted regions explicit and local. Binary inclusions and mechanical
  disassembly are scaffolding, not evidence of understood source. Use labelled
  instructions for code and structured definitions for decoded tables/scripts.
  Document justified byte directives, such as unsupported opcodes or data.
- Treat inferred names, types, routine boundaries and BOGUS script formats as
  provisional. Distinguish static findings, byte matches and runtime evidence.
- Preserve original bugs and hardware behaviour in matching source. Document
  known bugs briefly; keep optional fixes separate from the matching target.
- Work in small connected batches. Keep one latest verified full-build proof,
  including changed-source negative controls, and a bounded set of useful
  failures. Preserve unique attempts and findings; record retirement of obsolete
  generated payloads. An old hash ledger does not require permanent retention.

## NES behaviour

- Track physical ROM offsets, PRG/CHR bank identities and CPU/PPU addresses
  separately. A CPU address alone does not identify code across bank switches.
  Account for aliases and count each physical ROM byte once in coverage.
- Respect the NES CPU variant, zero page, stack, flags, interrupt entry/return,
  PPU register side effects, OAM DMA, APU/DMC behaviour and controller reads.
  Check cycle timing where hardware interactions depend on it.
- Verify mapper writes, bus conflicts, mirroring, reset mapping and bank-switch
  transitions from evidence. Do not transplant GBA compiler, ABI, IRQ or memory
  assumptions from the Sims project.
- Recover the engine and investigate the BOGUS state-machine data described by
  the developer. Do not assume every PRG byte is native code, or infer a C
  compiler or exact original language from the CPU instruction set alone.

## Verification and progress

- `make identify` reads and hashes the local ROM; it does not validate its title
  or revision against an independent catalogue. Do not auto-pin its output.
- Run `make test` for tooling changes. Test meaningful failure cases using
  synthetic fixtures; never commit game bytes as test data.
- There is no ROM build yet. Once implemented, pin tools and flags, build from
  a clean output directory, compare the complete file and its components, and
  retain source-to-bank/address maps. Never substitute a copy of the reference
  for a missing build step.
- Before accepting a source replacement, change a meaningful instruction or
  operand in an isolated copy and verify that a fresh build and comparison fail.
  Retain that negative control with the successful build evidence.
- Before publishing progress, regenerate it from verified source ownership and
  matching results. Keep native code, decoded scripts/data, extracted assets,
  copied regions and unresolved bytes separate. Leave unknown denominators
  unknown; never colour unverified work green.
- Whole-ROM equality is one gate. Completion also requires a reviewed inventory
  of all code banks, indirect targets, scripts and data formats, plus reproducible
  gameplay checks across all three adventures and shared systems. Necessary local
  graphics/audio inputs must be accounted for without counting them as code.
- Documentation-only edits need link and diff checks, not a ROM rebuild.

## Publication and privacy

- Never commit ROMs, extracted game assets, game binaries, proprietary tools,
  credentials or personal machine paths. Keep local inputs and generated outputs
  under ignored `baseroms/`, `analysis/`, `extracted/`, `build/`, `reports/` and
  `toolchains/`. `baseroms/.gitkeep` is the only tracked ROM-directory file.
- Stage explicit files and inspect their contents and outgoing history before
  pushing. Ignore rules do not protect a file that is already tracked.
- Preserve third-party licences and notices when borrowing code; record its
  source, revision and changes. Attribution alone is not permission.
- The project does not accept contributions. When a hosted repository is set up,
  disable issues, discussions and pull requests wherever supported. Keep that
  policy in the README. Do not contact other projects unless the user asks.
- Commit small verified milestones. Push when publication is authorised; never
  force-push or rewrite published history without an explicit user request.

## Repository and communication

Keep reconstructed code, scripts and structured data in `src/`, shared assembly
symbols and macros in `include/`, pins and maps in `config/`, and tooling in
`tools/`. Preserve added dependency notices in `licenses/`. `docs/` is internal
AI scratch space. Reader-facing instructions belong in the README.

Keep the README lean, retain the AI experiment disclosure and no-contributions
policy, and describe verified results plainly without inflated progress claims.
