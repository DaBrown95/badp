"""Trace candidate v1.5 inventory PPU streams without exporting their text.

The PPU handler consumes ordinary bytes, three-byte $FE/$FF address commands,
and a zero terminator. This logical decode does not establish scheduling, queue
capacity, reachability or the safety of every 32-byte lookahead across a bank.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys

from .project import input_path
from .script_entries import BANK_SIZE, ROOT, _locate, _location, load_audited_banks

_WORD = re.compile(r'\$[0-9a-fA-F]{4}\Z')
_QUEUE = re.compile(r'^\s*BogusQueueStateAB\s+([^;]+)')
_CASE = re.compile(r'^\s*BogusRemapCase\s+([^,;]+),\s*([^;]+)')
FLOW_INPUTS = ('tools/ppu_streams.py', 'tools/script_entries.py')


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_seeds(source: str, bank1: bytes) -> list[int]:
    """Collect direct queues, four entries of each table, and eight remap cases."""
    if len(bank1) != BANK_SIZE:
        raise ValueError('expected one full alternate bank')
    seeds = set()
    for line in source.splitlines():
        match = _QUEUE.match(line)
        if not match:
            continue
        operand = match.group(1).strip()
        if not _WORD.fullmatch(operand):
            raise ValueError('unsupported direct PPU stream pointer expression')
        pointer = int(operand[1:], 16)
        if pointer:  # Zero selects a runtime slot value.
            seeds.add(pointer)
    for table in (0x505f, 0x509d):
        for offset in range(table, table + 8, 2):
            seeds.add(int.from_bytes(bank1[offset:offset + 2], 'little'))
    _, start_marker, after_start = source.partition('\nScriptD00D:\n')
    block, end_marker, _ = after_start.partition('\n    BogusRemapEnd')
    if not start_marker or not end_marker:
        raise ValueError('cannot establish the inventory PPU remap boundaries')
    cases = {}
    for line in block.splitlines():
        match = _CASE.match(line)
        if not match:
            continue
        key, value = (part.strip() for part in match.groups())
        if not _WORD.fullmatch(key) or not _WORD.fullmatch(value):
            raise ValueError('unsupported PPU remap expression')
        key_int = int(key[1:], 16)
        if key_int in cases:
            raise ValueError('duplicate PPU remap key')
        cases[key_int] = int(value[1:], 16)
    if set(cases) != set(range(0x8000, 0x8008)):
        raise ValueError('cannot establish the eight inventory PPU remap cases')
    seeds.update(cases.values())
    if 0 in seeds:
        raise ValueError('candidate PPU pointer table contains a dynamic zero pointer')
    return sorted(seeds)


def decode_stream(bank0: bytes, bank1: bytes, pointer: int, *, limit: int = 4096) -> dict:
    """Decode one logical stream; address operand zeros do not terminate it."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE or type(limit) is not int or limit <= 0:
        raise ValueError('expected two full banks and a positive stream limit')
    bank, start = _locate(pointer)
    data = (bank0, bank1)[bank]
    cursor = start
    characters = absolute = relative = 0
    segments: list[dict] = []

    def segment(kind: str, size: int) -> None:
        offset = cursor - start
        # Coalesce payload extents without exporting their tile values.
        if kind == 'payload' and segments and segments[-1]['kind'] == kind:
            segments[-1]['size'] += size
        else:
            segments.append({'kind': kind, 'offset': offset, 'size': size})

    while cursor < BANK_SIZE and cursor - start < limit:
        opcode = data[cursor]
        if opcode == 0:
            segment('terminator', 1)
            cursor += 1
            return {'encoded_pointer': f'0x{pointer:04x}', 'location': _location(bank, start),
                    'size': cursor - start, 'characters': characters, 'absolute_addresses': absolute,
                    'relative_addresses': relative, 'segments': segments,
                    'lookahead_crossing_possible': cursor - 1 + 32 > BANK_SIZE}
        if opcode >= 0xfe:
            if cursor + 3 > BANK_SIZE or cursor + 3 - start > limit:
                raise ValueError('truncated PPU address command')
            if opcode == 0xfe:
                relative += 1
                segment('relative_address', 3)
            else:
                absolute += 1
                segment('absolute_address', 3)
            cursor += 3
        else:
            characters += 1
            segment('payload', 1)
            cursor += 1
    raise ValueError('unterminated or bank-crossing PPU stream')


def inventory(bank0: bytes, bank1: bytes, seeds: list[int], *, limit: int = 4096) -> dict:
    streams = [decode_stream(bank0, bank1, pointer, limit=limit) for pointer in sorted(set(seeds))]
    coverage: dict[int, set[int]] = {}
    control: set[int] = set()
    payload: set[int] = set()
    for stream in streams:
        start = stream['location']['physical_prg_offset']
        for pos in range(start, start + stream['size']):
            coverage.setdefault(pos, set()).add(start)
        for segment in stream['segments']:
            begin = start + segment['offset']
            positions = range(begin, begin + segment['size'])
            (payload if segment['kind'] == 'payload' else control).update(positions)
    return {'streams': streams, 'physical_bytes': len(coverage),
            'control_bytes': len(control), 'payload_bytes': len(payload),
            'control_payload_overlap_bytes': len(control & payload),
            'overlapping_stream_bytes': sum(len(starts) > 1 for starts in coverage.values()),
            'lookahead_crossing_streams': sum(s['lookahead_crossing_possible'] for s in streams)}


def main() -> int:
    try:
        from .progress import verify_primary

        inputs = {name: _digest(ROOT / name) for name in FLOW_INPUTS}
        target, bank0, bank1, _ = load_audited_banks()
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_sha256 = _digest(proof_path)
        verified = verify_primary(ROOT, target)
        source_path = ROOT / 'src/us-v1.5/rom.s'
        if _digest(source_path) != verified['source_sha256']:
            raise ValueError('source changed after build verification')
        result = inventory(bank0, bank1, literal_seeds(source_path.read_text(), bank1))
        reference = target['reference']['file']['sha256']
        rom = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        if (_digest(source_path) != verified['source_sha256'] or _digest(rom) != reference
                or _digest(proof_path) != proof_sha256
                or {name: _digest(ROOT / name) for name in FLOW_INPUTS} != inputs):
            raise ValueError('PPU stream inputs changed during traversal')
        result.update(target='us-v1.5', reference_sha256=reference, source_sha256=verified['source_sha256'],
                      build_proof_sha256=proof_sha256, flow_input_sha256=inputs,
                      interpretation='candidate logical streams; runtime reachability and lookahead safety remain unverified')
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/ppu-streams.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'target': result['target'], 'streams': len(result['streams']),
                          'physical_bytes': result['physical_bytes'],
                          'control_bytes': result['control_bytes'],
                          'payload_bytes': result['payload_bytes'],
                          'control_payload_overlap_bytes': result['control_payload_overlap_bytes'],
                          'overlapping_stream_bytes': result['overlapping_stream_bytes'],
                          'lookahead_crossing_streams': result['lookahead_crossing_streams'],
                          'output': 'analysis/us-v1.5/ppu-streams.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'PPU stream inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
