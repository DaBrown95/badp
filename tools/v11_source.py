"""Explicit v1.1 native and command differences from the shared v1.2 forms.

Composition reads no ROM and never patches an emitted binary. Physical layout,
versioned data and full-build/inventory evidence are separate requirements.
"""
import re
from collections import Counter
from .source_variants import replace_once, operands


def palette_pointers(source: str, variant: dict) -> str:
    """Keep changed state selections separate from palette relocation."""
    for table in ('BackgroundPalettePointers', 'SpritePalettePointers'):
        changes = {row['index']: row for row in variant['palette_pointer_overrides'] if row['table'] == table}
        if len(changes) != sum(row['table'] == table for row in variant['palette_pointer_overrides']):
            raise ValueError('duplicate palette selection index')
        start = source.index('\n' + table + ':')
        end = source.index('\nSpritePalettePointers:' if table == 'BackgroundPalettePointers' else '\n.assert', start + 1)
        lines, index = [], 0
        for line in source[start:end].splitlines():
            text, separator, comment = line.partition(';')
            if text.strip().startswith('.word '):
                fields = operands(text.strip().removeprefix('.word '))
                for n, value in enumerate(fields):
                    if index in changes:
                        row = changes[index]
                        if value != row['expected'] or not re.fullmatch(r'\w+', row['target']):
                            raise ValueError('changed palette state selection')
                        fields[n] = row['target']
                    index += 1
                line = '    .word ' + ', '.join(fields) + (' ;' + comment if separator else '')
            lines.append(line)
        if index != 22 or any(type(i) is not int or not 0 <= i < index for i in changes):
            raise ValueError('changed palette selector extent')
        source = source[:start] + '\n'.join(lines) + source[end:]
    return source


def extra_palettes(source: str, definitions: str) -> str:
    return replace_once(source, '\nObservedSpriteDirectHeaderBA23:',
                        '\n' + definitions + '\nObservedSpriteDirectHeaderBA23:')


def extra_scripts(source: str, definitions: str) -> str:
    source = replace_once(source,
        'LegacyEncodedPointerAndByte (InteractionScriptAF05 - BankStart), $E0 ; CONTROL_SCRIPT_PREFIX_AF02',
        'LegacyEncodedPointerAndByte (V11AF02Fallthrough - BankStart), $E0 ; CONTROL_SCRIPT_PREFIX_AF02')
    return replace_once(source, '\nInteractionScriptAF05:',
                        '\n' + definitions + '\nInteractionScriptAF05:')


def position_records(source: str, variant: dict) -> str:
    """F0 records pass their first payload byte to the descriptor initializer."""
    remap = {int(key, 0): value for key, value in variant['script_index_remap'].items()}
    lines = []
    for line in source.splitlines():
        text, separator, comment = line.partition(';')
        if text.strip().startswith('PositionRecord '):
            fields = operands(text.strip().removeprefix('PositionRecord '))
            if len(fields) != 8:
                raise ValueError('changed position-record fields')
            if fields[2] == '$F0' and re.fullmatch(r'\$[0-9A-Fa-f]{2}', fields[3]):
                value = int(fields[3][1:], 16)
                if value in remap:
                    fields[3] = f'${remap[value]:02X}'
                    line = '    PositionRecord ' + ', '.join(fields) + (' ;' + comment if separator else '')
        lines.append(line)
    return '\n'.join(lines) + '\n'


def script_fragments(source: str, variant: dict) -> str:
    """Apply bounded command differences at their shared source labels."""
    for change in variant.get('script_fragments', []):
        start = source.index('\n' + change['start'] + ':')
        end = source.index('\n' + change['end'] + ':', start)
        body = source[start:end] + '\n'
        for statement, count in Counter(change.get('remove', [])).items():
            if body.count(statement + '\n') != count:
                raise ValueError('changed fragment statement count: ' + statement)
            body = body.replace(statement + '\n', '')
        for replacement in change.get('replace', []):
            old, new = replacement['old'] + '\n', replacement['new'] + '\n'
            count = replacement.get('count', 1)
            if type(count) is not int or count < 1 or body.count(old) != count:
                raise ValueError('changed fragment replacement count at ' + change['start'] + ': ' + replacement['old'])
            body = body.replace(old, new)
        if 'insert' in change:
            body = replace_once(body, change['after'] + '\n',
                                change['after'] + '\n' + change['insert'] + '\n')
        source = source[:start] + body.removesuffix('\n') + source[end:]
    return source


