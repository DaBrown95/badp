# Bible Adventures

A matching reconstruction of Wisdom Tree's *Bible Adventures* for the
Nintendo Entertainment System (NES), aiming to recover the complete game as
readable source across all six supplied USA versions.

This is an **AI-driven experiment** to see what coding agents can do.
Almost all code, analysis and tooling are AI-generated.

## Progress

All six reference ROMs have been identified against a
[pinned No-Intro catalogue](config/catalogues/no-intro-nes.json). Exact headers,
full-file hashes and separate PRG/CHR identities are recorded in
[config/targets/](config/targets/). No game code has been reconstructed and no
ROM build exists.

We will complete v1.5 first, then adapt the shared reconstruction to the other
versions in order. Each version needs its own matching and gameplay evidence.
The [project configuration](config/project.json) records the primary target and
rollout order.

| Version | Target | Reconstruction order |
| --- | --- | --- |
| USA v1.5 | `us-v1.5` | Primary |
| USA v1.4 | `us-v1.4` | 2 |
| USA v1.3 | `us-v1.3` | 3 |
| USA v1.2 | `us-v1.2` | 4 |
| USA v1.1 | `us-v1.1` | 5 |
| USA, unversioned | `us-unversioned` | 6 |

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

Keep your own NES ROMs in the ignored `baseroms/` directory, using the filenames
recorded in each target manifest. The default target is v1.5:

```text
baseroms/Bible Adventures (USA) (v1.5) (Unl).nes
```

Inspect its container and verify the reference inputs:

```sh
make identify
make audit
make audit-all
```

Select another configured version, or inspect an arbitrary file:

```sh
make audit TARGET=us-v1.4
make identify ROM='baseroms/another-dump.nes'
```

`make identify` reads iNES and NES 2.0 containers and prints JSON with full-file hashes,
separate PRG/CHR hashes, header fields, and any trainer or trailing data.
It does not modify the ROM, identify a release from a database, or select a
reference automatically. The audits compare against reviewed pins, including
catalogue SHA-1 checks. Header mapper fields still need verification against the
cartridge and program behaviour. Input audits do not establish a working build.

| Command | Purpose |
| --- | --- |
| `make help` | Show available commands. |
| `make targets` | Show the primary target and version order. |
| `make identify` | Inspect the primary ROM, or a selected target/file. |
| `make audit` | Verify the primary input; `TARGET=<id>` selects another. |
| `make audit-all` | Verify all six input identities. |
| `make test` | Test the tooling using synthetic data; no game ROM needed. |

A ROM build and pinned assembler/linker are the next implementation steps.
`make build` is not implemented yet. The intended build will verify every byte
of the selected container and its PRG/CHR payload separately.

## Repository

```text
.
├── Makefile        Project commands
├── assets/         Future verified progress image and ROM map
├── config/         Target identities, version order, future tool pins and maps
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
