"""Encode this release's required local editable inputs, with no opaque gaps."""
from __future__ import annotations

import json
from pathlib import Path

from . import chr_assets, map_assets, map_layout_assets, menu_assets, palette_assets, ppu_assets, sprite_assets
from .build_rom import digest

GROUPS = ('map-chunks', 'map-layouts', 'sprite-frames', 'palettes',
          'ppu-message-tiles', 'ppu-inventory-tiles', 'menu-tiles',
          'chr-tiles', 'retained-resource-tile')
INPUTS = ('tools/unversioned_assets.py', 'tools/chr_assets.py', 'tools/map_assets.py',
          'tools/map_data.py', 'tools/map_layout_assets.py', 'tools/menu_assets.py',
          'tools/palette_assets.py', 'tools/ppu_assets.py', 'tools/ppu_streams.py',
          'tools/sprite_assets.py', 'tools/sprite_metadata.py', 'tools/asset_paths.py',
          'config/maps-us-unversioned.json', 'config/menu-us-unversioned.json',
          'config/palettes-us-unversioned.json', 'config/sprite-frames-us-unversioned.json',
          'config/ppu-messages-us-unversioned.json', 'config/ppu-inventory-us-unversioned.json')


def capture(root: Path, reference: bytes) -> dict:
    """Decode only the supported asset formats; never export an opaque gap."""
    from .sprite_metadata import decode_frame_header
    prg, identity = reference[16:65552], digest(reference)
    maps = json.loads((root / 'config/maps-us-unversioned.json').read_text())
    result = {
        'map-chunks': map_assets.capture(prg, identity, target='us-unversioned',
             chunk_table_offset=0x232d, geometry=maps['chunk_assets']),
        'map-layouts': map_layout_assets.capture(prg, identity, target='us-unversioned', geometry=maps['layout_assets']),
        'chr-tiles': chr_assets.capture(reference[65552:], identity, target='us-unversioned'),
    }
    for name, module in (('sprite-frames', sprite_assets), ('palettes', palette_assets)):
        manifest = json.loads((root / f'config/{name}-us-unversioned.json').read_text())
        result[name] = module.capture(root, prg, identity, target='us-unversioned', manifest=manifest)
    for name, key in (('messages', 'message'), ('inventory', 'inventory')):
        manifest = json.loads((root / f'config/ppu-{name}-us-unversioned.json').read_text())
        result[f'ppu-{key}-tiles'] = ppu_assets.capture(root, prg, identity, target='us-unversioned', manifest=manifest)
    geometry = json.loads((root / 'config/menu-us-unversioned.json').read_text())['geometry']
    result['menu-tiles'] = menu_assets.capture(prg, identity, target='us-unversioned', geometry=geometry)
    frame = prg[0xfc39:0xfc3e]
    decoded = decode_frame_header(frame, header_format='separate-bytes')
    if frame != prg[0x3a8d:0x3a92] or decoded['tile_read_offsets'] != [3, 4]:
        raise ValueError('retained resource lacks the reviewed complete frame format')
    result['retained-resource-tile'] = {'schema_version': 1, 'target': 'us-unversioned',
        'reference_sha256': identity, 'format': 'sprite-tile-attribute-pair', 'tiles': list(frame[3:])}
    return result


def ensure_inputs(root: Path, reference: bytes) -> None:
    """Create missing decoded inputs locally, preserving every existing edit."""
    folder = root / 'extracted/us-unversioned'
    if any(p.is_symlink() for p in (root / 'extracted', folder)):
        raise ValueError('refusing a symlinked own editable-input folder')
    missing = [name for name in GROUPS if not (folder / (name + '.json')).exists()]
    if not missing:return
    decoded = capture(root, reference)
    folder.mkdir(parents=True, exist_ok=True)
    for name in missing:
        path = folder / (name + '.json')
        if path.is_symlink():raise ValueError('refusing a symlinked own editable input')
        with path.open('x') as handle:
            json.dump(decoded[name], handle, indent=2)
            handle.write('\n')


def load(root: Path) -> tuple[dict, dict]:
    assets, hashes = {}, {}
    for name in GROUPS:
        path = root / f'extracted/us-unversioned/{name}.json'
        if any(p.is_symlink() for p in (root / 'extracted', path.parent, path)):
            raise ValueError('refusing a symlinked own editable input')
        raw = path.read_bytes()
        assets[name], hashes[str(path.relative_to(root))] = json.loads(raw), digest(raw)
    return assets, hashes