def script_descriptor_indices(source: str, variant: dict) -> str:
    """Keep descriptor-index operands distinct from generic script values."""
    roles = {'BogusCreateSlotFromValue': 0, 'BogusInitializeOtherSlotRelative': 0,
             'BogusInitializeOtherSlotAbsolute': 0, 'BogusCountSlotsByRecord': 0,
             'BogusCreateLinkedSlot': 0}
    if variant.get('target') != 'us-v1.1' or variant.get('script_index_roles') != roles:
        raise ValueError('invalid v1.1 script descriptor roles')
    remap = {int(key, 0): value for key, value in variant['script_index_remap'].items()}
    if any(not 0 <= key < 114 or type(value) is not int or not 114 <= value < 127
           for key, value in remap.items()):
        raise ValueError('invalid v1.1 script descriptor index')
    conditional = variant.get('conditional_script_index_roles', {})
    expected = {
        'BogusBranchIfMatchingSlotReady': {'selector': 1, 'index': 2, 'excluded_selectors': [0]},
        'BogusMarkMatchingSlots': {'selector': 1, 'index': 2, 'excluded_selectors': [0, 255]},
        'BogusSelectRelativeSlotAndYield': {'selector': 2, 'index': 3, 'excluded_selectors': [0, 35]},
    }
    if conditional and conditional != expected:
        raise ValueError('invalid conditional descriptor-index roles')
    lines = []
    for line in source.splitlines():
        text, separator, comment = line.partition(';')
        match = re.fullmatch(r'\s*(\w+)\s+(.+?)\s*', text)
        if match and match[1] in roles.keys() | conditional.keys():
            fields = operands(match[2])
            if match[1] in conditional:
                role = conditional[match[1]]
                selector = role['selector']
                if selector >= len(fields):
                    raise ValueError('missing descriptor-search selector')
                if (not re.fullmatch(r'\$[0-9A-Fa-f]{2}', fields[selector])
                        or int(fields[selector][1:], 16) in role['excluded_selectors']):
                    lines.append(line)
                    continue
                index = role['index']
            else:
                index = roles[match[1]]
            if not fields or index >= len(fields):
                raise ValueError('missing script descriptor operand')
            if re.fullmatch(r'\$[0-9A-Fa-f]{2}', fields[index]):
                value = int(fields[index][1:], 16)
                if value in remap:
                    fields[index] = f'${remap[value]:02X}'
                    line = '    ' + match[1] + ' ' + ', '.join(fields) + (' ;' + comment if separator else '')
        lines.append(line)
    return '\n'.join(lines) + '\n'


