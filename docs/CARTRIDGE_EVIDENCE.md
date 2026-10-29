# Cartridge profile checks

The target names follow the pinned No-Intro catalogue. The PRG, CHR and combined
PRG+CHR CRC-32 values of all six audited local inputs also match these NesCartDB
cartridge profiles, accessed 2026-10-28. The local SHA-1 and SHA-256 pins identify
the references used by this project. A CRC-32 match does not prove identical
contents, and a catalogue profile does not inspect the owner's cartridge.
The comparison and per-file SHA-256 receipts are in the ignored file
`analysis/us-v1.5/cartridge-profile-comparison.json`.

| Target | Profile label | PRG CRC-32 | CHR CRC-32 | Combined CRC-32 | Profiled board |
| --- | --- | --- | --- | --- | --- |
| USA v1.5 | [Version 5.0](https://nescartdb.com/profile/view/4773/bible-adventures) | `663A15A3` | `1C05428A` | `8E011A8B` | BC5 |
| USA v1.4 | [Version 1.4](https://nescartdb.com/profile/view/958/bible-adventures) | `E571615D` | `1C05428A` | `680DA78D` | BC6 |
| USA v1.3 | [Version 1.3](https://nescartdb.com/profile/view/1015/bible-adventures) | `9B8E02C0` | `B0A8C32A` | `73140EEF` | BC6 |
| USA v1.2 | [Version 1.2](https://nescartdb.com/profile/view/1364/bible-adventures) | `3B73C254` | `BC62F3F3` | `7F24EFC0` | UNK-COLORDREAMS-REVB |
| USA v1.1 | [Version 1.1](https://nescartdb.com/profile/view/2117/bible-adventures) | `306554E5` | `D247B206` | `73C246D4` | UNK-COLORDREAMS-REVA |
| USA unversioned | [Unversioned](https://nescartdb.com/profile/view/1157/bible-adventures) | `07016AD0` | `E1BB9C64` | `40A5E676` | UNK-COLORDREAMS-REVA |

The target keeps No-Intro's v1.5 name. The local v1.5 menu stream also contains
a version 5.0 label, which supports the match to the Version 5.0 profile. The
reason for the different catalogue names remains unknown.

The profiles report mapper 11, vertical mirroring and 74xx377 hardware for
their samples. The v1.5 profile identifies an LS377 and 4051. The v1.4 profile
identifies an LS377 and a 7660. These observations apply to those catalogued
boards. They do not establish the wiring of every board or the owner's hardware.
They also do not prove reset bank state, bus-conflict behaviour, mapper timing
or the meaning of a header's submapper field. Those hardware details remain
unverified for the project's targets.
