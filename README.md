# Bible Adventures

A matching reconstruction of Wisdom Tree's *Bible Adventures* for the
Nintendo Entertainment System (NES), aiming to recover the complete game as
readable source.

This is an **AI-driven experiment** to see what coding agents can do.
Almost all code, analysis and tooling are AI-generated.

## Progress

Initial repository setup. No game code has been reconstructed, no ROM build
exists, and the target release has not been selected. The target will be
identified from the owner's ROM; its hashes and cartridge details remain
unpinned in [config/targets/nes.json](config/targets/nes.json).

The starting approach is labelled 6502 assembly, with gameplay scripts and data
decoded as their formats become understood. Programmer Vance Kozik identifies
the game's engine as the in-house BOGUS state-machine system in his
[developer interview](https://www.nesworld.com/kozik.php). The original source
language, assembler and toolchain have not been established.

Future progress reports will distinguish reconstructed code, decoded data,
local binary inclusions and unresolved regions. A matching ROM assembled from
copied bytes alone will not count as a completed reconstruction.

## Building

The repository tools require Python 3.10+ and Make. They use only the Python
standard library. Run from the repository root:

```sh
make test
```

Put your own NES ROM in the ignored `baseroms/` directory. The default path is:

```text
baseroms/bible-adventures.nes
```

Inspect its container and calculate its identity:

```sh
make identify
```

For a different filename:

```sh
make identify ROM='baseroms/Bible Adventures.nes'
```

This reads iNES and NES 2.0 containers and prints JSON with full-file hashes,
separate PRG/CHR hashes, header fields, and any trainer or trailing data.
It does not modify the ROM, identify a release from a database, or select a
reference automatically. Header mapper fields still need verification against
the cartridge and program behaviour.

| Command | Purpose |
| --- | --- |
| `make help` | Show available commands. |
| `make identify` | Inspect a local ROM without changing it. |
| `make test` | Test the tooling using synthetic data; no game ROM needed. |

A ROM build and pinned assembler/linker will follow target identification.
`make build` is not implemented yet. The intended build will verify every byte
of the selected container and its PRG/CHR payload separately.

## Repository

```text
.
├── Makefile        Project commands
├── assets/         Future verified progress image and ROM map
├── config/         Target identity, future tool pins and bank maps
├── include/        Shared assembly symbols and macros
├── src/            Reconstructed code, scripts and structured data
├── tools/          Build and analysis scripts
├── tests/          Tooling tests using synthetic data
└── docs/           Internal AI scratch notes
```

## About

This project does not accept contributions, pull requests, issues or support
requests. ROMs, extracted assets and game binaries are not included.

## Licence and credits

The [MIT licence](LICENSE.md) covers our own contributions to the source, tools
and documentation. It does not cover original game code, assets, text or
trademarks, or third-party material.

### Original game

*Bible Adventures* was developed by Color Dreams for Wisdom Tree. Vance Kozik
describes his work on the game's levels and character programming in the
[developer interview](https://www.nesworld.com/kozik.php).

This is an unofficial project, unaffiliated with the original developers,
publisher or Nintendo.

### Tools and dependencies

The initial tools use Python's standard library. No third-party game code,
assembler, linker or emulator is bundled. Future dependencies will be pinned
in `config/` and retain their upstream licences and notices.

### References and inspiration

- [NESdev Wiki](https://www.nesdev.org/wiki/Nesdev_Wiki), for NES hardware research.
- [iNES](https://www.nesdev.org/wiki/INES) and [NES 2.0](https://www.nesdev.org/wiki/NES_2.0), for ROM container formats.
- [Color Dreams mapper documentation](https://www.nesdev.org/wiki/Color_Dreams), a starting reference whose applicability must be checked against the selected dump.
- [ca65](https://cc65.github.io/doc/ca65.html) and [ld65](https://cc65.github.io/doc/ld65.html), candidates for the reconstruction toolchain, without implying they were used for the original game.
