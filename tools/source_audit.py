"""Account for every physical PRG byte, retaining unresolved competing uses.

This is a completion worklist, not a new source-progress metric. A reversible
asset encoding proves a representation, not exclusive use as non-executable
data. Candidate script decodes must remain visible even inside artwork.
"""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import sys

from . import map_assets, map_layout_assets, menu_assets, palette_assets, ppu_assets, sprite_assets, text_assets
from .build_rom import digest
from .identify_rom import inspect_rom
from .inventory_review import apply_review
from .prg_inventory import CATEGORIES, inventory
from .progress import verify_primary
from .project import IDENTITY_PARTS, load_project, load_target
from .script_entries import BANK_SIZE, ROOT, load_audited_banks

INPUTS = ('tools/source_audit.py', 'tools/map_assets.py', 'tools/map_layout_assets.py', 'tools/asset_paths.py',
          'tools/inventory_review.py', 'config/inventory-review-us-v1.5.json',
          'tools/menu_assets.py', 'tools/palette_assets.py', 'tools/ppu_assets.py', 'tools/ppu_streams.py', 'config/ppu-streams-us-v1.5.json', 'config/palettes-us-v1.5.json', 'tools/sprite_assets.py', 'tools/text_assets.py',
          'config/sprite-frames-us-v1.5.json')


