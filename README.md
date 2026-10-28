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
[config/targets/](config/targets/).

The v1.5 build matches the reference ROM byte for byte. Its source covers reset
and startup, NMI frame and controller handling, PPU update streams and setup,
palette streams, split-screen setup, scroll updates, bank switching, sprite
setup and animation, audio voice and command handling, map initialization and
redraw, frame motion and slot updates, arithmetic, packed-text decoding, and
shared banked record and data-copy routines. The script command dispatcher, its record-length and
handler tables, and source at all 197 handler entries are also reconstructed.
Slot descriptors, position-record streams, audio lookup tables and several
script regions are represented as structured data. Some scripts and slot
records have also been observed during the opening gameplay checks. Remaining
PRG bytes and CHR graphics are local binary inclusions.
Changed-source controls check that each reconstructed region affects the
assembled output.

We will complete v1.5 first, then adapt the shared reconstruction to the other
versions in order. Each version needs its own matching and gameplay evidence.
The [project configuration](config/project.json) records the primary target and
rollout order.

Percentages show verified reconstructed code and structured data as a share of
physical PRG bytes. PRG also contains data whose format is not yet understood;
the game's total code denominator is unknown. CHR graphics, the container
header and copied bytes do not count as reconstructed source. These percentages
are not measures of gameplay completion.

<!-- BEGIN GENERATED PROGRESS -->
| Version | Reconstructed PRG | Status |
| --- | ---: | --- |
| USA v1.5 | **63.10%** (41,354 / 65,536 bytes) | In progress |
| USA v1.4 | **0.00%** (0 / 65,536 bytes) | Not started |
| USA v1.3 | **0.00%** (0 / 65,536 bytes) | Not started |
| USA v1.2 | **0.00%** (0 / 65,536 bytes) | Not started |
| USA v1.1 | **0.00%** (0 / 65,536 bytes) | Not started |
| USA, unversioned | **0.00%** (0 / 65,536 bytes) | Not started |
<!-- END GENERATED PROGRESS -->

Run `make progress` to rebuild v1.5 and refresh this table and the
[verified progress data](assets/progress.json).

