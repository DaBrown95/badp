"""Check the instruction matrix against isolated, synthetic cc65 assembly."""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile

from .nes6502 import OPCODES
from .setup import sha256, verified_tools

OPERANDS = {'imp': '', 'acc': 'a', 'imm': '#$12', 'zp': 'z:$12', 'zpx': 'z:$12,x',
            'zpy': 'z:$12,y', 'indx': '($12,x)', 'indy': '($12),y', 'rel': '*+2',
            'abs': 'a:$1234', 'absx': 'a:$1234,x', 'absy': 'a:$1234,y', 'ind': '($1234)'}


def verify(root: Path) -> dict:
    tools = verified_tools(root)
    lines, expected = ['.setcpu "6502"', '.segment "CODE"'], bytearray()
    for opcode, (mnemonic, mode, size) in sorted(OPCODES.items()):
        lines.append(f'    {mnemonic} {OPERANDS[mode]}'.rstrip())
        expected.append(opcode)
        if size == 2:
            expected.append(0 if mode == 'rel' else 0x12)
        elif size == 3:
            expected.extend((0x34, 0x12))
    source = '\n'.join(lines) + '\n'
    linker = ('MEMORY { TEST: start=$8000, size=$1000, type=ro, file=%O; }\n'
              'SEGMENTS { CODE: load=TEST, type=ro; }\n')
    with tempfile.TemporaryDirectory(prefix='.native-opcode-check-', dir=root / 'build') as directory:
        work = Path(directory)
        (work / 'matrix.s').write_text(source)
        (work / 'matrix.cfg').write_text(linker)
        subprocess.run([str(tools['ca65']), '-o', 'matrix.o', 'matrix.s'], cwd=work,
                       capture_output=True, text=True, check=True)
        subprocess.run([str(tools['ld65']), '-C', 'matrix.cfg', '-o', 'matrix.bin', 'matrix.o'],
                       cwd=work, capture_output=True, text=True, check=True)
        actual = (work / 'matrix.bin').read_bytes()
        if actual != expected:
            raise ValueError('official instruction matrix disagrees with pinned synthetic assembly')
    return {'official_forms': len(OPCODES), 'encoded_bytes': len(expected),
            'synthetic_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'synthetic_output_sha256': hashlib.sha256(expected).hexdigest(),
            'assembler_sha256': sha256(tools['ca65']), 'linker_sha256': sha256(tools['ld65'])}
