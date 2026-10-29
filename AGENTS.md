# Project guidance

This owner-run project uses AI agents to reconstruct *Bible Adventures* for the
NES as readable source that rebuilds the game exactly. It covers all six
supplied USA variants: the unversioned release and v1.1 through v1.5. All six
versions have accepted matching builds and reviewed inventories.
`config/project.json` selects v1.5 as the primary target and records the
reconstruction order. Reviewed input identities are pinned in `config/targets/`.
Follow the user's instructions over this file.

## Version strategy

- Maintain all six accepted versions. For engine changes, verify the primary
  target first, then the affected variants with their own builds and inventories.
- Share engine code, scripts and data definitions where evidence supports their
  use across versions. Express differences in target configuration or small
  source variants. Avoid six independent copies of the game source.
- Preserve each target's own reference, layout and verification evidence. A
  match or successful gameplay run on one version does not verify another.
  Audit all local ROM identities cheaply with `make audit-all`.

## Matching

- Identify new ROMs before adding targets. Record full-file SHA-1/SHA-256,
  exact header bytes and separate PRG/CHR identities. Check the release against
  a pinned catalogue. Investigate header claims before relying on them as
  evidence of cartridge hardware. Never silently repair, strip or replace a
  reference header.
- Keep the reference ROM and expected hashes fixed once selected. Investigate
  mismatches; never change the reference to make a candidate pass.
- Accepted code must assemble and link to identical bytes at the original bank
  and CPU address. Preserve addressing modes, branch encodings, vectors, layout
  and alignment. No output patches, masks, fabricated code or raw instruction
  bytes disguised as reconstructed code.
- Keep unconverted regions explicit and local. Binary inclusions and mechanical
  disassembly are temporary inputs. They do not establish that the source is
  understood. Use labelled instructions for code and structured definitions for
  decoded tables and scripts.
  Document justified byte directives, such as unsupported opcodes or data.
- Treat inferred names, types, routine boundaries and BOGUS script formats as
  provisional. Distinguish static findings, byte matches and runtime evidence.
- Preserve original bugs and hardware behaviour in matching source. Document
  known bugs briefly; keep optional fixes separate from the matching target.
- Work in substantial connected batches. Keep the latest verified full-build
  proof, including changed-source negative controls, and a bounded set of useful
  failures. Preserve unique attempts and findings. Record when you retire
  obsolete generated payloads. A recorded hash does not require keeping an
  obsolete payload forever.

## NES behaviour

- Track physical ROM offsets, PRG/CHR bank identities and CPU/PPU addresses
  separately. A CPU address alone does not identify code across bank switches.
  Account for aliases and count each physical ROM byte once in coverage.
- Respect the NES CPU variant, zero page, stack, flags, interrupt entry/return,
  PPU register side effects, OAM DMA, APU/DMC behaviour and controller reads.
  Check cycle timing where hardware interactions depend on it.
- Verify mapper writes, bus conflicts, mirroring, reset mapping and bank-switch
  transitions from evidence.
- Recover the engine and investigate the BOGUS state-machine data described by
  the developer. Do not assume every PRG byte is native code. Do not infer a C
  compiler or the original language from the CPU instruction set alone.

## Verification and progress

- `make identify` reads and hashes the local ROM. It does not validate its title
  or revision against an independent catalogue. Do not auto-pin its output.
- `make audit` verifies the primary input against reviewed identity pins;
  `TARGET=<id>` selects another target. `make audit-all` checks all six inputs.
  These are reference checks, not ROM builds or reconstruction progress.
- Run `make test` for tooling changes. Test meaningful failure cases using
  synthetic fixtures; never commit game bytes as test data.
- `make build` assembles and links v1.5 using the pinned cc65 tools, verifies the
  whole ROM and components, and retains a source map and changed-source controls
  in `build/us-v1.5/`. Decoded graphics and other asset inputs remain local.
  Select `TARGET=us-v1.4`, `TARGET=us-v1.3`, `TARGET=us-v1.2` or `TARGET=us-v1.1`
  to build a shared-source variant with its own decoded assets, controls and
  inventory. `TARGET=us-unversioned` builds the shared engine with that release's
  formats, editable inputs, controls and inventory. Never substitute a copy of
  the reference for a missing build step.
- Before accepting a source replacement, change a meaningful instruction or
  operand in an isolated copy and verify that a fresh build and comparison fail.
  Retain that negative control with the successful build evidence.
- Before publishing progress, run `make progress` and commit the refreshed README
  table and `assets/progress.json` with the corresponding work. It rebuilds the
  primary target and checks proof freshness and controls before reporting PRG
  source counts. Keep native code, decoded scripts/data, extracted assets,
  copied regions and unresolved bytes separate. Leave the unknown game-code
  denominator unknown. Never credit unverified work.
- Whole-ROM byte equality establishes identical executable behaviour under the
  same conditions. It does not establish that source names, boundaries or data
  interpretations are correct. Completion also requires a reviewed inventory of
  all code banks, indirect targets, scripts and data formats. Necessary local
  graphics/audio inputs must be accounted for without counting them as code.
  Use runtime investigation to resolve specific source, data-format or mapping
  uncertainties. Completing levels is not a separate acceptance requirement.
  Retain existing useful gameplay checks.
- Documentation-only edits need link and diff checks, not a ROM rebuild.

## Publication and privacy

- Never commit ROMs, extracted game assets, game binaries, proprietary tools,
  credentials or personal machine paths. Keep local inputs and generated outputs
  under ignored `baseroms/`, `analysis/`, `extracted/`, `build/`, `reports/` and
  `toolchains/`. `baseroms/.gitkeep` is the only tracked ROM-directory file.
- Stage explicit files and inspect their contents and outgoing history before
  pushing. Ignore rules do not protect a file that is already tracked.
- Preserve third-party licences and notices when borrowing code. Record its
  source, revision and changes. Attribution alone is not permission.
- The project does not accept contributions. Keep hosted issues, discussions
  and pull requests disabled wherever supported. Keep that policy in the README.
  Do not contact other projects unless the user asks.
- Commit small verified milestones. Push when publication is authorised. Never
  force-push or rewrite published history without an explicit user request.

## Repository and communication

Keep reconstructed code, scripts and structured data in `src/`, shared assembly
symbols and macros in `include/`, pins and maps in `config/`, and tooling in
`tools/`. Preserve added dependency notices in `licenses/`. `docs/` retains
technical review notes, some pinned as acceptance evidence.
Keep transient status logs and publication audits in ignored local directories.
Reader-facing instructions belong in the README. Do not remove or edit pinned
evidence without reviewing the change and updating its recorded hashes.

Keep the README lean, retain the AI experiment disclosure and no-contributions
policy, and describe verified results plainly without inflated progress claims.