The starting approach is labelled 6502 assembly, with gameplay scripts and data
decoded as their formats become understood. Programmer Vance Kozik identifies
the game's engine as the in-house BOGUS state-machine system in his
[developer interview](https://www.nesworld.com/kozik.php). The original source
language, assembler and toolchain have not been established.

Future progress reports will distinguish reconstructed code, decoded data,
local binary inclusions and unresolved regions. A matching ROM assembled from
copied bytes alone will not count as a completed reconstruction.

## Building

Requires Python 3.10+, Make and a C compiler. On macOS, install Xcode's command
line tools. Run once from the repository root to download and build the pinned
assembler and linker locally:

```sh
make setup
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
make build
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

`make build` assembles and links v1.5 in a fresh directory, verifies the entire
ROM and its components, and runs the source-change controls. Output and proof:
`build/us-v1.5/bible-adventures.nes` and `build/us-v1.5/proof.json`. They remain
local, along with the extracted inputs and control builds.

On macOS with Apple silicon and Homebrew's SDL2 installed, an optional emulator
check exercises the opening of each adventure:

```sh
make setup-mesen
make verify-gameplay
make verify-controller
```

The check runs the reference and matching build under the same inputs, comparing
rendered frame pixels, state, mapper writes, NMI, OAM DMA, audio-register writes
and direct `$2000`–`$2007` write timing (excluding `$2004` OAM-data writes).
PNG screenshots are retained as visual evidence. The
Moses sequences carry and recover the baby, complete the first three levels,
and carry the baby into the fourth. The third-level checks cover both a
lower-platform route and the completed route over the roof and down the stairs.
A separate Noah sequence opens and closes the inventory and checks its table reads. These sequences check
controller actions against their record loads; David's opening also checks a
native position event against its record load.
It keeps its evidence in the ignored `reports/us-v1.5/runtime/` directory. These
short opening scenarios do not establish full gameplay completion or physical
cartridge behaviour. The controller check also compares all eight button bits
and simultaneous press/release handling on the reference and build.

| Command | Purpose |
| --- | --- |
| `make help` | Show available commands. |
| `make setup` | Download and build the pinned cc65 tools locally. |
| `make setup-mesen` | Download the pinned optional MesenCE emulator locally. |
| `make targets` | Show the primary target and version order. |
| `make identify` | Inspect the primary ROM, or a selected target/file. |
| `make audit` | Verify the primary input; `TARGET=<id>` selects another. |
| `make audit-all` | Verify all six input identities. |
| `make build` | Build and compare v1.5; retain source-change controls. |
| `make verify-gameplay` | Compare v1.5 opening scenarios and inventory in MesenCE. |
| `make verify-controller` | Compare controller bit order and simultaneous transitions. |
| `make progress` | Rebuild and update the per-version tracker. |
| `make position-records` | Decode v1.5 position records to ignored local analysis. |
| `make script-entries` | Inventory candidate v1.5 script entry points locally. |
| `make script-flow` | Trace reviewed v1.5 script paths to local analysis. |
| `make contact-record-flow` | Trace candidate contact-event records and scripts locally. |
| `make native-event-flow` | Trace candidate native events through later scripts. |
| `make direct-record-flow` | Check direct record targets for possible script overlaps. |
| `make packed-text` | Decode v1.5 packed text to local analysis. |
| `make ppu-streams` | Inventory candidate PPU command streams without exporting text. |
| `make trace-audio` | Capture audio-command reads during extended v1.5 emulator inputs. |
| `make audio-inventory` | Validate and decode the local audio trace; payloads remain local. |
| `make audio-flow` | Trace candidate audio-command paths from literal voice starts. |
| `make trace-sprites` | Capture sprite resource and frame entries during extended v1.5 inputs. |
| `make sprite-inventory` | Validate and decode the local sprite trace; payloads remain local. |
| `make map-data` | Decode candidate map layouts and chunks to local analysis. |
| `make trace-map` | Check map fetches in extended v1.5 emulator inputs. |
| `make prg-inventory` | Combine verified source ownership with candidate and observed data uses. |
| `make trace-runtime-extents` | Capture sampled Moses script and record accesses. |
| `make runtime-extents` | Check sampled command and record bytes against the current source map. |
| `make test` | Test the tooling using synthetic data; no game ROM needed. |

Run `make trace-runtime-extents` before `make runtime-extents`; repeat the
capture after changing the build or gameplay verifier.

Other versions have pinned reference identities but do not have builds yet.

## Repository

```text
.
├── Makefile        Project commands
├── assets/         Verified progress data
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

The tooling uses Python's standard library and downloads these dependencies
locally when requested. No third-party game code or emulator is bundled.

| Dependency | Use | Licence |
| --- | --- | --- |
| [cc65 V2.19](https://github.com/cc65/cc65/tree/555282497c3ecf8b313d87d5973093af19c35bd5) | ca65 assembler, ld65 linker and da65 disassembler | [zlib](https://github.com/cc65/cc65/blob/555282497c3ecf8b313d87d5973093af19c35bd5/LICENSE) |
| [MesenCE 2.2.1](https://github.com/nesdev-org/MesenCE/releases/tag/2.2.1) | Optional opening-gameplay comparisons | [GPL-3.0-or-later](https://github.com/nesdev-org/MesenCE/blob/20ba206cef5ba207c21203176d02cb9f43dda9fb/LICENSE) |

### References and inspiration

- [NESdev Wiki](https://www.nesdev.org/wiki/Nesdev_Wiki), for NES hardware research.
- [iNES](https://www.nesdev.org/wiki/INES) and [NES 2.0](https://www.nesdev.org/wiki/NES_2.0), for ROM container formats.
- [Color Dreams mapper documentation](https://www.nesdev.org/wiki/Color_Dreams), a starting reference whose applicability must be checked against the selected dump.
- [ca65](https://cc65.github.io/doc/ca65.html) and [ld65](https://cc65.github.io/doc/ld65.html), used for the reconstruction without implying they were used for the original game.
