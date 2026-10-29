"""Own physical source partition and bounded unversioned inventory review.

Assembler leaf spans bind emitted instructions, structured directives and
explicit editable asset inputs. Overlapping logical uses are reviewed apart
from this disjoint representation; no byte percentage establishes completion.
"""
from __future__ import annotations

from collections import defaultdict
import re

from .native_control_flow import _fields, NATIVE_INSTRUCTION
from .nes6502 import OPCODES, source_mode_matches


def source_partition(debug: str, source: str, prg: bytes,
                     payloads: dict[str, bytes]) -> list[dict]:
    """Require a consistent source/asset representation for every PRG byte."""
    if len(prg) != 65536:
        raise ValueError('expected two complete own PRG banks')
    files, segments, spans, locations = {}, {}, {}, defaultdict(list)
    for line in debug.splitlines():
        tag, sep, rest = line.partition('\t')
        if not sep or tag not in ('file', 'seg', 'span', 'line'):
            continue
        row = _fields(rest)
        if tag == 'file':files[int(row['id'])] = row['name']
        elif tag == 'seg':segments[int(row['id'])] = row
        elif tag == 'span':spans[int(row['id'])] = (int(row['seg']), int(row['start'], 0), int(row['size'], 0))
        elif 'span' in row:
            for ident in row['span'].split('+'):
                locations[int(ident)].append((int(row['file']), int(row['line'])))
    source_ids = [ident for ident, name in files.items() if name == 'source/rom.s']
    if len(source_ids) != 1:
        raise ValueError('missing or ambiguous own debug source')
    banks = {}
    for bank in (0, 1):
        matches = [(ident, row) for ident, row in segments.items() if row.get('name') == f'PRG{bank}']
        if len(matches) != 1:raise ValueError('missing own debug bank')
        ident, row = matches[0]
        if (int(row['start'], 0) != 32768 or int(row['size'], 0) != 32768
                or int(row['ooffs'], 0) != 16 + bank * 32768):
            raise ValueError('changed own debug bank geometry')
        banks[ident] = bank
    text = source.splitlines()
    owners: list[tuple[str, str | None] | None] = [None] * 65536
    for ident, (segment, offset, size) in spans.items():
        if segment not in banks or size == 0:continue
        if size < 0 or not 0 <= offset < offset + size <= 32768:
            raise ValueError('own source span crosses a bank')
        start = banks[segment] * 32768 + offset
        candidates = set()
        for file_id, number in locations[ident]:
            if file_id != source_ids[0]:continue
            if not 1 <= number <= len(text):raise ValueError('own debug line leaves source')
            statement = text[number - 1].partition(';')[0].strip()
            native = NATIVE_INSTRUCTION.match(statement)
            if native:
                decoded = OPCODES.get(prg[start])
                if (decoded and decoded[0] == native[1].lower() and size == decoded[2]
                        and source_mode_matches(decoded[0], statement[native.end():], decoded[1])):
                    candidates.add(('code', None))
            elif re.match(r'^\.(byte|word)\s', statement):candidates.add(('data', None))
            elif re.match(r'^\.res\s', statement):candidates.add(('fill', None))
            elif statement.startswith('.incbin '):
                match = re.fullmatch(r'\.incbin "([a-z0-9.-]+)"', statement)
                if not match or match[1] not in payloads:
                    raise ValueError('unaccounted binary source input')
                name = match[1]
                if payloads[name] != prg[start:start + size]:
                    raise ValueError('asset leaf span differs from its complete encoded input')
                candidates.add(('asset', name))
        if not candidates:continue  # Parent macro spans have no emitting statement.
        if len(candidates) != 1:raise ValueError('conflicting own source span representations')
        owner = candidates.pop()
        for position in range(start, start + size):
            if owners[position] not in (None, owner):
                raise ValueError('overlapping own source representations')
            owners[position] = owner
    if None in owners:
        raise ValueError(f'unrepresented own PRG byte at physical offset {owners.index(None):04x}')
    result = []
    for bank in (0, 1):
        cursor, end = bank * 32768, (bank + 1) * 32768
        while cursor < end:
            start, owner = cursor, owners[cursor]
            while cursor < end and owners[cursor] == owner:cursor += 1
            row = {'bank': bank, 'cpu': f'0x{start % 32768 + 32768:04x}',
                   'size': cursor - start, 'kind': owner[0]}
            if owner[1] is not None:row['asset'] = owner[1]
            result.append(row)
    return result


