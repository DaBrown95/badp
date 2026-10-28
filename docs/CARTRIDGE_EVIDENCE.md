# Cartridge-profile corroboration

The target names follow the pinned No-Intro catalogue. Separately, the PRG,
CHR and combined PRG+CHR CRC-32 values of the six audited local inputs match
the values reported in these NesCartDB cartridge profiles, accessed 2026-10-28.
The local SHA-1 and SHA-256 pins remain the reference authority; CRC-32 is not
a cryptographic identity proof and a catalogue profile does not inspect the
owner's cartridge. The local comparison and per-file SHA-256 receipts are in
ignored `analysis/us-v1.5/cartridge-profile-comparison.json`.

| Target | Profile label | PRG CRC-32 | CHR CRC-32 | Combined CRC-32 | Profiled board |
| --- | --- | --- | --- | --- | --- |
| USA v1.5 | [Version 5.0](https://nescartdb.com/profile/view/4773/bible-adventures) | `663A15A3` | `1C05428A` | `8E011A8B` | BC5 |
| USA v1.4 | [Version 1.4](https://nescartdb.com/profile/view/958/bible-adventures) | `E571615D` | `1C05428A` | `680DA78D` | BC6 |
| USA v1.3 | [Version 1.3](https://nescartdb.com/profile/view/1015/bible-adventures) | `9B8E02C0` | `B0A8C32A` | `73140EEF` | BC6 |
| USA v1.2 | [Version 1.2](https://nescartdb.com/profile/view/1364/bible-adventures) | `3B73C254` | `BC62F3F3` | `7F24EFC0` | UNK-COLORDREAMS-REVB |
| USA v1.1 | [Version 1.1](https://nescartdb.com/profile/view/2117/bible-adventures) | `306554E5` | `D247B206` | `73C246D4` | UNK-COLORDREAMS-REVA |
| USA unversioned | [Unversioned](https://nescartdb.com/profile/view/1157/bible-adventures) | `07016AD0` | `E1BB9C64` | `40A5E676` | UNK-COLORDREAMS-REVA |

The v1.5 / Version 5.0 naming difference is preserved rather than silently
renaming the target. The local v1.5 menu stream also contains a version 5.0
label; this supports the correspondence but does not establish why the two
catalogues use different revision names.

The profiles report mapper 11, vertical mirroring and 74xx377 hardware for
their respective samples. The v1.5 profile identifies an LS377 and 4051,
while the v1.4 profile identifies an LS377 and a 7660. These are observations
reported for those particular catalogued boards, not proof of every board's
wiring or of the owner's physical hardware. In particular, they do not prove
reset bank state, bus-conflict behaviour, mapper timing or the meaning of a
header's submapper field. Target hardware verification remains unverified.