def encode(root: Path, assets: dict, reference: bytes) -> dict[str, bytes]:
    if set(assets) != set(GROUPS):raise ValueError('missing own editable input group')
    prg, identity = reference[16:65552], digest(reference)
    files = {}
    maps = json.loads((root / 'config/maps-us-unversioned.json').read_text())
    files['unversioned-map-chunks.bin'] = map_assets.encode(assets['map-chunks'], prg, identity,
        target='us-unversioned', chunk_table_offset=0x232d, geometry=maps['chunk_assets'])
    for bank, offset, data in map_layout_assets.encode(assets['map-layouts'], prg, identity,
            target='us-unversioned', geometry=maps['layout_assets']):
        files[f'unversioned-map-layout-{bank}-{offset + 32768 - 2:04x}.bin'] = data
    for name, module in (('sprite-frames', sprite_assets), ('palettes', palette_assets)):
        manifest = json.loads((root / f'config/{name}-us-unversioned.json').read_text())
        for i, (bank, offset, data) in enumerate(module.encode(root, assets[name], prg, identity,
                target='us-unversioned', manifest=manifest)):
            if bank != 0:raise ValueError('own bank0 asset changed bank')
            filename = f'unversioned-sprite-{i:03d}.bin' if name == 'sprite-frames' else f'unversioned-palette-{i:02d}.bin'
            files[filename] = data[3:] if name == 'sprite-frames' else data
    for name, key in (('messages', 'message'), ('inventory', 'inventory')):
        manifest = json.loads((root / f'config/ppu-{name}-us-unversioned.json').read_text())
        spans = ppu_assets.encode(root, assets[f'ppu-{key}-tiles'], prg, identity,
                                 target='us-unversioned', manifest=manifest)
        if key == 'inventory':
            for bank, offset, data in spans:
                if bank != 1:raise ValueError('own inventory payload changed bank')
                files[f'unversioned-ppu-inventory-{offset + 32768:04x}.bin'] = data
        else:
            by_offset = {offset: data for bank, offset, data in spans if bank == 1}
            for i, stream in enumerate(ppu_assets.inventory(root, prg, target='us-unversioned', manifest=manifest)):
                for j, segment in enumerate(stream['segments']):
                    if segment['kind'] == 'payload':
                        files[f'unversioned-message-{i:02d}-{j:02d}.bin'] = by_offset[stream['location']['bank_offset'] + segment['offset']]
    geometry = json.loads((root / 'config/menu-us-unversioned.json').read_text())['geometry']
    rows = menu_assets.encode(assets['menu-tiles'], prg, identity, target='us-unversioned', geometry=geometry)
    files['unversioned-menu-tiles.bin'] = b''.join(data for bank, offset, data in sorted(rows, key=lambda row: row[1]))
    files['chr.bin'] = chr_assets.encode(assets['chr-tiles'], identity, target='us-unversioned')
    tile = assets['retained-resource-tile']
    if (not isinstance(tile, dict) or set(tile) != {'schema_version', 'target', 'reference_sha256', 'format', 'tiles'}
            or type(tile['schema_version']) is not int or tile['schema_version'] != 1
            or tile['target'] != 'us-unversioned' or tile['reference_sha256'] != identity
            or tile['format'] != 'sprite-tile-attribute-pair'
            or not isinstance(tile['tiles'], list) or len(tile['tiles']) != 2
            or any(type(value) is not int or not 0 <= value <= 255 for value in tile['tiles'])):
        raise ValueError('invalid retained resource tile input')
    files['unversioned-retained-resource-tile.bin'] = bytes(tile['tiles'])
    return files


def changed(root: Path, assets: dict, group: str) -> dict:
    if group not in GROUPS:raise ValueError('unknown own asset control')
    result = dict(assets)
    module = {'map-chunks': map_assets, 'map-layouts': map_layout_assets,
              'sprite-frames': sprite_assets, 'palettes': palette_assets,
              'ppu-message-tiles': ppu_assets, 'ppu-inventory-tiles': ppu_assets,
              'menu-tiles': menu_assets, 'chr-tiles': chr_assets}.get(group)
    if group == 'map-chunks':
        geometry = json.loads((root / 'config/maps-us-unversioned.json').read_text())['chunk_assets']
        result[group] = module.changed_asset(assets[group], geometry=geometry)
    elif module is not None:result[group] = module.changed_asset(assets[group])
    else:
        result[group] = {**assets[group], 'tiles': [value ^ 1 for value in assets[group]['tiles']]}
    return result
