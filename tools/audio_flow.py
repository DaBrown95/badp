"""Trace candidate v1.5 audio-command flows without exporting their payloads.

Literal starts come from reconstructed BOGUS commands, indexed voice-pointer
tables and the native $18 handler. This static traversal does not establish
reachability or stream bounds. Any decoded audio data remains in ignored local analysis.
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from .audio_commands import decode_command
from .project import input_path
from .script_entries import BANK_SIZE, ROOT, _locate, _location, load_audited_banks

_CALL = re.compile(r'^\s*(BogusSetVoicePointers|BogusStartVoice4|BogusRestartVoice4|AudioPointerEntry|AudioVoicePointerRecord)\s+([^;]+)')
_WORD = re.compile(r'\$[0-9a-fA-F]{4}\Z')
FLOW_INPUTS = ('tools/audio_flow.py', 'tools/audio_commands.py', 'tools/script_entries.py')


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_seeds(source: str) -> list[int]:
    """Read literal starts, indexed table pointers and the native opcode-$18 start."""
    starts = set()
    for line in source.splitlines():
        match = _CALL.match(line)
        if not match:
            continue
        name, operands = match.groups()
        parts = [part.strip() for part in operands.split(',')]
        expected = 4 if name in ('BogusSetVoicePointers', 'AudioVoicePointerRecord') else 1
        if len(parts) != expected or any(not _WORD.fullmatch(part) for part in parts):
            raise ValueError(f'unsupported audio pointer expression in {name}')
        for part in parts:
            pointer = int(part[1:], 16)
            # These high-byte values stop or preserve a voice rather than start it.
            if pointer >> 8 not in (0, 0xff):
                starts.add(pointer)
    _, start_marker, after_start = source.partition('\nScriptOp18:\n')
    block, end_marker, _ = after_start.partition('\n.assert')
    if not start_marker or not end_marker:
        raise ValueError('cannot establish native opcode-$18 audio boundaries')
    lo = re.search(r'(?m)^\s*ldx #\$([0-9a-fA-F]{2})\s*$', block)
    hi = re.search(r'(?m)^\s*ldy #\$([0-9a-fA-F]{2})\s*$', block)
    if not lo or not hi or not re.search(r'(?m)^\s*jsr StartAudioVoice\s*$', block):
        raise ValueError('cannot establish native opcode-$18 audio start')
    native = int(lo.group(1), 16) | (int(hi.group(1), 16) << 8)
    if native >> 8 in (0, 0xff):
        raise ValueError('native opcode-$18 audio start is not a ROM pointer')
    starts.add(native)
    return sorted(starts)


def walk(bank0: bytes, bank1: bytes, seeds: list[int], *, limit: int = 10000) -> dict:
    """Follow possible command edges in (original voice start, current pointer) contexts."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE or type(limit) is not int or limit <= 0:
        raise ValueError('expected two full banks and a positive node limit')
    pending: deque[tuple[int, int]] = deque()
    queued: set[tuple[int, int]] = set()

    def add(seed: int, pointer: int) -> None:
        _locate(seed)
        _locate(pointer)
        key = (seed, pointer)
        if key not in queued:
            queued.add(key)
            pending.append(key)

    for seed in seeds:
        add(seed, seed)
    nodes = []
    coverage: dict[int, set[int]] = {}
    while pending and len(nodes) < limit:
        seed, pointer = pending.popleft()
        bank, offset = _locate(pointer)
        location = _location(bank, offset)
        node = {'seed': f'0x{seed:04x}', 'encoded_pointer': f'0x{pointer:04x}',
                'location': location, 'successors': []}
        nodes.append(node)
        # The engine copies five bytes even if the command consumes fewer.
        if offset + 5 > BANK_SIZE:
            node['status'] = 'five_byte_fetch_crosses_bank'
            continue
        command = decode_command((bank0, bank1)[bank][offset:offset + 5])
        node['command'] = command
        node['length'] = command['size']
        start = location['physical_prg_offset']
        for byte in range(start, start + command['size']):
            coverage.setdefault(byte, set()).add(start)
        if command['kind'] == 'stop_voice':
            node['status'] = 'voice_stopped'
            continue
        if command['kind'] == 'restore_pointer':
            # The handler restores the original pointer, then its common tail
            # advances once before the next fetch.
            edges = [('restore_then_advance', (seed + 1) & 0xffff)]
        elif command['kind'] == 'loop':
            edges = [('possible_loop', command['target']),
                     ('possible_loop_exit', (pointer + command['size']) & 0xffff)]
        else:
            edges = [('next', (pointer + command['size']) & 0xffff)]
        node['status'] = 'candidate'
        for kind, successor in edges:
            node['successors'].append({'kind': kind, 'encoded_pointer': f'0x{successor:04x}'})
            add(seed, successor)
    return {'seeds': [f'0x{x:04x}' for x in sorted(set(seeds))], 'nodes': nodes,
            'unprocessed': [{'seed': f'0x{s:04x}', 'encoded_pointer': f'0x{p:04x}'}
                            for s, p in pending],
            'physical_bytes': len(coverage),
            'overlapping_decode_bytes': sum(len(starts) > 1 for starts in coverage.values()),
            'crossing_fetches': sum(x['status'] == 'five_byte_fetch_crosses_bank' for x in nodes)}


def main() -> int:
    try:
        from .progress import verify_primary

        flow_inputs = {name: _digest(ROOT / name) for name in FLOW_INPUTS}
        target, bank0, bank1, _ = load_audited_banks()
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_sha256 = _digest(proof_path)
        verified = verify_primary(ROOT, target)
        source_path = ROOT / 'src/us-v1.5/rom.s'
        if _digest(source_path) != verified['source_sha256']:
            raise ValueError('source changed after build verification')
        source = source_path.read_text()
        result = walk(bank0, bank1, literal_seeds(source))
        if result['unprocessed']:
            raise ValueError('candidate audio traversal reached its node limit')
        reference = target['reference']['file']['sha256']
        rom = input_path(ROOT, target, os.environ.get('BADP_ROM') or None)
        if (_digest(source_path) != verified['source_sha256'] or _digest(rom) != reference
                or _digest(proof_path) != proof_sha256
                or {name: _digest(ROOT / name) for name in FLOW_INPUTS} != flow_inputs):
            raise ValueError('audio-flow inputs changed during traversal')
        result.update(target='us-v1.5', reference_sha256=target['reference']['file']['sha256'],
                      source_sha256=verified['source_sha256'],
                      build_proof_sha256=proof_sha256, flow_input_sha256=flow_inputs,
                      interpretation='static candidate paths; runtime reachability and other starts remain unverified')
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/audio-flow.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'target': result['target'], 'seeds': len(result['seeds']),
                          'candidate_contexts': len(result['nodes']), 'physical_bytes': result['physical_bytes'],
                          'overlapping_decode_bytes': result['overlapping_decode_bytes'],
                          'crossing_fetches': result['crossing_fetches'],
                          'output': 'analysis/us-v1.5/audio-flow.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'audio flow failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
