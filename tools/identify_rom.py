"""Read-only iNES/NES 2.0 layout inspection; no release identification or pinning.

Format references:
https://www.nesdev.org/wiki/INES
https://www.nesdev.org/wiki/NES_2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def hashes(data: bytes) -> dict:
    return {
        "size": len(data),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def rom_size(lsb: int, msb: int, unit: int) -> int:
    if msb == 0x0F:
        return (1 << (lsb >> 2)) * (2 * (lsb & 3) + 1)
    return ((msb << 8) | lsb) * unit


def inspect_rom(data: bytes) -> dict:
    if len(data) < 16:
        raise ValueError("ROM is shorter than the 16-byte NES header")
    header = data[:16]
    if header[:4] != b"NES\x1a":
        raise ValueError("expected an iNES or NES 2.0 container (NES magic missing)")

    variant = header[7] & 0x0C
    if variant not in (0, 8):
        raise ValueError("unrecognised NES header format bits; inspect the header manually")
    nes2 = variant == 8
    mapper = (header[6] >> 4) | (header[7] & 0xF0)
    submapper = None
    notes = []
    if nes2:
        mapper |= (header[8] & 0x0F) << 8
        submapper = header[8] >> 4
        prg_size = rom_size(header[4], header[9] & 0x0F, 16384)
        chr_size = rom_size(header[5], header[9] >> 4, 8192)
    else:
        prg_size = header[4] * 16384
        chr_size = header[5] * 8192
        if any(header[11:16]):
            notes.append("Legacy header has nonzero padding; mapper/other fields may be unreliable.")

    trainer_size = 512 if header[6] & 4 else 0
    payload_start = 16 + trainer_size
    payload_end = payload_start + prg_size + chr_size
    if prg_size == 0:
        raise ValueError("header declares no PRG ROM")
    if len(data) < payload_end:
        raise ValueError(
            f"truncated ROM: header requires at least {payload_end} bytes, found {len(data)}"
        )

    def section(start: int, size: int) -> dict:
        return {"offset": start, **hashes(data[start:start + size])}

    if payload_end < len(data):
        notes.append("Trailing bytes are reported separately; their purpose has not been classified.")
    return {
        "schema_version": 1,
        "file": hashes(data),
        "header_claims": {
            "format": "NES 2.0" if nes2 else "iNES",
            "hex": header.hex(),
            "mapper": mapper,
            "submapper": submapper,
        },
        "trainer": section(16, trainer_size),
        "prg": section(payload_start, prg_size),
        "chr": section(payload_start + prg_size, chr_size),
        "prg_chr": section(payload_start, prg_size + chr_size),
        "trailing": section(payload_end, len(data) - payload_end),
        "notes": notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "rom", nargs="?", type=Path,
        default=Path(os.environ.get("BADP_ROM", "baseroms/bible-adventures.nes")),
        help="local ROM path (default: BADP_ROM or baseroms/bible-adventures.nes)",
    )
    args = parser.parse_args()
    try:
        result = inspect_rom(args.rom.read_bytes())
    except (OSError, ValueError) as exc:
        print(f"ROM inspection failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
