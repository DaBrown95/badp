"""Use the shared asset formats with a release's actual addresses and identity.

Inherited manifests describe formats and logical entries. Their translated
locations are decoded and checked against the selected target, never treated
as gameplay evidence from that target. No reference or emitted ROM is patched.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import (chr_assets, map_assets, map_data, map_layout_assets, menu_assets,
               palette_assets, ppu_assets, sprite_assets, text_assets)

MODULES = {'chr': chr_assets, 'map_chunks': map_assets, 'map_layouts': map_layout_assets,
           'packed_text': text_assets, 'menu_tiles': menu_assets, 'palettes': palette_assets,
           'ppu_tiles': ppu_assets, 'sprite_frames': sprite_assets}
MANIFESTS = {'sprite_frames': 'config/sprite-frames-us-v1.5.json',
             'palettes': 'config/palettes-us-v1.5.json', 'ppu_tiles': 'config/ppu-streams-us-v1.5.json'}


def options(root: Path, profile: dict) -> dict[str, dict]:
    layout, target = profile['geometry'], profile['target']
    result = {name: {'target': target} for name in MODULES}
    result['packed_text']['geometry'] = {
        'table_offset': layout.offset(1, text_assets.packed_text.TABLE_OFFSET),
        'data_end': layout.offset(1, text_assets.packed_text.DATA_END),
        'primary_offset': layout.offset(1, text_assets.packed_text.PRIMARY_OFFSET),
        'secondary_offset': layout.offset(1, text_assets.packed_text.SECONDARY_OFFSET)}
    result['map_chunks']['chunk_table_offset'] = layout.offset(0, map_data.CHUNK_TABLE_OFFSET)
    result['map_layouts']['geometry'] = {
        'state_table_offset': layout.offset(0, map_data.STATE_TABLE_OFFSET),
        'chunk_table_offset': layout.offset(0, map_data.CHUNK_TABLE_OFFSET)}
    result['menu_tiles']['geometry'] = {
        'commands': tuple((name, layout.address(1, cpu)) for name, cpu in menu_assets.COMMANDS),
        'region_start': layout.offset(1, menu_assets.REGION_START),
        'region_end': layout.offset(1, menu_assets.REGION_END)}
    for name, path in MANIFESTS.items():
        manifest = json.loads((root / path).read_text())
        if manifest['target'] != profile['canonical_target']:
            raise ValueError('asset manifest is not the canonical source layout')
        manifest['target'] = target
        manifest['source'] = ('Shared format entries translated to this target and decoded against its reference; '
                              'primary runtime observations do not verify this version.')
        if 'end_cpu' in manifest:
            _, end = layout.span(manifest['bank'], int(manifest['cpu_addresses'][0], 0), int(manifest['end_cpu'], 0))
            manifest['end_cpu'] = f'0x{end:04x}'
        if 'cpu_addresses' in manifest:
            bank = manifest['bank']
            manifest['cpu_addresses'] = [f'0x{layout.address(bank, int(value, 0)):04x}'
                                         for value in manifest['cpu_addresses']]
        if 'encoded_pointers' in manifest:
            translated = []
            for value in manifest['encoded_pointers']:
                pointer = int(value, 0)
                actual = layout.address(0, pointer) if pointer >= 0x8000 else layout.offset(1, pointer)
                translated.append(f'0x{actual:04x}')
            manifest['encoded_pointers'] = translated
        result[name]['manifest'] = manifest
    return result


def select(root: Path, prg: bytes, chr_data: bytes, reference: str, profile: dict) -> dict:
    if len(prg) != 65536 or len(chr_data) != 65536:
        raise ValueError('invalid variant asset geometry')
    settings = options(root, profile)
    selected = {}
    for name, module in MODULES.items():
        if name == 'chr':
            asset, payload, source, sha = module.select(root, chr_data, reference, **settings[name])
        else:
            asset, payload, source, sha = module.select(root, prg, reference, **settings[name])
        selected[name] = {'asset': asset, 'payload': payload, 'source': source, 'input_sha256': sha,
                          'options': settings[name]}
    return selected


def spans(selected: dict) -> dict[str, list[tuple[int, int, bytes]]]:
    result = {}
    for name, row in selected.items():
        if name == 'chr':
            continue
        result[name] = [(1, 0, row['payload'])] if name == 'map_chunks' else row['payload']
    return result


def encoded_gaps(prg: bytes, regions: list[dict], gaps: list[dict],
                 payloads: dict[str, list[tuple[int, int, bytes]]]) -> dict[str, bytes]:
    """Build every local gap only from decoded assets, preserving shared views.

    Source-owned overlaps must keep their source bytes. Overlapping asset views
    must agree. There is no reference-byte fallback for a missing asset extent.
    """
    if len(prg) != 65536:
        raise ValueError('invalid PRG geometry for asset gaps')
    owned = bytearray(65536)
    for row in regions:
        start = row['bank'] * 32768 + int(row['cpu'], 0) - 32768
        owned[start:start + row['size']] = bytes([1]) * row['size']
    flat = []
    for name, rows in payloads.items():
        for bank, offset, data in rows:
            if (bank not in (0, 1) or type(offset) is not int or not isinstance(data, bytes)
                    or not data or not 0 <= offset < offset + len(data) <= 32768):
                raise ValueError('invalid encoded asset span')
            absolute = bank * 32768 + offset
            if any(owned[absolute + i] and value != prg[absolute + i] for i, value in enumerate(data)):
                raise ValueError('asset edit conflicts with overlapping source bytes: ' + name)
            flat.append((bank, offset, data))
    result = {}
    for gap in gaps:
        start, size, bank = int(gap['cpu'], 0) - 32768, gap['size'], gap['bank']
        data, covered = bytearray(size), bytearray(size)
        for asset_bank, offset, payload in flat:
            if asset_bank != bank:
                continue
            low, high = max(start, offset), min(start + size, offset + len(payload))
            for position in range(low, high):
                index, value = position - start, payload[position - offset]
                if covered[index] and data[index] != value:
                    raise ValueError('overlapping local asset views disagree')
                data[index], covered[index] = value, 1
        if not all(covered):
            raise ValueError('unrepresented local asset bytes in ' + gap['name'])
        result[gap['name']] = bytes(data)
    return result


def changed_payload(name: str, root: Path, row: dict, prg: bytes, reference: str):
    module, settings = MODULES[name], row['options']
    changed = module.changed_asset(row['asset'], prg, geometry=settings.get('geometry')) if name == 'packed_text' else module.changed_asset(row['asset'])
    if name == 'chr':
        payload = module.encode(changed, reference, **settings)
    elif name in ('palettes', 'ppu_tiles', 'sprite_frames'):
        payload = module.encode(root, changed, prg, reference, **settings)
    else:
        payload = module.encode(changed, prg, reference, **settings)
    return changed, [(1, 0, payload)] if name == 'map_chunks' else payload
