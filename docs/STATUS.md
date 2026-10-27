# Bootstrap status

The repository structure follows the Sims Bustin' Out project, adapted for the
NES. MIT covers project-authored work; original material remains excluded.
The AI disclosure, owner-run contribution policy and strict matching standard
are carried over.

No game ROM has been inspected. The owner chose to identify the release from
their ROM later. The target manifest deliberately contains null identities;
there are no verified routines, progress percentages or build claims.

The initial source approach is readable 6502 assembly and decoded scripts/data.
In the [Vance Kozik interview](https://www.nesworld.com/kozik.php), the developer
identifies BOGUS as the state-machine engine used for Bible Adventures and
describes in-house development tools. This does not establish an original C
compiler, assembler, script syntax or source language. The reconstruction's
assembler choice remains open; ca65/ld65 are candidates.

## Next work

1. Inspect the owner's local dump with `make identify`. Corroborate the release
   and payload identity using a named catalogue revision and provenance; pin
   exact file/header and PRG/CHR identities without changing the input.
2. Verify cartridge mapping and timing, including bus conflicts and reset-bank
   behaviour. Map physical banks separately from CPU/PPU addresses.
3. Pin an assembler/linker and implement an exact layout build. Classify any
   local binary inclusions explicitly; an equal scaffold is not source progress.
4. Trace reset, NMI/IRQ vectors, bank transitions and indirect dispatch. Separate
   native instructions, BOGUS state-machine data, other data and unknown bytes.
5. Reconstruct connected routines and data formats, retaining changed-source
   negative controls and one current full-build proof. Build the progress map
   from verified ownership with no invented denominator.
6. Establish repeatable runtime checks for all three adventures, shared menus,
   controls, rendering, audio and progression. Completion needs complete source
   accounting and gameplay evidence as well as byte equality.

No hosted repository or remote has been created. Hosted contribution settings
must be configured when publication is requested.
