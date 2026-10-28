"""Official NMOS 6502 instruction forms used for NES source-boundary checks.

The two regular opcode groups are generated from their bit fields; the third
and the single-byte exceptions are listed explicitly. Decimal flag instructions
exist on the NES CPU even though its ADC/SBC arithmetic stays binary. This
module does not decode unofficial opcodes or infer code in unowned ROM data.
"""
from __future__ import annotations

SIZES = {'imp': 1, 'acc': 1, 'imm': 2, 'zp': 2, 'zpx': 2, 'zpy': 2, 'indx': 2,
         'indy': 2, 'rel': 2, 'abs': 3, 'absx': 3, 'absy': 3, 'ind': 3}


def _table() -> dict[int, tuple[str, str, int]]:
    result = {}

    def add(opcode: int, mnemonic: str, mode: str) -> None:
        if opcode in result:
            raise ValueError('duplicate official instruction opcode')
        result[opcode] = (mnemonic, mode, SIZES[mode])

    for group, mnemonic in enumerate(('ora', 'and', 'eor', 'adc', 'sta', 'lda', 'cmp', 'sbc')):
        for mode_index, mode in enumerate(('indx', 'zp', 'imm', 'abs', 'indy', 'zpx', 'absy', 'absx')):
            if mnemonic == 'sta' and mode == 'imm':
                continue
            add(group << 5 | mode_index << 2 | 1, mnemonic, mode)
    for group, mnemonic in enumerate(('asl', 'rol', 'lsr', 'ror', 'stx', 'ldx', 'dec', 'inc')):
        modes = {1: 'zp', 3: 'abs', 5: 'zpx', 7: 'absx'}
        if mnemonic in ('asl', 'rol', 'lsr', 'ror'):
            modes[2] = 'acc'
        elif mnemonic == 'stx':
            modes = {1: 'zp', 3: 'abs', 5: 'zpy'}
        elif mnemonic == 'ldx':
            modes = {0: 'imm', 1: 'zp', 3: 'abs', 5: 'zpy', 7: 'absy'}
        for mode_index, mode in modes.items():
            add(group << 5 | mode_index << 2 | 2, mnemonic, mode)
    exceptions = '''
00 brk imp
08 php imp
10 bpl rel
18 clc imp
20 jsr abs
24 bit zp
28 plp imp
2c bit abs
30 bmi rel
38 sec imp
40 rti imp
48 pha imp
4c jmp abs
50 bvc rel
58 cli imp
60 rts imp
68 pla imp
6c jmp ind
70 bvs rel
78 sei imp
84 sty zp
88 dey imp
8a txa imp
8c sty abs
90 bcc rel
94 sty zpx
98 tya imp
9a txs imp
a0 ldy imm
a4 ldy zp
a8 tay imp
aa tax imp
ac ldy abs
b0 bcs rel
b4 ldy zpx
b8 clv imp
ba tsx imp
bc ldy absx
c0 cpy imm
c4 cpy zp
c8 iny imp
ca dex imp
cc cpy abs
d0 bne rel
d8 cld imp
e0 cpx imm
e4 cpx zp
e8 inx imp
ea nop imp
ec cpx abs
f0 beq rel
f8 sed imp
'''
    for line in exceptions.splitlines():
        if line.strip():
            opcode, mnemonic, mode = line.split()
            add(int(opcode, 16), mnemonic, mode)
    if len(result) != 151:
        raise ValueError('incomplete official instruction matrix')
    return result


OPCODES = _table()
MNEMONICS = frozenset(row[0] for row in OPCODES.values())


def source_mode_matches(mnemonic: str, operand: str, mode: str) -> bool:
    """Check syntactic addressing forms, including ca65's size overrides.

    Symbol/expression values remain the pinned assembler's responsibility.
    A bare memory expression may use zero page or absolute addressing; explicit
    a:/z: overrides must keep their encoded width.
    """
    operand = ''.join(operand.lower().split())
    if mode == 'rel':
        return bool(operand) and not operand.startswith(('#', '(')) and ',' not in operand
    if not operand:
        return mode == ('acc' if mnemonic in ('asl', 'lsr', 'rol', 'ror') else 'imp')
    if operand == 'a':
        return mode == 'acc'
    if operand.startswith('#'):
        return mode == 'imm'
    if operand.startswith('('):
        if operand.endswith(',x)'):
            return mode == 'indx'
        if operand.endswith('),y'):
            return mode == 'indy'
        return mode == 'ind' and operand.endswith(')')
    forced = None
    if operand.startswith(('a:', 'z:')):
        forced, operand = operand[0], operand[2:]
    suffix = 'x' if operand.endswith(',x') else 'y' if operand.endswith(',y') else ''
    allowed = {('zp' + suffix), ('abs' + suffix)}
    if forced == 'a':
        allowed = {'abs' + suffix}
    elif forced == 'z':
        allowed = {'zp' + suffix}
    return mode in allowed
