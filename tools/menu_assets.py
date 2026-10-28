"""Round-trip local tile streams referenced by the v1.5 menu script.

The BOGUS $6E command supplies a banked pointer, PPU row, column, selector
and byte count. These locally supplied bytes are graphics data, not code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from .asset_paths import asset_path
import sys

from .script_entries import BANK_SIZE, ROOT, load_audited_banks

TARGET = 'us-v1.5'
ASSET_PATH = Path('extracted/us-v1.5/menu-tiles.json')
# Instruction locations, not payload bytes. Both branches of ScriptF176 are
# represented; whether a particular path executes remains context-dependent.
COMMANDS = (('tile_row_0', 0xf187), ('tile_row_1', 0xf18e), ('tile_row_2', 0xf195),
            ('tile_row_3', 0xf19c), ('copyright', 0xf1a3), ('brand', 0xf1aa),
            ('brand_tail', 0xf1b1), ('game_marker', 0xf1c4), ('noah', 0xf1cb),
            ('moses', 0xf1d2), ('david', 0xf1d9), ('restart', 0xf1e8),
            ('continue', 0xf1ef), ('different_game', 0xf1f6))
REGION_START, REGION_END = 0x7357, 0x7401


def inventory(prg: bytes, *, region_start: int = REGION_START, region_end: int = REGION_END,
              commands: tuple = COMMANDS) -> list[dict]:
    """Derive bounded, disjoint streams from audited BOGUS command bytes."""
    if len(prg) != 2 * BANK_SIZE:
        raise ValueError('expected two complete PRG banks')
    if (any(type(n) is not int for n in (region_start, region_end))
            or not 0 <= region_start < region_end <= BANK_SIZE or not commands
            or len({name for name, _ in commands}) != len(commands)
            or len({cpu for _, cpu in commands}) != len(commands)
            or any(not isinstance(name, str) or not name or type(cpu) is not int
                   or not 0x8000 <= cpu <= 0xfff9 for name, cpu in commands)):
        raise ValueError('invalid menu layout geometry')
    bank = prg[BANK_SIZE:]
    result = []
    for name, cpu in commands:
        offset = cpu - 0x8000
        command = bank[offset:offset + 7]
        if len(command) != 7 or command[0] != 0x6e:
            raise ValueError('menu display command is missing or truncated')
        pointer = int.from_bytes(command[1:3], 'little')
        row, column, selector, count = command[3:7]
        if not count or not region_start <= pointer < pointer + count <= region_end:
            raise ValueError('menu display stream leaves the reviewed region')
        result.append({'name': name, 'command_cpu': cpu, 'pointer': pointer, 'row': row,
                       'column': column, 'selector': selector, 'count': count})
    expected = region_start
    for item in sorted(result, key=lambda x: x['pointer']):
        if item['pointer'] != expected:
            raise ValueError('menu display streams overlap or leave a gap')
        expected += item['count']
    if expected != region_end:
        raise ValueError('menu display streams do not cover the reviewed region')
    return result


def capture(prg: bytes, reference_sha256: str, *, target: str = TARGET, geometry: dict | None = None) -> dict:
    if not isinstance(reference_sha256, str) or len(reference_sha256) != 64:
        raise ValueError('invalid reference identity')
    entries = []
    for item in inventory(prg, **(geometry or {})):
        start = BANK_SIZE + item['pointer']
        entries.append({'name': item['name'], 'command_cpu': f"0x{item['command_cpu']:04x}",
                        'source_cpu': f"0x{item['pointer'] + 0x8000:04x}", 'row': item['row'],
                        'column': item['column'], 'selector': item['selector'],
                        'tiles': list(prg[start:start + item['count']])})
    return {'schema_version': 1, 'target': target, 'reference_sha256': reference_sha256,
            'bank': 1, 'streams': entries}


def encode(asset: dict, prg: bytes, reference_sha256: str, *, target: str = TARGET,
           geometry: dict | None = None) -> list[tuple[int, int, bytes]]:
    if (not isinstance(asset, dict) or set(asset) != {'schema_version', 'target', 'reference_sha256', 'bank', 'streams'}
            or type(asset['schema_version']) is not int or asset['schema_version'] != 1
            or asset['target'] != target or asset['reference_sha256'] != reference_sha256
            or type(asset['bank']) is not int or asset['bank'] != 1 or not isinstance(asset['streams'], list)):
        raise ValueError('menu asset identity differs from the reference')
    originals = inventory(prg, **(geometry or {}))
    if len(asset['streams']) != len(originals):
        raise ValueError('menu stream count differs from the reviewed commands')
    spans = []
    for entry, original in zip(asset['streams'], originals):
        if (not isinstance(entry, dict) or set(entry) != {'name', 'command_cpu', 'source_cpu', 'row', 'column', 'selector', 'tiles'}
                or entry['name'] != original['name'] or entry['command_cpu'] != f"0x{original['command_cpu']:04x}"
                or entry['source_cpu'] != f"0x{original['pointer'] + 0x8000:04x}"
                or any(type(entry[key]) is not int or entry[key] != original[key] for key in ('row', 'column', 'selector'))
                or not isinstance(entry['tiles'], list) or len(entry['tiles']) != original['count']
                or any(type(tile) is not int or not 0 <= tile <= 255 for tile in entry['tiles'])):
            raise ValueError('menu stream identity, layout or tile values differ')
        spans.append((1, original['pointer'], bytes(entry['tiles'])))
    return spans


def serialize(asset: dict) -> bytes:
    return (json.dumps(asset, indent=2) + '\n').encode('utf-8')


def select(root: Path, prg: bytes, reference_sha256: str, *, target: str = TARGET,
           geometry: dict | None = None) -> tuple[dict, list[tuple[int, int, bytes]], str, str]:
    path = root / asset_path(target, ASSET_PATH.name)
    if (root / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError('refusing a symlinked menu asset input')
    if path.exists():
        raw = path.read_bytes()
        asset, source = json.loads(raw), 'local'
    else:
        asset = capture(prg, reference_sha256, target=target, geometry=geometry)
        raw, source = serialize(asset), 'reference'
    return asset, encode(asset, prg, reference_sha256, target=target, geometry=geometry), source, hashlib.sha256(raw).hexdigest()


def changed_asset(asset: dict) -> dict:
    changed = json.loads(json.dumps(asset))
    if not changed['streams']:
        raise ValueError('menu control has no streams')
    for stream in changed['streams']:
        if not stream['tiles']:
            raise ValueError('menu control stream has no tiles')
        stream['tiles'][0] ^= 1
    return changed


def verify_control(reference: bytes, candidate: bytes, prg_offset: int, asset: dict) -> list[int]:
    if len(reference) != len(candidate):
        raise ValueError('menu control changed ROM size')
    expected = sorted(prg_offset + BANK_SIZE + int(x['source_cpu'], 16) - 0x8000 for x in asset['streams'])
    changed = [i for i, (a, b) in enumerate(zip(reference, candidate)) if a != b]
    if (len(expected) != len(set(expected)) or changed != expected
            or any(candidate[i] != (reference[i] ^ 1) for i in expected)):
        raise ValueError('menu control did not change exactly one tile per stream')
    return changed


def main() -> int:
    try:
        target, bank0, bank1, _ = load_audited_banks()
        asset = capture(bank0 + bank1, target['reference']['file']['sha256'])
        data = serialize(asset)
        path = ROOT / ASSET_PATH
        if (ROOT / 'extracted').is_symlink() or path.parent.is_symlink() or path.is_symlink():
            raise ValueError('refusing a symlinked menu asset output')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('local menu data already exists and differs; preserve or move it before exporting')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.resolve().is_relative_to((ROOT / 'extracted').resolve()):
            raise ValueError('menu asset output escapes the extracted directory')
        if not path.exists():
            path.write_bytes(data)
        print(json.dumps({'target': TARGET, 'streams': len(asset['streams']),
                          'tile_bytes': sum(len(s['tiles']) for s in asset['streams']),
                          'output': str(ASSET_PATH)}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f'menu asset export failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