def partition(evidence: list[dict], assets: dict[str, list[tuple[int, int]]],
              *, bank_size: int = BANK_SIZE, bank_count: int = 2) -> dict:
    """Intersect complete evidence runs with asset spans without double credit."""
    if (type(bank_size) is not int or bank_size <= 0
            or type(bank_count) is not int or bank_count <= 0):
        raise ValueError('invalid audit geometry')
    size = bank_size * bank_count
    uses: list[tuple[str, ...]] = [()] * size
    local_assets: list[set[str]] = [set() for _ in range(size)]
    cursor = 0
    for span in evidence:
        start, length, names = span['physical_prg_offset'], span['size'], span['uses']
        if (type(start) is not int or type(length) is not int or start != cursor or length <= 0
                or start + length > size or start // bank_size != (start + length - 1) // bank_size
                or span['bank'] != start // bank_size
                or span['cpu_start'] != f'0x{0x8000 + start % bank_size:04x}'
                or not isinstance(names, list) or any(n not in CATEGORIES for n in names)
                or len(names) != len(set(names))
                or len(set(names) & {'source_code', 'source_data', 'source_fill'}) > 1):
            raise ValueError('invalid or incomplete physical evidence partition')
        uses[start:start + length] = [tuple(names)] * length
        cursor += length
    if cursor != size:
        raise ValueError('physical evidence partition omits bytes')
    for name, spans in assets.items():
        if not isinstance(name, str) or not name:
            raise ValueError('invalid local asset name')
        for start, length in spans:
            if (type(start) is not int or type(length) is not int or start < 0 or length <= 0
                    or start + length > size or start // bank_size != (start + length - 1) // bank_size):
                raise ValueError('local asset span crosses a bank or lies outside PRG')
            for offset in range(start, start + length):
                local_assets[offset].add(name)
    rows = []
    for bank in range(bank_count):
        cursor, end = bank * bank_size, (bank + 1) * bank_size
        while cursor < end:
            start = cursor
            key = uses[cursor], local_assets[cursor]
            while cursor < end and (uses[cursor], local_assets[cursor]) == key:
                cursor += 1
            names, asset_names = key
            ownership = ('source_code' if 'source_code' in names else
                         'source_data' if 'source_data' in names else
                         'source_fill' if 'source_fill' in names else
                         'local_asset' if asset_names else 'unresolved_local')
            rows.append({'bank': bank, 'cpu_start': f'0x{0x8000 + start % bank_size:04x}',
                         'physical_prg_offset': start, 'size': cursor - start,
                         'representation': ownership, 'local_assets': sorted(asset_names),
                         'evidence_uses': list(names),
                         'review_status': 'unreviewed', 'review_decisions': []})
    counts: Counter = Counter()
    for row in rows:
        counts[row['representation']] += row['size']
    return {'prg_bytes': size, 'representation_bytes': dict(sorted(counts.items())),
            'regions': rows, 'complete_executable_inventory': all(
                row['review_status'] == 'reviewed' for row in rows)}


def asset_spans(root: Path, prg: bytes, reference: str) -> dict[str, list[tuple[int, int]]]:
    """Only encodings already covered by the full build's asset controls."""
    result = {'map_chunks': [(BANK_SIZE + slot * map_assets.CHUNK_SIZE, map_assets.CHUNK_SIZE)
                             for slot in sorted(map_assets.slots_for_reference(prg))],
              'unreferenced_map_duplicate': [(BANK_SIZE + map_assets.duplicate_slot(prg) * map_assets.CHUNK_SIZE,
                                               map_assets.CHUNK_SIZE)]}
    for name, module in (('map_layouts', map_layout_assets), ('packed_text', text_assets),
                         ('menu_tiles', menu_assets)):
        _, spans, _, _ = module.select(root, prg, reference)
        result[name] = [(bank * BANK_SIZE + offset, len(data)) for bank, offset, data in spans]
    _, spans, _, _ = palette_assets.select(root, prg, reference)
    result['palette_colours'] = [(bank * BANK_SIZE + offset, len(data)) for bank, offset, data in spans]
    _, spans, _, _ = ppu_assets.select(root, prg, reference)
    result['ppu_tile_payloads'] = [(bank * BANK_SIZE + offset, len(data)) for bank, offset, data in spans]
    _, spans, _, _ = sprite_assets.select(root, prg, reference)
    result['inventoried_sprite_frames'] = [(bank * BANK_SIZE + offset, len(data))
                                         for bank, offset, data in spans]
    return result


def compare_regions(primary: bytes, others: dict[str, bytes], regions: list[dict],
                    *, minimum_size: int = 8) -> list[dict]:
    """Search whole opaque runs across revisions; offsets alone imply no meaning.

    Small fragments are deliberately omitted. Identical occurrences can be
    overlapping or numerous; a common repeated pattern is not a unique match.
    """
    if type(minimum_size) is not int or minimum_size <= 0:
        raise ValueError('invalid comparison minimum size')
    runs = []
    for row in regions:
        if row['representation'] != 'unresolved_local':
            continue
        start, size = row['physical_prg_offset'], row['size']
        if start < 0 or size <= 0 or start + size > len(primary):
            raise ValueError('invalid comparative region')
        if runs and runs[-1]['bank'] == row['bank'] and runs[-1]['start'] + runs[-1]['size'] == start:
            runs[-1]['size'] += size
        else:
            runs.append({'bank': row['bank'], 'start': start, 'size': size})
    result = []
    for run in runs:
        if run['size'] < minimum_size:
            continue
        payload = primary[run['start']:run['start'] + run['size']]
        matches = {}
        for target, prg in others.items():
            positions, count, cursor = [], 0, 0
            while True:
                position = prg.find(payload, cursor)
                if position < 0:
                    break
                count += 1
                if len(positions) < 16:
                    positions.append(position)
                cursor = position + 1
            matches[target] = {'exact_occurrences': count,
                               'first_physical_prg_offsets': positions}
        result.append({'bank': run['bank'], 'physical_prg_offset': run['start'],
                       'size': run['size'], 'sha256': digest(payload), 'revisions': matches})
    return result


def main() -> int:
    try:
        selected = os.environ.get('BADP_TARGET') or 'us-v1.5'
        if selected != 'us-v1.5':
            from .verify_variant import verify
            from .variant_inventory import review
            target = load_target(ROOT, selected)
            verify(ROOT, target)
            proof = json.loads((ROOT / 'build' / selected / 'proof.json').read_text())
            result = review(ROOT, target, proof, (ROOT / target['input_path']).read_bytes())
            print(json.dumps({'target': selected, 'representation_bytes': result['representation_bytes'],
                              'inventory_review': result['inventory_review']}, indent=2))
            return 0
        hashes = {name: digest((ROOT / name).read_bytes()) for name in INPUTS}
        combined = inventory()
        target, bank0, bank1, _ = load_audited_banks()
        reference = target['reference']['file']['sha256']
        if combined['reference_sha256'] != reference:
            raise ValueError('inventory reference changed')
        result = partition(combined['evidence_spans'], asset_spans(ROOT, bank0 + bank1, reference))
        revisions, revision_identities = {}, {}
        for target_id in load_project(ROOT)['target_order']:
            if target_id == 'us-v1.5':
                continue
            manifest = load_target(ROOT, target_id)
            rom = (ROOT / manifest['input_path']).read_bytes()
            actual = inspect_rom(rom)
            if any(actual[part] != manifest['reference'][part] for part in IDENTITY_PARTS):
                raise ValueError('comparative ROM differs from reviewed identity')
            offset, size = actual['prg']['offset'], actual['prg']['size']
            revisions[target_id] = rom[offset:offset + size]
            revision_identities[target_id] = actual['file']['sha256']
        result['comparative_references'] = revision_identities
        result['opaque_run_comparisons'] = compare_regions(bank0 + bank1, revisions, result['regions'])
        # Preserve conditional contexts without treating every speculative
        # decode as another missing implementation. The review ledger names
        # concrete completion blockers separately.
        result.update(schema_version=1, target='us-v1.5', reference_sha256=reference,
                      source_sha256=combined['source_sha256'],
                      source_map_sha256=combined['source_map_sha256'],
                      build_proof_sha256=combined['build_proof_sha256'],
                      inventory_input_sha256=combined['inventory_input_sha256'],
                      audit_input_sha256=hashes, optional_traces=combined['optional_traces'],
                      uncatalogued_bytes=combined['uncatalogued_bytes'],
                      conditional_context_counts={k: combined[k] for k in (
                          'direct_incomplete_observed_indexed_jumps',
                          'direct_incomplete_predecessor_indexed_jumps',
                          'static_sprite_crossings', 'static_sprite_non_rom_resources',
                          'static_sprite_non_rom_frames', 'audio_fetches_crossing_bank')},
                      interpretation='Representation counts are disjoint physical bytes, not executable '
                      'coverage or a completion percentage. Source ownership wins only for this '
                      'accounting; all candidate uses and asset overlaps remain in each region. '
                      'Review decisions allow overlapping uses and are bound to the reviewed inputs.')
        result = apply_review(result, json.loads((ROOT / 'config/inventory-review-us-v1.5.json').read_text()), ROOT)
        verified = verify_primary(ROOT, target)
        if (verified['source_sha256'] != combined['source_sha256']
                or verified['source_map_sha256'] != combined['source_map_sha256']
                or digest((ROOT / 'build/us-v1.5/proof.json').read_bytes()) != combined['build_proof_sha256']
                or hashes != {name: digest((ROOT / name).read_bytes()) for name in INPUTS}):
            raise ValueError('audit inputs changed')
        output = ROOT / 'analysis/us-v1.5/source-audit.json'
        if (ROOT / 'analysis').is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'representation_bytes': result['representation_bytes'],
                          'inventory_review': result['inventory_review'],
                          'regions': len(result['regions']),
                          'conditional_context_counts': result['conditional_context_counts'],
                          'output': 'analysis/us-v1.5/source-audit.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'source audit failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