def emitting_units(debug: str, source: str, forms: dict[str, int]) -> list[dict]:
    """Locate declared fixed-size forms, including macro-generated declarations."""
    files, segments, spans, lines = {}, {}, {}, []
    for line in debug.splitlines():
        tag, sep, rest = line.partition('\t')
        if not sep or tag not in ('file', 'seg', 'span', 'line'):continue
        row = _fields(rest)
        if tag == 'file':files[int(row['id'])] = row['name']
        elif tag == 'seg':segments[int(row['id'])] = row
        elif tag == 'span':spans[int(row['id'])] = row
        elif 'span' in row:lines.append(row)
    text, found = source.splitlines(), {}
    for line in lines:
        if files[int(line['file'])] != 'source/rom.s':continue
        number = int(line['line'])
        if not 1 <= number <= len(text):raise ValueError('unit debug line leaves source')
        words = text[number - 1].partition(';')[0].split()
        if not words or words[0] not in forms:continue
        name = words[0]
        for ident in line['span'].split('+'):
            row = spans[int(ident)];segment = segments[int(row['seg'])]
            if segment['name'] not in ('PRG0', 'PRG1') or int(row['size'], 0) != forms[name]:continue
            bank, offset = int(segment['name'][-1]), int(row['start'], 0)
            key = bank, offset, name
            found[key] = {'bank': bank, 'cpu': f'0x{offset + 32768:04x}', 'size': forms[name],
                          'macro': name, 'source_line': number, 'physical_prg_offset': bank * 32768 + offset}
    return [found[key] for key in sorted(found)]


def command_schemas(source: str) -> dict:
    """Read direct typed command forms, excluding tables and asset directives."""
    from .source_variants import operands
    constants = {name: int(value, 16) for name, value in
                 re.findall(r'(?m)^(\w+) = \$([0-9A-Fa-f]+)\s*(?:;.*)?$', source)}
    result = {}
    for match in re.finditer(r'(?m)^\.macro (\w+)([^\n]*)\n(.*?)^\.endmacro', source, re.S):
        if not match[1].startswith(('Bogus', 'Unversioned')):continue
        parts = []
        for line in match[3].splitlines():
            statement = line.partition(';')[0].strip()
            if not statement:continue
            row = re.fullmatch(r'\.(byte|word) (.+)', statement)
            if not row:parts = [];break
            parts += [(1 if row[1] == 'byte' else 2, value) for value in operands(row[2])]
        if not parts or parts[0][0] != 1:continue
        try:
            value = parts[0][1]
            opcode = int(value[1:], 16) if value.startswith('$') else constants[value]
        except (ValueError, KeyError):continue
        if not 0 <= opcode < 191:continue
        result[match[1]] = {'opcode': opcode, 'size': sum(width for width, _ in parts), 'parts': parts[1:]}
    return result


