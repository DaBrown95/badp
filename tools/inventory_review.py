"""Apply explicit, input-bound inventory decisions without requiring exclusive use.

A source representation, a reviewed mechanism and a resolved storage group are
different gates. A decision cannot hide opaque bytes or omit a required gate.
"""
from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path, PurePosixPath

MECHANISMS = frozenset(('native-entry-and-transfers', 'bank-transitions', 'bogus-successors',
                        'slot-resources', 'audio', 'asset-formats'))
REPRESENTATION_GATES = {
    'source_code': ('native-entry-and-transfers', 'bank-transitions'),
    'source_data': ('bogus-successors', 'slot-resources', 'audio'),
    'source_fill': ('bank-transitions',), 'local_asset': ('asset-formats',)}


def evidence_valid(root: Path, entry: dict) -> bool:
    name = entry.get('path', '')
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or '..' in path.parts or str(path) != name
            or not isinstance(entry.get('scope'), str) or not entry['scope'].strip()
            or not isinstance(entry.get('sha256'), str) or len(entry['sha256']) != 64):
        raise ValueError('invalid review evidence reference')
    full = root / name
    if not full.resolve().is_relative_to(root.resolve()) or full.is_symlink():
        raise ValueError('review evidence escapes workspace')
    return full.is_file() and hashlib.sha256(full.read_bytes()).hexdigest() == entry['sha256']


def apply_review(result: dict, ledger: dict, root: Path) -> dict:
    """Return a reviewed audit, failing closed on stale or missing evidence.

    Source/reference/map identity binds the review to its actual representation.
    Evidence may predate a rebuild when its documented scope remains unchanged.
    Every referenced artifact must still have the reviewed content hash.
    """
    if ledger.get('schema_version') != 1 or ledger.get('target') != result.get('target'):
        raise ValueError('invalid inventory review identity')
    bound = all(ledger.get(k) == result.get(k) for k in
                ('reference_sha256', 'source_sha256', 'source_map_sha256'))
    # Bind the interpretation inputs as well as emitted source. The ledger's
    # own hash is omitted to avoid a circular fingerprint.
    inputs = {**result.get('inventory_input_sha256', {}), **result.get('audit_input_sha256', {})}
    inputs.pop(f'config/inventory-review-{result.get("target")}.json', None)
    bound = bound and ledger.get('review_input_sha256') == inputs
    decisions = ledger.get('decisions')
    if not isinstance(decisions, list):
        raise ValueError('missing inventory review decisions')
    states, entries, blockers = {}, {}, []
    for entry in decisions:
        ident = entry.get('id')
        if (not isinstance(ident, str) or not ident or ident in entries
                or entry.get('state') not in ('open', 'closed')
                or any(not isinstance(entry.get(k), str) or not entry[k].strip()
                       for k in ('location', 'unknown', 'completion_effect', 'close_when', 'decision'))
                or entry.get('kind') not in ('mechanism', 'storage')):
            raise ValueError('invalid or duplicate inventory decision')
        if (entry['kind'] == 'mechanism') != (ident in MECHANISMS):
            raise ValueError('unknown mechanism or reserved storage id')
        if entry['kind'] == 'storage':
            bank, cpu, size = entry.get('bank'), entry.get('cpu'), entry.get('size')
            if (type(bank) is not int or bank not in (0, 1) or type(cpu) is not int
                    or type(size) is not int or not 0x8000 <= cpu < cpu + size <= 0x10000):
                raise ValueError('invalid storage decision extent')
        evidence = entry.get('evidence')
        if not isinstance(evidence, list) or not evidence:
            raise ValueError('inventory decision lacks evidence')
        valid = [evidence_valid(root, row) for row in evidence]
        state = entry['state'] if bound and all(valid) else 'stale'
        states[ident], entries[ident] = state, entry
        if state != 'closed':
            blockers.append({**{k: entry[k] for k in ('id', 'location', 'unknown', 'completion_effect', 'close_when')},
                             'state': state})
    for ident in sorted(MECHANISMS - entries.keys()):
        states[ident] = 'missing'
        blockers.append({'id': ident, 'state': 'missing', 'close_when': 'Record an evidence-backed mechanism review.'})
    rows, counts = [], Counter()
    for original in result['regions']:
        row = dict(original)
        start, end = row['physical_prg_offset'], row['physical_prg_offset'] + row['size']
        required = list(REPRESENTATION_GATES.get(row['representation'], ()))
        required += [entry['id'] for entry in decisions if entry['kind'] == 'storage'
                     and start < entry['bank'] * 0x8000 + entry['cpu'] - 0x8000 + entry['size']
                     and entry['bank'] * 0x8000 + entry['cpu'] - 0x8000 < end]
        # Explicit storage decisions can be reviewed while opaque storage still
        # prevents reconstruction acceptance. They cannot change ownership.
        status = ('unreviewed' if not required else 'reviewed' if all(states.get(k) == 'closed' for k in required)
                  else 'blocked')
        row.update(review_decisions=required, review_status=status)
        row.pop('exclusive_use_reviewed', None)
        if row['representation'] == 'unresolved_local' and not any(states.get(k) != 'closed' for k in required):
            blockers.append({'id': f'opaque-{row["bank"]}-{row["cpu_start"]}', 'state': 'open',
                             'location': f'bank {row["bank"]} {row["cpu_start"]} +{row["size"]}',
                             'unknown': 'Opaque local storage has no accepted representation.',
                             'completion_effect': 'Closing a review entry cannot replace reconstruction.',
                             'close_when': 'Provide a supported source or understood local asset representation.'})
        counts[status] += row['size']
        rows.append(row)
    opaque = result['representation_bytes'].get('unresolved_local', 0)
    complete = not blockers and not opaque and counts['reviewed'] == result['prg_bytes']
    return {**result, 'regions': rows, 'complete_executable_inventory': complete,
            'inventory_review': {'status': 'accepted' if complete else 'blocked',
                                'input_binding_valid': bound, 'decision_states': states,
                                'review_bytes': dict(counts), 'opaque_storage_bytes': opaque,
                                'blockers': blockers}}