def descriptors(source: str, variant: dict) -> str:
    """Apply explicit descriptor fields while retaining shared pointer roles."""
    if (variant.get('schema_version') != 1 or variant.get('target') != 'us-v1.1'
            or variant.get('shared_entries') != 114 or variant.get('entries') != 127):
        raise ValueError('invalid v1.1 descriptor variant identity')
    start = source.index('\nSlotInitialDescriptors:')
    end = source.index('\n.assert', start)
    overrides = {row['index']: row for row in variant['field_overrides']}
    unavailable = set(variant['unavailable_indices'])
    if (len(overrides) != len(variant['field_overrides'])
            or len(unavailable) != len(variant['unavailable_indices'])
            or any(type(i) is not int or not 0 <= i < 114 for i in overrides.keys() | unavailable)):
        raise ValueError('invalid v1.1 descriptor change indices')
    lines, count = [], 0
    for line in source[start:end].splitlines():
        text, separator, comment = line.partition(';')
        if text.strip().startswith('SlotDescriptor '):
            fields = operands(text.strip().removeprefix('SlotDescriptor '))
            if len(fields) != 5:
                raise ValueError('changed shared descriptor field count')
            if count in overrides:
                row = overrides[count]
                if [int(value.removeprefix('$'), 16) for value in fields[1:]] != row['expected']:
                    raise ValueError('changed shared descriptor fields at index ' + str(count))
                if len(row['fields']) != 4 or any(type(n) is not int or not 0 <= n <= 255 for n in row['fields']):
                    raise ValueError('invalid target descriptor byte fields')
                fields[1:] = [f'${n:02X}' for n in row['fields']]
            if count in unavailable:
                if fields[0] == '$FFFF':
                    raise ValueError('changed shared descriptor availability')
                fields[0] = '$FFFF'
            line = '    SlotDescriptor ' + ', '.join(fields) + (' ;' + comment if separator else '')
            count += 1
        lines.append(line)
    if count != 114 or len(variant['extra_entries']) != 13:
        raise ValueError('changed v1.1 descriptor extent')
    lines += ['', '; Additional v1.1 descriptor entries, using the same six-byte format.',
              'V11AdditionalSlotDescriptors:']
    for index, row in enumerate(variant['extra_entries'], 114):
        pointer, values = int(row['record'], 0), row['fields']
        if not 0 <= pointer <= 65535 or len(values) != 4 or any(type(n) is not int or not 0 <= n <= 255 for n in values):
            raise ValueError('invalid additional v1.1 descriptor')
        marker = ' ; CONTROL_V11_EXTRA_DESCRIPTORS' if index == 114 else f' ; index ${index:02X}'
        lines.append(f'    SlotDescriptor ${pointer:04X}, ' + ', '.join(f'${n:02X}' for n in values) + marker)
    return source[:start] + '\n'.join(lines) + source[end:]

def logical_entries(source: str) -> str:
    source = replace_once(source, 'ScriptF313 = BankStart + $7313',
                          'ScriptF313 = CandidateF30E + 2')
    old = '    BogusJumpBank1 ScriptBB8A'
    if source.count(old) != 2:
        raise ValueError('changed BB8A resume consumers')
    source = source.replace(old, '    BogusJumpBank1 V11BB8AResume')
    return source


def conditional_views(source: str, variant: dict) -> str:
    for marker in ('CONTROL_CONTACT_SCRIPT_DC26', 'CONTROL_CONTACT_SCRIPT_E08A'):
        old = '    BogusSelectRelativeSlotAndYield $40, $FF, $00, $00, $00 ; ' + marker
        source = replace_once(source, old,
            '    .byte >(RuntimeScriptE764 - BankStart), $40, $FF, $00, $00, $00 ; ' + marker)
    lines = []
    for line in source.splitlines():
        if line.lstrip().startswith('.assert'):
            for message in variant['conditional_view_decisions']:
                if '"' + message + '"' in line:
                    line = '; v1.1 changed incidental view: ' + line.strip()
                    break
        text, separator, comment = line.partition(';')
        if text.strip().startswith('SlotRecordVoiceOverlay '):
            fields = operands(text.strip().removeprefix('SlotRecordVoiceOverlay '))
            # The potential voice-word view follows the relocated record's
            # actual fields, even when its first byte is no longer opcode31.
            fields[7] = f'((>{fields[0]}) + ((<{fields[1]}) * $100))'
            line = '    SlotRecordVoiceOverlay ' + ', '.join(fields) + (' ;' + comment if separator else '')
        lines.append(line)
    return '\n'.join(lines) + '\n'


