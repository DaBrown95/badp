"""Compose explicit release differences into the common readable assembly.

Only source expressions and typed fields are transformed. No ROM payload is
read by composition, and no emitted binary is patched. Logical address names
retain their primary identities while target addresses come from the layout.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re


def operands(text: str) -> list[str]:
    """Split assembler fields without splitting nested expressions."""
    result, start, stack = [], 0, []
    for index, char in enumerate(text):
        if char in '({':
            stack.append(char)
        elif char in ')}':
            if not stack or stack.pop() != ( '(' if char == ')' else '{'):
                raise ValueError('unbalanced source operand')
        elif char == ',' and not stack:
            result.append(text[start:index].strip());start = index + 1
    if stack:
        raise ValueError('unbalanced source operand')
    result.append(text[start:].strip())
    if any(not item for item in result):
        raise ValueError('empty source operand')
    return result


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f'variant source precondition is missing or ambiguous: {old[:70]}')
    return source.replace(old, new, 1)


def marked_statement(source: str, marker: str, transform) -> str:
    """Transform one typed field while preserving its input mutation surface."""
    lines = source.splitlines()
    matches = [i for i, line in enumerate(lines) if line.partition(';')[2].strip() == marker]
    if len(matches) != 1:
        raise ValueError('missing or ambiguous variant field: ' + marker)
    index = matches[0]
    text = lines[index].partition(';')[0].strip()
    lines[index] = '    ' + transform(text) + ' ; ' + marker
    return '\n'.join(lines) + '\n'


@dataclass(frozen=True)
class Layout:
    ranges: tuple[tuple[int, int, int, int], ...]
    blocks: tuple[tuple[int, int, int, int], ...] = ()

    def __post_init__(self):
        previous = {}
        for bank, start, end, delta in self.ranges:
            if (type(bank) is not int or bank not in (0, 1)
                    or any(type(n) is not int for n in (start, end, delta))
                    or not 0x8000 <= start < end <= 0x10000
                    or not 0x8000 <= start + delta < end + delta <= 0x10000
                    or start < previous.get(bank, 0x8000)):
                raise ValueError('invalid or overlapping target layout interval')
            previous[bank] = end
        previous = {}
        for bank, start, end, target in self.blocks:
            if (type(bank) is not int or bank not in (0, 1)
                    or any(type(n) is not int for n in (start, end, target))
                    or not 0x8000 <= start < end <= 0x10000
                    or not 0x8000 <= target < target + end - start <= 0x10000
                    or start < previous.get(bank, 0x8000)):
                raise ValueError('invalid or overlapping relocated source block')
            previous[bank] = end

    def address(self, bank: int, cpu: int) -> int:
        if type(bank) is not int or bank not in (0, 1) or type(cpu) is not int or not 0x8000 <= cpu <= 0x10000:
            raise ValueError('invalid logical PRG location')
        return cpu + next((delta for b, start, end, delta in self.ranges
                           if bank == b and start <= cpu < end), 0)

    def offset(self, bank: int, offset: int) -> int:
        return self.address(bank, offset + 0x8000) - 0x8000

    def span(self, bank: int, start: int, end: int) -> tuple[int, int]:
        """Map a physical extent, keeping the left end of reordered blocks.

        A frame extent ending where the primary palette begins does not end
        at the palette's new start after those blocks exchange positions.
        """
        if (type(bank) is not int or bank not in (0, 1) or type(start) is not int
                or type(end) is not int or not 0x8000 <= start < end <= 0x10000):
            raise ValueError('invalid source span')
        for b, low, high, target in self.blocks:
            if b == bank and low <= start < end <= high:
                return target + start - low, target + end - low
            if b == bank and start < high and low < end:
                raise ValueError('source span crosses a reordered block boundary')
        return self.address(bank, start), self.address(bank, end)

    def expression(self, *, bank: int | None, encoded: bool = False) -> str:
        terms = ['(n)']
        for b, start, end, delta in self.ranges:
            if bank is not None and b != bank:
                continue
            low, high = (start - 0x8000, end - 0x8000) if encoded or bank is None else (start, end)
            condition = f'((n) >= ${low:04X}) * ((n) < ${high:04X})'
            if bank is None:
                condition = f'(CurrentBank = {b}) * ' + condition
            terms.append(f'({delta} * {condition})')
        return '(' + ' + '.join(terms) + ')'


def load_profile(root: Path, target: str) -> dict:
    if target not in ('us-v1.4', 'us-v1.3', 'us-v1.2'):
        raise ValueError('no maintained source variant for this target')
    profile = json.loads((root / f'config/variants/{target}.json').read_text())
    if (profile.get('schema_version') != 1 or profile.get('target') != target
            or profile.get('canonical_target') != 'us-v1.5'):
        raise ValueError('invalid source variant identity')
    for value in source_paths(profile):
        path = PurePosixPath(value)
        if not value or path.is_absolute() or '..' in path.parts or str(path) != value:
            raise ValueError('unsafe variant source path')
        if not (root / value).resolve().is_relative_to(root.resolve()) or (root / value).is_symlink():
            raise ValueError('variant source escapes workspace')
    profile['geometry'] = Layout(tuple((row['bank'], int(row['start'], 0), int(row['end'], 0), row['delta'])
                                       for row in profile['layout']),
                                 tuple((row['bank'], int(row['start'], 0), int(row['end'], 0), int(row['target_start'], 0))
                                       for row in profile.get('relocated_blocks', [])))
    if type(profile.get('menu_brand_count_delta')) is not int:
        raise ValueError('invalid menu length difference')
    if target in ('us-v1.3', 'us-v1.2'):
        profile['selector_text'] = (root / profile['bank_selection_source']).read_text()
        profile['definition_text'] = '\n'.join((root / name).read_text() for name in profile['native_definitions'])
    if target == 'us-v1.2':
        profile['earlier_definition_text'] = '\n'.join((root / name).read_text() for name in profile['earlier_definitions'])
    return profile


def source_paths(profile: dict) -> list[str]:
    paths = [profile.get(key, '') for key in ('canonical_source', 'canonical_map', 'reset_source')]
    if profile['target'] in ('us-v1.3', 'us-v1.2'):
        definitions = profile.get('native_definitions')
        if not isinstance(definitions, list) or not definitions:
            raise ValueError('missing target native definitions')
        paths += [profile.get('bank_selection_source', ''), *definitions]
    if profile['target'] == 'us-v1.2':
        earlier = profile.get('earlier_definitions')
        if not isinstance(earlier, list) or not earlier:
            raise ValueError('missing earlier native definitions')
        paths += earlier
    if any(not isinstance(path, str) for path in paths):
        raise ValueError('invalid variant source path')
    return paths


def variant_regions(config: dict, profile: dict) -> list[dict]:
    if 'code_windows' not in profile:
        return target_regions(config, profile['geometry'])
    layout = profile['geometry']
    overrides = profile.get('region_overrides', {})
    known = {row['id'] for row in config['regions']}
    if set(overrides) - known:
        raise ValueError('unknown versioned source-region override')
    result = []
    for row in config['regions']:
        if row['kind'] == 'code':
            continue
        start = int(row['cpu'], 0)
        low, high = layout.span(row['bank'], start, start + row['size'])
        result.append({**row, 'cpu': f'0x{low:04x}', 'size': high - low,
                       **overrides.get(row['id'], {})})
    return result + profile['code_windows'] + profile.get('extra_regions', [])


def typed_literal(value: str, function: str, layout: Layout) -> str:
    value = value.strip()
    if re.fullmatch(r'\$[0-9A-Fa-f]{4}', value):
        number = int(value[1:], 16)
        bank, cpu = (0, number) if function == 'Bank0Resource' else (1, 0x8000 + number)
        if 0x8000 <= cpu <= 0x10000 and layout.address(bank, cpu) != cpu:
            return f'({function} {{{value}}})'
    return value


def typed_lines(source: str, layout: Layout) -> str:
    """Relocate only known record fields and the mixed encoded map table.

    Absolute packed-text pointers are bank-1 CPU addresses, not encoded bank-0
    resources. Other word constants, PPU addresses and RAM operands stay intact.
    """
    lines, related = [], False
    record_types = ('SlotRuntimeRecord', 'SlotCompactRecord', 'SlotDescriptor',
                    'SlotRecordScriptOverlay', 'SlotRecordVoiceOverlay', 'SlotRecordBranchPrefix')
    pattern = re.compile(r'^(\s*)(' + '|'.join(record_types) + r')\s+(.+?)\s*$')
    for line in source.splitlines():
        text, separator, comment = line.partition(';')
        match = pattern.match(text)
        if match:
            fields = operands(match[3])
            fields[0] = typed_literal(fields[0], 'Bank1Encoded' if match[2] == 'SlotDescriptor'
                                      else 'Bank0Resource', layout)
            if match[2] in ('SlotRuntimeRecord', 'SlotRecordScriptOverlay', 'SlotRecordVoiceOverlay', 'SlotRecordBranchPrefix'):
                fields[1] = typed_literal(fields[1], 'Bank1Encoded', layout)
            line = match[1] + match[2] + ' ' + ', '.join(fields) + (' ;' + comment if separator else '')
        match = re.match(r'^(\w*(?:Resource|Pointer)) = (\$[0-9A-Fa-f]{4})', line)
        if match:
            line = line.replace(match[2], typed_literal(match[2], 'Bank0Resource', layout), 1)
        if line.startswith('SlotRelatedAddressTable:'):
            related = True
        elif related and line.startswith('.assert'):
            related = False
        if related and text.strip().startswith('.word '):
            match = re.search(r'\$([0-9A-Fa-f]{4})', line)
            if not match:
                raise ValueError('unexpected mixed map pointer table expression')
            kind = 'Bank0Resource' if int(match[1], 16) >= 0x8000 else 'Bank1Encoded'
            line = line[:match.start()] + typed_literal(match[0], kind, layout) + line[match.end():]
        lines.append(line)
    return '\n'.join(lines) + '\n'


def compose(source: str, reset: str, profile: dict) -> str:
    if profile['target'] not in ('us-v1.4', 'us-v1.3', 'us-v1.2'):
        raise ValueError('unsupported composition rules')
    if profile['target'] in ('us-v1.3', 'us-v1.2'):
        from .legacy_source import prepare
        source = prepare(source, profile)
    if profile['target'] == 'us-v1.2':
        from .earlier_source import prepare as earlier_prepare
        source = earlier_prepare(source, profile['selector_text'], profile['earlier_definition_text'])
    layout = profile['geometry']
    if source.count('CheckResetState:') != 1 or source.count('InitializeGame:') != 1:
        raise ValueError('ambiguous reset variant boundaries')
    start, end = source.index('CheckResetState:'), source.index('InitializeGame:')
    source = source[:start] + reset + '\n' + source[end:]
    for bank in (0, 1):
        source = replace_once(source, f'.scope Bank{bank}\nBankStart:', f'.scope Bank{bank}\nCurrentBank = {bank}\nBankStart:')
    definitions = ('\n.define TargetOffset(n) ' + layout.expression(bank=None)
                   + '\n.define Bank0Resource(n) ' + layout.expression(bank=0)
                   + '\n.define Bank1Encoded(n) ' + layout.expression(bank=1, encoded=True))
    source = replace_once(source, '.include "nes.inc"', '.include "nes.inc"' + definitions)
    source = re.sub(r'(\.assert \(\* - BankStart\) = )\$([0-9A-Fa-f]+)', r'\1TargetOffset $\2', source)
    source = re.sub(r'BankStart \+ \$([0-9A-Fa-f]{4})', r'BankStart + (TargetOffset {$\1})', source)
    for ident in ('MenuBrandTail', 'MenuTileRow0', 'MenuTileRow1', 'MenuTileRow2', 'MenuTileRow3'):
        pattern = r'(' + ident + r' = MenuLocalData \+ )\$([0-9A-F]+)'
        source, count = re.subn(pattern, lambda m: m[1] + f'${int(m[2], 16) + profile["menu_brand_count_delta"]:02X}', source)
        if count != 1:
            raise ValueError('missing or ambiguous post-brand menu alias')
    # The command length is a source parameter, separate from local tile values.
    brand = re.compile(r'^(\s*BogusQueueState6E \(MenuBrandLine - BankStart\),.*?,\s*)(\$[0-9A-Fa-f]{2})(\s*)$', re.M)
    source, count = brand.subn(lambda m: m[1] + f'({m[2]} + ({profile["menu_brand_count_delta"]}))' + m[3], source)
    if count != 1:
        raise ValueError('missing or ambiguous brand command count')
    source = replace_once(source, 'ldy $A1B3,x', 'ldy SlotRelatedAddressTable+1,x')
    source = replace_once(source, 'lda $A1B2,x', 'lda SlotRelatedAddressTable,x')
    source = replace_once(source, 'lda #$06\n    clc\n    adc $FE\n    sta $FE\n    lda #$9F',
                          'lda #<SlotInitialDescriptors\n    clc\n    adc $FE\n    sta $FE\n    lda #>SlotInitialDescriptors')
    source = typed_lines(source, layout)
    # These primary-only aliases are incidental interpretations of resource
    # bytes. In v1.4 the relocated record remains represented, but those opcode
    # assertions would falsely carry the primary command interpretation over.
    primary_only = ('E002 record/voice opcode disagreement', 'E099 record/script opcode disagreement',
                    'EB0D record/script opcode disagreement', 'EBAD record/script opcode disagreement',
                    'record/voice opcode disagreement', 'record/script branch prefix disagreement')
    source = '\n'.join('; v1.4 primary-only incidental view: ' + line.strip()
                       if any(phrase in line for phrase in primary_only) else line
                       for line in source.splitlines()) + '\n'
    def mode_resource(text):
        name, args = text.split(maxsplit=1)
        if name != 'BogusModeResourceOverlay':
            raise ValueError('unexpected mode/resource source form')
        fields = operands(args)
        if len(fields) != 2:
            raise ValueError('invalid mode/resource fields')
        return '.word ' + typed_literal(fields[1], 'Bank0Resource', layout)
    source = marked_statement(source, 'CONTROL_OVERLAY_B077', mode_resource)
    source = replace_once(source, 'CandidateScriptD555Value = $27', 'CandidateScriptD555Value = <(Bank0Resource {$B927})')
    def resource_word(text):
        name, value = text.split(maxsplit=1)
        if name != '.word' or not re.fullmatch(r'\$[0-9A-Fa-f]{4}', value):
            raise ValueError('unexpected partial-resource source form')
        return '.word ' + typed_literal(value, 'Bank0Resource', layout)
    for marker in ('CONTROL_PARTIAL_RESOURCE_AD18', 'CONTROL_MODE_RECORD_E055_RESOURCE', 'CONTROL_COMPACT_EB10_RESOURCE'):
        source = marked_statement(source, marker, resource_word)
    # A compact resource's low/high bytes are owned by separate source spans.
    # Read both fields before relocating; do not freeze either to reference data.
    low_match = re.search(r'\.byte \$([0-9A-Fa-f]{2}) ; CONTROL_RECORD_STORAGE_E040', source)
    high_match = re.search(r'\.byte \$([0-9A-Fa-f]{2}), (\$[0-9A-Fa-f]{2}) ; CONTROL_COMPACT_E040_HIGH_MODE', source)
    if not low_match or not high_match:
        raise ValueError('missing split compact-resource fields')
    pointer = int(high_match[1] + low_match[1], 16)
    expression = typed_literal(f'${pointer:04X}', 'Bank0Resource', layout)
    source = marked_statement(source, 'CONTROL_RECORD_STORAGE_E040', lambda text: '.byte <' + expression)
    source = marked_statement(source, 'CONTROL_COMPACT_E040_HIGH_MODE', lambda text: '.byte >' + expression + ', ' + high_match[2])
    # Two consecutive compact records are also a six-byte normal-record prefix.
    # Keep flags and both resource words separate in the relocated representation.
    prefix = re.search(r'\.word \$([0-9A-Fa-f]{4}), \$([0-9A-Fa-f]{4}) ; CONTROL_RECORD_DA40_PREFIX\n    \.byte \$([0-9A-Fa-f]{2}), (\$[0-9A-Fa-f]{2})', source)
    if not prefix:
        raise ValueError('missing paired compact-record prefix')
    second = int(prefix[3] + prefix[2][:2], 16)
    replacement = ('.word ' + typed_literal('$' + prefix[1], 'Bank0Resource', layout)
                   + ' ; CONTROL_RECORD_DA40_PREFIX\n    .byte $' + prefix[2][2:]
                   + '\n    .word ' + typed_literal(f'${second:04X}', 'Bank0Resource', layout)
                   + '\n    .byte ' + prefix[4])
    source = source[:prefix.start()] + replacement + source[prefix.end():]
    if profile['target'] in ('us-v1.3', 'us-v1.2'):
        from .legacy_source import typed_fields, compact_constant_maps
        source = compact_constant_maps(typed_fields(source, layout), layout)
    return source


def target_regions(config: dict, layout: Layout) -> list[dict]:
    result = []
    for entry in config['regions']:
        bank, start = entry['bank'], int(entry['cpu'], 0)
        mapped, end = layout.span(bank, start, start + entry['size'])
        if mapped >= end:
            raise ValueError('source region collapses in target layout')
        result.append({**entry, 'cpu': f'0x{mapped:04x}', 'size': end - mapped})
    for bank in (0, 1):
        end = 0x8000
        for row in sorted((r for r in result if r['bank'] == bank), key=lambda r: int(r['cpu'], 0)):
            start = int(row['cpu'], 0)
            if start < end:
                raise ValueError('target source regions overlap')
            end = start + row['size']
    return result
