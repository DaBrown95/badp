# Bible Adventures

A matching reconstruction of Wisdom Tree's *Bible Adventures* for the Nintendo
Entertainment System. It covers the unversioned USA release and v1.1 through
v1.5. Native code uses labelled 6502 assembly. Scripts and decoded tables use
structured definitions. Shared source and small variants preserve each release's
layout and behaviour, including original bugs.

This is an AI-driven experiment to see whether coding agents can reconstruct
the game. Almost all code, analysis and tooling are AI-generated. The project
is unofficial. The original source files, names, language and toolchain remain
unknown.

## History and motivation

Color Dreams developed *Bible Adventures* for Wisdom Tree, which released it in
1991 without a Nintendo licence. It contains three biblical platform games:
Noah's Ark, Baby Moses, and David and Goliath. The
[MobyGames entry](https://www.mobygames.com/game/8520/bible-adventures/) records
its release history. In a [developer interview](https://www.nesworld.com/kozik.php),
Vance Kozik describes his level and character programming and identifies the
engine as BOGUS, the in-house Binary Output Game Utility System state machine.

I started this project after realising that Cinemassacre's
[AVGN "Bible Games" video](https://www.youtube.com/watch?v=LkNvQYiM6bw), released
in December 2006, was approaching its twentieth anniversary. That put the game
back on my mind, and I wanted to try reconstructing it with coding agents. The
[episode archive](https://cinemassacre-archive.github.io/avgn/episode-17) records
the video's release date and the games it covers.

## Verified status

Each version has its own byte-identical build, changed-source controls and
accepted inventory. "Accepted" means the project's source and data-format review
found no remaining reconstruction blocker. Original names, the purpose of some
retained storage, and whether conditional paths execute remain uncertain.
Matching bytes establish identical executable behaviour under the same
conditions. They do not verify every inferred interpretation or physical
cartridge behaviour.

The percentages below count native code and structured data against all
65,536 physical PRG bytes. Locally supplied assets and explicit alignment fill
account for the rest. CHR graphics are also local inputs. These percentages
measure how many PRG bytes have reconstructed source, not overall completion.
The number of bytes that contain game code remains unknown.

<!-- BEGIN GENERATED PROGRESS -->
| Version | Reconstructed PRG | Status |
| --- | ---: | --- |
| USA v1.5 | **68.95%** (45,185 / 65,536 bytes) | Accepted |
| USA v1.4 | **68.91%** (45,163 / 65,536 bytes) | Accepted |
| USA v1.3 | **69.04%** (45,248 / 65,536 bytes) | Accepted |
| USA v1.2 | **69.08%** (45,270 / 65,536 bytes) | Accepted |
| USA v1.1 | **68.76%** (45,060 / 65,536 bytes) | Accepted |
| USA, unversioned | **67.19%** (44,033 / 65,536 bytes) | Accepted |
<!-- END GENERATED PROGRESS -->

The [progress data](assets/progress.json) separates native code, structured data
and fill. Input identities are pinned in [config/targets/](config/targets/)
against a [reviewed No-Intro catalogue](config/catalogues/no-intro-nes.json).
Target names follow No-Intro; NesCartDB labels the matching v1.5 cartridge
[Version 5.0](https://nescartdb.com/profile/view/4773/bible-adventures).

## Build

You need Python 3.10+, Make, a C compiler and your own matching ROM dump. On
macOS, install Xcode's command line tools. The setup command downloads,
checks the checksum and builds the pinned cc65 assembler and linker under the
ignored `toolchains/` directory:

```sh
make setup
make test
```

Place your ROM in `baseroms/` using the filename in its target manifest. For
the default v1.5 target:

```text
baseroms/Bible Adventures (USA) (v1.5) (Unl).nes
```

Then audit the input and build:

```sh
make audit
make build
```

Select any of the other five supported releases with `TARGET`:

```sh
make audit TARGET=us-v1.4
make build TARGET=us-v1.4
make build TARGET=us-unversioned
```

Each build needs only its selected ROM. `make audit-all` checks all six
inputs when available. `make identify ROM='baseroms/another-dump.nes'` inspects a
file without modifying it or automatically approving it as a reference.

Each build assembles and links the source, decodes or encodes the local assets,
and compares the whole ROM and its components with the reference. It also builds
isolated source and asset edits and checks that each comparison fails. The
output is `build/<target>/bible-adventures.nes`, with the source map, controls and
`proof.json` beside it. Reference headers and hashes stay fixed. A mismatch is a
failure, including when you deliberately edit an asset.

## Local assets and verification

The repository excludes ROMs, graphics, audio, extracted text, generated binaries
and emulator evidence. The build derives the inputs it needs from your
audited ROM and preserves supported editable files under `extracted/`. Asset
values do not receive reconstructed-source credit.

The optional v1.5 export commands include `make extract-chr-tiles`,
`make extract-map-chunks`, `make extract-map-layouts`, `make extract-packed-text`,
`make extract-sprite-frames`, `make extract-menu-tiles`, `make extract-palettes`
and `make extract-ppu-tiles`. These retain fixed geometry, encoding and overlap
constraints. Earlier versions use their own asset profiles; the unversioned
build maintains its distinct sprite, PPU-message and retained-resource formats.

On macOS with Apple silicon and Homebrew's SDL2 installed, optional emulator
comparisons use the pinned MesenCE build:

```sh
make setup-mesen
make verify-gameplay
make verify-controller
```

Run `make build` for v1.5 first. These comparisons cover maintained v1.5 routes
in all three adventures, including five Moses levels, animal carrying and
inventory interactions. They compare rendered pixels, sampled state, mapper
writes, interrupts, DMA and audio/PPU register writes under fixed inputs.
They do not cover every path, other releases or physical hardware. `make help`
lists the other controlled probes.

The maintainer commands `make source-audit` and `make progress` also need local
review evidence and an existing build proof for each version. A fresh clone
with ROMs and tools can reproduce builds and source-change controls. It lacks
the historical emulator traces and review files needed to reproduce the
published acceptance decisions. Missing or stale review evidence blocks
acceptance even when the build matches.

The decisions are in `config/inventory-review-*.json`. The supporting technical
notes are in `docs/`. `make progress` rebuilds the selected target and verifies
all maintained proofs before refreshing the table above. Tooling tests use
synthetic data and need no ROM.

## Repository

| Path | Contents |
| --- | --- |
| `src/`, `include/` | Reconstructed assembly, scripts, data and shared symbols |
| `config/` | Target identities, layouts, tool pins and inventory decisions |
| `tools/`, `tests/` | Build and research tools; synthetic tooling tests |
| `assets/progress.json` | Verified PRG source counts |
| `docs/` | Supporting technical review notes |
| `licenses/` | Third-party attribution |

This is an owner-run project. It does not accept contributions, pull requests,
issues or support requests.

## Licence and credits

The original game's [NES credits are listed on MobyGames](https://www.mobygames.com/game/8520/bible-adventures/credits/nes/).

The [MIT licence](LICENSE.md) applies only to this project's original
copyrightable contributions. It grants no rights to the original game's code,
artwork, audio, text or trademarks, including original material represented in
reconstructed source. See [NOTICE.md](NOTICE.md) for the scope and third-party
attribution. This project is unaffiliated with Color Dreams, Wisdom Tree,
Cinemassacre or Nintendo.

The setup commands install these dependencies locally. The repository does not
bundle them:

| Dependency | Use | Licence |
| --- | --- | --- |
| [cc65 V2.19](https://github.com/cc65/cc65/tree/555282497c3ecf8b313d87d5973093af19c35bd5) | ca65 assembler, ld65 linker and da65 disassembler | [zlib](https://github.com/cc65/cc65/blob/555282497c3ecf8b313d87d5973093af19c35bd5/LICENSE) |
| [MesenCE 2.2.1](https://github.com/nesdev-org/MesenCE/releases/tag/2.2.1) | Optional emulator comparisons | [GPL-3.0-or-later](https://github.com/nesdev-org/MesenCE/blob/20ba206cef5ba207c21203176d02cb9f43dda9fb/LICENSE) |

Research references include the [NESdev Wiki](https://www.nesdev.org/wiki/Nesdev_Wiki),
[iNES](https://www.nesdev.org/wiki/INES), [NES 2.0](https://www.nesdev.org/wiki/NES_2.0),
[Color Dreams mapper documentation](https://www.nesdev.org/wiki/Color_Dreams),
and the [ca65](https://cc65.github.io/doc/ca65.html) and
[ld65](https://cc65.github.io/doc/ld65.html) manuals. Use of these tools does not
imply they were used for the original game. Exploratory TAS-derived inputs
are credited in [licenses/tasvideos-5223.md](licenses/tasvideos-5223.md).