def prepare(source: str) -> str:
 source=replace_once(source,'''InitializeGame:
    lda PPUSTATUS
    lda #$3F
    sta PPUADDR
    lda #$00
    sta PPUADDR
    ldy #$1F
    lda #$0E
ClearPalette:
    sta PPUDATA
    dey
    bpl ClearPalette
''','InitializeGame:\n')
 source=replace_once(source,'    lda SpriteRecordReserveCount,x                  ; CONTROL_ALLOCATE_SPRITE_FIND_SPACE\n    sta $04DC\n','')
 source=replace_once(source,'    ldx $04DC                    ; CONTROL_ALLOCATE_SPRITE_SEARCH\n    bne AllocateSpriteSearchCount\n','')
 a=source.index('    lda $04DC\n    beq AllocateSpriteSize');b=source.index('AllocateSpriteSize:',a);source=source[:a]+source[b:]
 source=replace_once(source,'    lda SpriteRecordReserveCount,x\n    bne ReleaseSpriteCountReady\n','')
 a=source.index('\n; Convert an index into an eleven-byte $0400 record');b=source.index('\n; Look up a valid record',a);source=source[:a]+source[b:]
 source=replace_once(source,'    lda #$00\n    sta $04DC\n    lda $10\n    jsr StoreSlotRecordField0A\n','')
 a=source.index('\nScriptOpC4:');b=source.index('\n.assert',a);source=source[:a]+source[b:]
 source=replace_once(source,'    ScriptOp 2, Bank0::ScriptOpC4, part ; opcode $C4\n','')
 source=replace_once(source,'InitializeSlotCheckLoad:\n    ldx $10\n','InitializeSlotCheckLoad:\n')
 # Only the general operand resolver exists in v1.1. Its callers load the
 # selected record byte, and resolving stores are inline in their callers.
 a=source.index('\nScriptOperand61OrSlot:');b=source.index('\nScriptYieldIfNonnegative:',a)
 source=source[:a]+"\nScriptOperandOrSlot:\n    cmp #$00\n    bne ScriptOperandReady\n    lda $70,x\nScriptOperandReady:\n    rts\n"+source[b:]
 for field in ('1','2'):
  source=re.sub(r'(?m)^(\s*)jsr ScriptResolveOperand6'+field+r'(?=\s|;|$)',lambda m:m[1]+'lda RecordBuffer'+field+'\n    jsr ScriptOperandOrSlot\n    sta RecordBuffer'+field,source)
  source=re.sub(r'(?m)^(\s*)jsr ScriptOperand6'+field+r'OrSlot(?=\s|;|$)',lambda m:m[1]+'lda RecordBuffer'+field+'\n    jsr ScriptOperandOrSlot',source)
 # Calls enter the older high-byte-clear tail after an inline low store.
 # The array-load fallthrough still includes its original low-byte store.
 source=re.sub(r'(?m)^(\s*)(jsr|jmp) ScriptStoreSlotLowAndClearHigh(?=\s|;|$)',lambda m:m[1]+'sta $70,x\n    '+m[2]+' ScriptClearSlotHigh',source)
 # Preserve the older call/return sequence at these connected consumer tails.
 tails=('ScriptCallF0D8','ScriptClearSlotMode','ScriptOp29','ScriptOp54','ScriptOp63','ScriptOp77','ScriptFetchIndexedEight','ScriptOp8CScan')
 for label in tails:
  start=source.index('\n'+label+':');end=source.index('\n.assert',start)
  # Every selected tail is the first JMP in its labelled body.
  match=re.search(r'(?m)^    jmp ([^;\n]+)',source[start:end]);assert match,label
  old=match[0];new=old.replace('jmp ','jsr ',1)+'\n    rts';source=source[:start]+source[start:end].replace(old,new,1)+source[end:]
 # v1.1 keeps the branch-to-RTS byte after an unconditional pointer jump.
 start=source.index('\nScriptOp05:');end=source.index('\n; $FF leaves',start)
 body=replace_once(source[start:end],'bcc ScriptPointerReturn','bcc ScriptOp05Return')
 body=replace_once(body,'jmp ScriptSetPointerFromOperands','jmp ScriptSetPointerFromOperands\nScriptOp05Return:\n    rts')
 source=source[:start]+body+source[end:]
 for label,following in (('ScriptOp16','ScriptOp17'),('ScriptOp1D','ScriptOp1E'),('ScriptOp1F','ScriptOp20'),('ScriptOpA9','ScriptOpAA'),('ScriptOpAA','ScriptOpABOrBF'),('ScriptOp4D','ScriptOp4E'),('ScriptOp4E','ScriptOp4F')):
  start=source.index('\n'+label+':');end=source.index('\n'+following+':',start)
  block=source[start:end]
  block,n=re.subn(r'(?m)^    jmp ([^;\n]+)',lambda m:'    jsr '+m[1]+'\n    rts',block)
  assert n== (2 if label in ('ScriptOpAA','ScriptOp4D','ScriptOp4E') else 1),(label,n)
  source=source[:start]+block+source[end:]
 source=replace_once(source,'    cpx #$B0\n    bne ClearSlotRecordsLoop','    cpx #$A0\n    bne ClearSlotRecordsLoop')
 a=source.index('\n; Opcode $9B calls this palette fade');b=source.index('\n; Observed sprite metadata',a);source=source[:a]+source[b:]
 source,n=re.subn(r'^    BogusCallNativeEncoded Bank0::FadeOutPalettes - 1[^\n]*\n','',source,flags=re.M);assert n==24,n
 # The older vertical-store successor enters after the mode-bit test.
 source=replace_once(source,'    beq SlotDrawCheckRelease\n','    beq SlotDrawCheckLink\n')
 start=source.index('\nSlotDrawCheckRelease:');end=source.index('\nSlotDrawReleaseIfUnlinked:',start)
 source=source[:start]+replace_once(source[start:end],'    lda $06D0,x','SlotDrawCheckLink:\n    lda $06D0,x')+source[end:]
 # Physical RAM operands only. Native macro operands below have the same role.
 def ram(m):
  n=int(m[0][1:],16)
  if 0x04D8<=n<=0x04DB:return f'${n-0x04D8+0xE3:02X}'
  if n==0x05E0:return '$C0'
  if n==0xC0:return '$05D0'
  if n==0xD0:return '$07F0'
  if 0xE2<=n<=0xE5:return f'${n-0xE2+0xD0:02X}'
  if n==0xE6:return '$E2'
  return f'${n-16:04X}' if 0x04B0<=n<0x0800 else m[0]
 out=[]
 for line in source.splitlines():
  s=line.strip()
  if re.match(r'^(?:lda|ldx|ldy|sta|stx|sty|adc|sbc|and|ora|eor|asl|lsr|rol|ror|inc|dec|cmp|cpx|cpy|bit|LegacyShiftIndexedPairRight|PositionRecordSearch)\b',s):
   text,sep,comment=line.partition(';');line=re.sub(r'(?<!#)\$[0-9A-Fa-f]{2,4}\b',ram,text)+(sep+comment if sep else '')
  out.append(line)
 source='\n'.join(out)+'\n'

 # The text queue intentionally retains an absolute zero-page store.
 a=source.index('\nPackedTextQueue:');b=source.index('\n.assert',a);source=source[:a]+replace_once(source[a:b],'sta $E4','sta a:$E4')+source[b:]
 return secondary_controller_tail(source)

