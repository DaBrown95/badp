"""Inventory standard record declarations and explicit fragmented loader views.

The authenticated assembler map locates declarations; complete source ownership
is checked independently for each physical byte. Views do not prove execution,
exclusive use, a descriptor association, or all possible dynamic loader inputs.
"""
from __future__ import annotations

from collections import defaultdict

from .native_control_flow import _fields

FORMS = {'SlotRuntimeRecord': ('normal', 9), 'SlotScriptOnlyRecord': ('normal', 9),
         'SlotCompactRecord': ('compact', 3)}
SIZES = {'normal': 9, 'compact': 3}


def inventory(source: str, debug: str, source_map: dict) -> list[dict]:
    lines = source.splitlines()
    starts = [i for i, line in enumerate(lines, 1) if line.strip() == '.scope Bank1']
    if len(starts) != 1:
        raise ValueError('missing or ambiguous bank-1 source scope')
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines) + 1)
                if lines[i - 1].strip() == '.endscope'), None)
    if end is None:
        raise ValueError('unterminated bank-1 source scope')
    declarations = {}
    for number in range(start + 1, end):
        words = lines[number - 1].split(';', 1)[0].split()
        if words and words[0] in FORMS:
            declarations[number] = words[0]
    files, segments, spans, associations = {}, {}, {}, []
    for row in debug.splitlines():
        tag, sep, rest = row.partition('\t')
        if not sep or tag not in ('file', 'seg', 'span', 'line'):
            continue
        fields = _fields(rest)
        if tag == 'line':
            if 'span' in fields:
                associations.append(fields)
            continue
        collection = {'file': files, 'seg': segments, 'span': spans}[tag]
        ident = int(fields['id'])
        if ident in collection:
            raise ValueError('duplicate debug record-view identity')
        collection[ident] = fields
    source_ids = [key for key, item in files.items() if item['name'] == 'source/rom.s']
    bank_ids = [key for key, item in segments.items() if item['name'] == 'PRG1']
    if len(source_ids) != 1 or len(bank_ids) != 1:
        raise ValueError('missing or ambiguous record-view debug source/segment')
    segment = segments[bank_ids[0]]
    if (int(segment['start'], 0) != 0x8000 or int(segment['size'], 0) != 0x8000
            or int(segment['ooffs'], 0) != 32784):
        raise ValueError('invalid record-view debug geometry')
    found = defaultdict(set)
    for row in associations:
        number = int(row['line'])
        if int(row['file']) != source_ids[0] or number not in declarations:
            continue
        expected = FORMS[declarations[number]][1]
        for ident in row['span'].split('+'):
            if int(ident) not in spans:
                raise ValueError('record-view debug span is missing')
            span = spans[int(ident)]
            if int(span['seg']) == bank_ids[0] and int(span['size'], 0) == expected:
                found[number].add(int(span['start'], 0))
    if not declarations or set(found) != set(declarations) or any(len(v) != 1 for v in found.values()):
        raise ValueError('record declarations have missing or ambiguous debug extents')
    views = []
    for number, positions in found.items():
        form = declarations[number]
        kind, size = FORMS[form]
        offset = next(iter(positions))
        views.append({'id': f'declared-{offset:04x}', 'bank': 1, 'cpu': f'0x{0x8000 + offset:04x}',
                      'kind': kind, 'size': size, 'basis': form, 'source_line': number})
    explicit = source_map.get('loader_views', [])
    if not isinstance(explicit, list):
        raise ValueError('fragmented loader views must be a list')
    for view in explicit:
        if (not isinstance(view, dict) or set(view) != {'id', 'bank', 'cpu', 'kind', 'size', 'basis'}
                or view['kind'] not in SIZES or view['size'] != SIZES[view['kind']]
                or not isinstance(view['basis'], str) or not view['basis']):
            raise ValueError('invalid fragmented loader view')
        views.append(view.copy())
    owned = set()
    for region in source_map['regions']:
        if region['bank'] == 1 and region['kind'] == 'data':
            first = int(region['cpu'], 0)
            owned.update(range(first, first + region['size']))
    seen, ids = set(), set()
    for view in views:
        cpu = int(view['cpu'], 0)
        key = view['kind'], cpu
        if (type(view['bank']) is not int or view['bank'] != 1 or not 0x8000 <= cpu <= 0xfff6
                or key in seen or not isinstance(view['id'], str) or not view['id'] or view['id'] in ids
                or not set(range(cpu, cpu + view['size'])) <= owned):
            raise ValueError('duplicate, out-of-bank or incompletely source-owned record view')
        seen.add(key)
        ids.add(view['id'])
    return sorted(views, key=lambda row: (row['kind'], int(row['cpu'], 0)))