def analyze(root, target, proof, reference) -> dict:
    """Review actual source entries and finite transfer mechanisms for this ROM.

    No reachability search over arbitrary RAM is performed. A conditional
    interpretation within represented storage remains distinct from a missing
    source implementation.
    """
    from collections import Counter
    import json
    from .build_rom import digest
    from .native_control_flow import inventory as native_inventory
    from .prg_inventory import summarize
    from .record_views import inventory as record_views
    from .script_entries import inventory as descriptors
    from .script_flow import CONDITIONAL_POINTER, scan_lookup_table
    from .source_audit import partition
    from .unversioned_assets import load as load_assets, encode as encode_assets
    from . import audio_flow
    folder = root / 'build/us-unversioned'
    source = (folder / 'source/rom.s').read_text()
    debug = (folder / 'bible-adventures.dbg').read_text()
    config_bytes = (root / 'config/source-us-unversioned.json').read_bytes()
    config = json.loads(config_bytes)
    prg = reference[16:65552];banks = prg[:32768], prg[32768:]
    lengths = banks[0][0x7da0:0x7e5f]
    if len(lengths) != 191 or lengths != banks[1][0x7da0:0x7e5f]:
        raise ValueError('own command-length copies differ')
    assets, _ = load_assets(root)
    payloads = encode_assets(root, assets, reference)
    from .sprite_metadata import decode_frame_header
    retained_frame = banks[1][0x7c39:0x7c3e]
    retained_header = decode_frame_header(retained_frame, header_format='separate-bytes')
    if (retained_frame != banks[0][0x3a8d:0x3a92]
            or retained_header['tile_read_offsets'] != [3, 4]
            or int.from_bytes(banks[1][0x7c37:0x7c39], 'little') != 0x7c39):
        raise ValueError('retained own resource/frame format requires a new review')
    physical = source_partition(debug, source, prg, payloads)
    native = native_inventory(debug, source, prg, config['regions'])
    starts = {(row['bank'], int(row['cpu'], 0)) for row in native['instructions']}
    transitions = {(row['bank'], int(row['cpu'], 0), int(row['target_cpu'], 0))
                   for row in native['same_bank_non_code_targets']}
    if (transitions != {(1, 0xffde, 0x80b8), (1, 0xfff6, 0x8000)}
            or any(not row['other_bank_instruction_start'] for row in native['same_bank_non_code_targets'])
            or native['same_bank_non_instruction_start_targets']):
        raise ValueError('new own native transfer or mapping gap needs review')
    vectors = []
    for bank in (0, 1):
        for offset in (0x7ffa, 0x7ffc, 0x7ffe):
            value = int.from_bytes(banks[bank][offset:offset + 2], 'little')
            if (bank, value) not in starts:raise ValueError('own vector lacks a native entry')
            vectors.append({'bank': bank, 'vector_cpu': f'0x{offset + 32768:04x}', 'target_cpu': f'0x{value:04x}'})
    dispatch = []
    for index in range(256):
        address = ((banks[0][0x50b1 + index] | banks[0][0x5170 + index] << 8) + 1) & 65535
        row = {'index': index, 'target_cpu': f'0x{address:04x}', 'nominal': index < 191,
               'bank0_instruction_start': (0, address) in starts}
        if row['nominal'] and not row['bank0_instruction_start']:
            raise ValueError('nominal own script handler lacks a reconstructed native entry')
        dispatch.append(row)
    schemas = command_schemas(source)
    commands = emitting_units(debug, source, {name: row['size'] for name, row in schemas.items()})
    for row in commands:
        offset = row['physical_prg_offset'];schema = schemas[row['macro']];opcode = prg[offset]
        if opcode != schema['opcode'] or len(lengths) <= opcode or lengths[opcode] != row['size']:
            raise ValueError('declared own command differs from its native length/format')
        row['opcode'] = opcode
    # This supported transfer enters the low byte of an existing record-load
    # operand and consumes the following B8 opcode as its third byte.
    overlaps = ((0, 0xa20a, bytes((0x2d, 0, 0xb8)),
                 'A203 branch -> A20A: 2D/00/B8 overlaps the A209 pointer and A20C command.'),
                (1, 0xf209, bytes((0x00, 0x2c)), 'Conditional normal 9F return; a record load overlaps F20A.'),
                (1, 0xf20b, bytes((0x85, 0x2d)), 'Conditional continuation overlaps the F20A/F20C commands.'),
                (1, 0xf20d, bytes((0x00, 0x00)), 'Conditional record load overlaps F20C, then rejoins F20F.'))
    for bank, cpu, raw, basis in overlaps:
        offset = bank * 32768 + cpu - 32768
        if prg[offset:offset + len(raw)] != raw or lengths[raw[0]] != len(raw):
            raise ValueError('supported own command overlap changed')
        commands.append({'bank': bank, 'cpu': f'0x{cpu:04x}', 'size': len(raw),
                         'macro': 'conditional-overlap', 'source_line': None,
                         'physical_prg_offset': offset, 'opcode': raw[0], 'basis': basis})
    command_starts = {(row['bank'], int(row['cpu'], 0)): row for row in commands}
    if len(command_starts) != len(commands):raise ValueError('duplicate own command declarations')
    edges, table_cases, contexts = [], [], []
    conditional = CONDITIONAL_POINTER - {0x57, 0xc2}
    for row in commands:
        offset, opcode = row['physical_prg_offset'], row['opcode']
        raw = prg[offset:offset + row['size']]
        targets = []
        if opcode in conditional | {4, 0x39, 0x3c, 0x58}:
            field = 4 if opcode == 0x39 else 3 if opcode == 0x3c else 2 if opcode == 0x58 else 1
            targets.append(int.from_bytes(raw[field:field + 2], 'little'))
        if opcode == 0x44:
            cpu = int(row['cpu'], 0)
            count = {0xb2d7: 6, 0xe71b: 8}.get(cpu) if row['bank'] == 1 else None
            if count is None:raise ValueError('new own indexed transfer needs a bounded source review')
            before = banks[1][cpu - 32768 - (8 if count == 6 else 3):cpu - 32768]
            expected = bytes.fromhex('80 14 00 85 04') if count == 6 else bytes.fromhex('40 07 00')
            if not before.endswith(expected):raise ValueError('own indexed predecessor changed')
            for index in range(count):
                start = offset + 1 + 2 * index
                value = int.from_bytes(prg[start:start + 2], 'little')
                targets.append(value)
                table_cases.append({'command_cpu': row['cpu'], 'index': index, 'target': f'0x{value:04x}',
                                    'scope': 'Same slot through the recorded clamp/divide or mask; independent arbitrary indices remain conditional.'})
        if opcode in (0x95, 0xb1):
            encoded = int(row['cpu'], 0) - (32768 if row['bank'] == 1 else 0)
            table = scan_lookup_table(banks, encoded + row['size'])
            if table['status'] != 'terminated':raise ValueError('own inline cases lack a stored terminator')
            if opcode == 0x95:targets += [case['target'] for case in table['records'] if not case.get('terminator')]
            contexts.append({'bank': row['bank'], 'cpu': row['cpu'], 'mechanism': 'lookup' if opcode == 0x95 else 'remap',
                             'stored_cases': len(table['records']) - 1})
        for target_word in targets:
            bank, cpu = (1, target_word + 32768) if target_word < 32768 else (0, target_word)
            if (bank, cpu) not in command_starts:
                raise ValueError(f'declared own successor lacks a source command view: {row["cpu"]} -> {bank}:{cpu:04x}')
            edges.append({'bank': row['bank'], 'cpu': row['cpu'], 'target_bank': bank, 'target_cpu': f'0x{cpu:04x}'})
    declared_records = record_views(source, debug, config)
    initial = descriptors(*banks, 0x1f03, 123, lengths)
    normal_records = {(row['bank'], int(row['cpu'], 0)) for row in declared_records if row['kind'] == 'normal'}
    normal_records.update((0, value) for value in (0xa1e5, 0xa1ee, 0xa294))
    crossing_records = []
    for row in initial['records']:
        loc = row['location']
        if row['status'] == 'crosses_bank_boundary':
            if (loc['bank'], int(loc['cpu_address'], 0)) != (0, 0xffff):
                raise ValueError('new own record boundary requires review')
            crossing_records.append(row)
            continue
        if (loc['bank'], int(loc['cpu_address'], 0)) not in normal_records:
            raise ValueError('own descriptor points outside the maintained normal record inventory')
    record_scripts = []
    for bank, cpu in sorted(normal_records):
        offset = bank * 32768 + cpu - 32768
        word = int.from_bytes(prg[offset + 2:offset + 4], 'little')
        if word >> 8 == 255:continue
        target_bank, target_cpu = (1, word + 32768) if word < 32768 else (0, word)
        if (target_bank, target_cpu) not in command_starts:
            raise ValueError('own normal record script lacks a maintained command entry')
        record_scripts.append({'bank': bank, 'cpu': f'0x{cpu:04x}', 'script_bank': target_bank,
                               'script_cpu': f'0x{target_cpu:04x}'})
    audio_forms = {'AudioNote': 1, 'AudioInstrument': 1, 'AudioSelectChannel': 1, 'AudioStopVoice': 1,
                   'AudioDelay': 2, 'AudioWriteFive': 5, 'AudioLoop': 4, 'AudioRestorePointer': 1,
                   'AudioRestartChannel': 1, 'AudioSetChannelMask': 1, 'AudioClearChannelMask': 1}
    audio_units = emitting_units(debug, source, audio_forms)
    seeds = set()
    for row in commands:
        if row['opcode'] not in (0x31, 0x49, 0x50):continue
        start = row['physical_prg_offset'] + 1
        for i in range(4 if row['opcode'] == 0x31 else 1):
            value = int.from_bytes(prg[start + i * 2:start + i * 2 + 2], 'little')
            if value >> 8 not in (0, 255):seeds.add(value)
    audio_tables = emitting_units(debug, source, {'AudioPointerEntry': 2, 'AudioVoicePointerRecord': 8})
    for row in audio_tables:
        for offset in range(row['physical_prg_offset'], row['physical_prg_offset'] + row['size'], 2):
            value = int.from_bytes(prg[offset:offset + 2], 'little')
            if value >> 8 not in (0, 255):seeds.add(value)
    symbols = []
    for line in debug.splitlines():
        if line.startswith('sym\t'):
            fields = _fields(line.partition('\t')[2])
            if fields.get('name') == 'LegacyOpcode18Audio':symbols.append(int(fields['val'], 0))
    if len(symbols) != 1:raise ValueError('missing own native audio entry')
    seeds.update(symbols)
    audio = audio_flow.walk(*banks, sorted(seeds), limit=65536)
    if audio['unprocessed']:raise ValueError('unprocessed own literal audio contexts')
    spans = {f'source_{kind}': [(row['bank'] * 32768 + int(row['cpu'], 0) - 32768, row['size'])
                               for row in physical if row['kind'] == kind] for kind in ('code', 'data', 'fill')}
    spans['candidate_script_bytes'] = [(row['physical_prg_offset'], row['size']) for row in commands]
    spans['candidate_audio_commands'] = [(row['location']['physical_prg_offset'], row['length']) for row in audio['nodes'] if 'length' in row]
    asset_spans = {row['asset']: [(other['bank'] * 32768 + int(other['cpu'], 0) - 32768, other['size'])
                                 for other in physical if other.get('asset') == row['asset']]
                   for row in physical if row['kind'] == 'asset'}
    result = partition(summarize(spans)['evidence_spans'], asset_spans)
    inputs = ('tools/unversioned_inventory.py', 'tools/inventory_review.py', 'tools/native_control_flow.py',
              'tools/nes6502.py', 'tools/record_views.py', 'tools/script_entries.py', 'tools/script_flow.py',
              'tools/audio_flow.py', 'tools/audio_commands.py', 'tools/prg_inventory.py', 'tools/source_audit.py',
              'tools/unversioned_assets.py', 'config/source-us-unversioned.json')
    result.update(schema_version=1, target=target['id'], reference_sha256=digest(reference),
                  source_sha256=proof['source_sha256'], source_map_sha256=digest(config_bytes),
                  build_proof_sha256=digest((folder / 'proof.json').read_bytes()),
                  inventory_input_sha256={**proof['input_sha256'], **{name: digest((root / name).read_bytes()) for name in inputs}},
                  audit_input_sha256={},
                  native_review={'instructions': native['instruction_count'], 'bytes': native['instruction_code_bytes'],
                                 'vectors': vectors,
                                 'same_bank_non_instruction_targets': native['same_bank_non_instruction_start_targets'],
                                 'bank_transition_targets': native['same_bank_non_code_targets']},
                  script_review={'declared_commands': len(commands), 'literal_successors': len(edges),
                                 'all_literal_targets_represented': True, 'nominal_handlers': 191,
                                 'indexed_cases': table_cases, 'inline_tables': contexts,
                                 'native_call_commands': sum(row['opcode'] == 0x9b for row in commands),
                                 'scope': 'Actual own source entries and literal successors, including A20A overlap. Conditional loaders, retries, saved pointers and out-of-range byte-index aliases retain their reconstructed mechanisms; no exhaustive RAM reachability requirement.'},
                  record_review={'descriptors': 123, 'distinct_descriptor_records': len(initial['records']),
                                 'declared_bank1_views': len(declared_records), 'script_relationships': len(record_scripts),
                                 'crossing_record_contexts': crossing_records,
                                 'literal_non_rom_resource': '0x7c37; sprite consumers retain this CPU address without OR80 conversion.'},
                  audio_review={'literal_seeds': len(seeds), 'declared_commands': len(audio_units),
                                'contexts': len(audio['nodes']), 'crossing_fetches': audio['crossing_fetches'],
                                'scope': 'Own literal starts and identical shared command protocol; no later-revision playback trace is imported.'},
                  retained_resource_review={'word_cpu': '0xfc37', 'encoded_frame_word': '0x7c39',
                                            'physical_frame_cpu': '0xfc39', 'frame_size': 5,
                                            'header': retained_header, 'identical_known_frame': 'bank0 0xba8d',
                                            'zero_attribute_overlap': '0xfc3d',
                                            'scope': 'Supported retained data format. No conversion from literal CPU7C37 to ROM FC37 or ordinary rendering is asserted.'},
                  interpretation='A complete physical source partition and finite mechanism review. Names, original purpose, ordinary reachability and arbitrary injected state remain separate.')
    output = root / 'analysis/us-unversioned'
    output.mkdir(parents=True, exist_ok=True)
    for name, payload in {'native-review': native, 'dispatch-review': dispatch, 'script-declarations': commands,
                          'script-successors': edges, 'record-relationships': record_scripts,
                          'audio-review': audio}.items():
        (output / (name + '.json')).write_text(json.dumps(payload, indent=2) + '\n')
    return result


def review(root, target, proof, reference) -> dict:
    import json
    from .build_rom import digest
    from .inventory_review import apply_review
    result = analyze(root, target, proof, reference)
    name = 'config/inventory-review-us-unversioned.json'
    ledger = json.loads((root / name).read_text())
    result['audit_input_sha256'][name] = digest((root / name).read_bytes())
    result = apply_review(result, ledger, root)
    (root / 'analysis/us-unversioned/source-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    return result