def secondary_controller_tail(source: str) -> str:
    """Share the surviving bank-0 controller tail at the same bank-1 PCs.

    The second bank retains114 bytes starting inside PositiveX and ending at
    the mode-gate RTS. This is an overlapping native view, not another claimed
    ordinary routine or proof of a bank-1 caller.
    """
    start = source.index('    lda $0620,x', source.index('\nControllerPositiveX:'))
    end = source.index('\n.assert', source.index('\nRequireControllerModeReturn:', start))
    body = source[start:end]
    body = '\n'.join(line.partition(';')[0].rstrip() for line in body.splitlines()
                     if not line.startswith('.assert'))
    for name in ('RequireControllerActive', 'ControllerDeltas', 'StopAudioVoice',
                 'StartAudioVoice', 'LegacyOpcode18Audio'):
        body = re.sub(r'\b' + name + r'\b', 'Bank0::' + name, body)
    body = replace_once(body, '    bne RequireControllerModeReturn',
                        'SharedModeGateReturnTail:\n    bne RequireControllerModeReturn')
    body = body.replace('    lda $0620,x',
                        '    lda $0620,x ; CONTROL_V11_SECONDARY_CONTROLLER', 1)
    return replace_once(source, 'SharedModeGateReturnTail:\n    V12ModeGateReturnTail',
                        'V11SecondaryControllerTail:\n' + body)


def include(text: str) -> str:
 text=replace_once(text,'SpriteRecordStride = $000B','SpriteRecordStride = $000A')
 text=replace_once(text,'SpriteRecordReserveCount = $040A\n','')
 lines=[]
 for line in text.splitlines():
  m=re.match(r'^(\w+) = \$([0-9A-Fa-f]{4})$',line)
  if m and 0x04B0<=int(m[2],16)<0x0800:line=m[1]+f' = ${int(m[2],16)-16:04X}'
  lines.append(line)
 return '\n'.join(lines)+'\n'
