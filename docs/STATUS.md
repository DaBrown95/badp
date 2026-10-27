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

The v1.5 build now assembles and links to the exact reference, with 121 bytes of
source code and 44 bytes of structured data across the physical PRG banks.
It still includes 65,371 local PRG bytes and 65,536 local CHR bytes. Seven
independent source-change controls verify every listed reconstructed region.
Passing input audits or whole-ROM equality alone is not reconstruction
completion. The developer identifies BOGUS as the
state-machine engine in the [Vance Kozik interview](https://www.nesworld.com/kozik.php);
the original source language and toolchain remain unestablished.

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
PPUSTATUS polling routine twice, and setting PPUMASK. The tails in both banks
contain a bank-select routine/table, NMI handler, reset routine and interrupt
vectors. The NMI handlers use different RAM source locations in the two banks;
their called routines and complete timing have not yet been traced.

The [source map](../config/source-us-v1.5.json) records bank, CPU address, size,
classification and control for every owned region. `make build` retains the
actual link map, debug information, source snapshots, local inputs, control
outputs and hashes under `build/us-v1.5/`. The assembler and linker are built
from the checksum-pinned cc65 V2.19 release; V2.19 reports itself as V2.18 with
the release's Git build ID, as documented upstream.

The repository retains the Sims project's MIT licence, AI disclosure,
owner-run contribution policy and strict matching standard. No hosted repository
or remote has been created. Configure hosted contribution settings when
publication is requested.
