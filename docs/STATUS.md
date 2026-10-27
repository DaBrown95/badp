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

No game source has been reconstructed and no ROM build exists. Passing input
audits is not reconstruction progress. The initial source approach is labelled
6502 assembly and decoded scripts/data. The developer identifies BOGUS as the
state-machine engine in the [Vance Kozik interview](https://www.nesworld.com/kozik.php);
the original source language and toolchain remain unestablished.

## Next work

1. Verify mapper behaviour, bus conflicts, timing and reset mapping for v1.5.
   Map physical banks separately from CPU/PPU addresses.
2. Pin an assembler/linker and implement an exact layout build. Classify local
   binary inclusions explicitly; an equal scaffold is not source progress.
3. Trace reset, NMI/IRQ vectors, bank transitions and indirect dispatch. Separate
   native instructions, BOGUS state-machine data, other data and unknown bytes.
4. Reconstruct connected routines and data formats, retaining changed-source
   negative controls and one current full-build proof. Build the progress map
   from verified ownership with no invented denominator.
5. Establish repeatable runtime checks for all three adventures and shared
   menus, controls, rendering, audio and progression. Finish source accounting
   and gameplay verification for v1.5, then repeat acceptance for each remaining
   version in the recorded order.

The repository retains the Sims project's MIT licence, AI disclosure,
owner-run contribution policy and strict matching standard. No hosted repository
or remote has been created. Configure hosted contribution settings when
publication is requested.
