"""Check sampled v1.5 script and record extents against the source map.

Inputs are local reference-only emulator traces. Results describe the sampled
paths under the recorded mapper model, not all possible game execution.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from .progress import verify_primary
from .project import input_path
from .script_entries import BANK_SIZE, ROOT, decode_slot_record, load_audited_banks
from .mesen_runtime import RUNTIME_INPUTS
from .setup_mesen import digest_file, spec
from .slot_record_flow import record_used_offsets

TRACE = 'analysis/us-v1.5/stage3-upper-carry-execution.json'
PAIR = re.compile(r'^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{2})$')
RECORD = re.compile(r'^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{2}):([0-9A-Fa-f]{2})$')
CODE = re.compile(r'^[0-9A-Fa-f]{5}$')


def _spans(offsets: set[int]) -> list[dict]:
    """Compress physical offsets without joining adjacent physical banks."""
    runs = []
    for pos in sorted(offsets):
        if runs and pos == runs[-1]['start'] + runs[-1]['size'] and pos // BANK_SIZE == runs[-1]['start'] // BANK_SIZE:
            runs[-1]['size'] += 1
        else:
            runs.append({'start': pos, 'size': 1})
    return runs


def _items(values: object, pattern: re.Pattern) -> list[tuple[tuple[int, ...], int]]:
    if not isinstance(values, dict):
        raise ValueError('trace entries must be a mapping')
    result = []
    for key, count in values.items():
        if not isinstance(key, str) or not (match := pattern.fullmatch(key)) or type(count) is not int or count <= 0:
            raise ValueError('malformed trace entry or count')
        result.append((tuple(int(value, 16) for value in match.groups()), count))
    return result


def coverage(bank0: bytes, bank1: bytes, lengths: bytes, gaps: set[int], trace: dict) -> dict:
    """Count unique sampled extents and the subset still supplied locally."""
    if len(bank0) != BANK_SIZE or len(bank1) != BANK_SIZE or not 1 <= len(lengths) <= 256:
        raise ValueError('invalid PRG banks or command length table')
    if not isinstance(gaps, set) or any(type(x) is not int or not 0 <= x < 2 * BANK_SIZE for x in gaps):
        raise ValueError('invalid physical gap set')
    if not isinstance(trace, dict):
        raise ValueError('trace must be a mapping')
    results = trace.get('results')
    if not isinstance(results, dict) or set(results) != {'code', 'scripts', 'records'}:
        raise ValueError('trace result categories are incomplete')
    scripts = _items(results['scripts'], PAIR)
    records = _items(results['records'], RECORD)
    if not scripts or not records:
        raise ValueError('trace has no script or record entries')
    code = results['code']
    if not isinstance(code, dict):
        raise ValueError('invalid native instruction-gap trace')
    for key, count in code.items():
        if (not isinstance(key, str) or not CODE.fullmatch(key) or int(key, 16) not in gaps
                or type(count) is not int or count <= 0):
            raise ValueError('invalid native instruction-gap entry')
    banks = (bank0, bank1)

    def locate(pointer: int, mapper: int) -> tuple[int, int]:
        # The recorded alternate-bank byte selects the physical PRG bank in
        # the existing emulator model; high encoded pointers use bank 0.
        bank = 0 if pointer >= BANK_SIZE else mapper & 1
        return bank, pointer & (BANK_SIZE - 1)

    script_bytes: set[int] = set()
    for (pointer, mapper), _ in scripts:
        bank, offset = locate(pointer, mapper)
        opcode = banks[bank][offset]
        if opcode >= len(lengths) or not lengths[opcode] or offset + lengths[opcode] > BANK_SIZE:
            raise ValueError('sampled command length is invalid or crosses a bank')
        script_bytes.update(bank * BANK_SIZE + offset + i for i in range(lengths[opcode]))

    record_bytes: set[int] = set()
    for (pointer, mapper, mode), _ in records:
        bank, offset = locate(pointer, mapper)
        if offset + 10 > BANK_SIZE:
            raise ValueError('sampled record fetch crosses a bank')
        fields = decode_slot_record(banks[bank][offset:offset + 10])
        used = record_used_offsets({'status': 'candidate', 'fields': fields, 'mode': mode})
        record_bytes.update(bank * BANK_SIZE + offset + i for i in used)

    missing_scripts = script_bytes & gaps
    missing_records = record_bytes & gaps
    return {'script_pointer_bank_pairs': len(scripts), 'script_fetches': sum(count for _, count in scripts),
            'script_physical_bytes': len(script_bytes), 'script_local_bytes': len(missing_scripts),
            'script_local_spans': _spans(missing_scripts),
            'record_pointer_bank_modes': len(records), 'record_loads': sum(count for _, count in records),
            'record_used_physical_bytes': len(record_bytes), 'record_local_bytes': len(missing_records),
            'record_local_spans': _spans(missing_records),
            'native_gap_instruction_starts': len(code),
            'native_gap_instruction_executions': sum(code.values())}


def validate_identity(trace: dict, expected: dict) -> None:
    """Reject a trace captured with different reference, source or runtime inputs."""
    if not isinstance(trace, dict) or any(trace.get(key) != value for key, value in expected.items()):
        raise ValueError('trace identity or source map does not match the current build')


def main() -> int:
    try:
        target, bank0, bank1, lengths = load_audited_banks()
        verified = verify_primary(ROOT, target)
        proof_path = ROOT / 'build/us-v1.5/proof.json'
        proof_sha = digest_file(proof_path)
        proof = json.loads(proof_path.read_text())
        path = ROOT / TRACE
        if path.is_symlink() or path.parent.is_symlink() or path.parent.parent.is_symlink():
            raise ValueError('refusing a symlinked trace')
        trace_raw = path.read_bytes()
        trace = json.loads(trace_raw)
        expected = {'reference_sha256': target['reference']['file']['sha256'],
                    'source_sha256': verified['source_sha256'],
                    'source_map_sha256': verified['source_map_sha256'],
                    'build_proof_sha256': proof_sha,
                    'collector_sha256': digest_file(ROOT / 'tools/trace_runtime_extents.py'),
                    'runtime_input_sha256': {name: digest_file(ROOT / name) for name in RUNTIME_INPUTS},
                    'emulator_core_sha256': spec(ROOT)['core_sha256']}
        validate_identity(trace, expected)
        gaps: set[int] = set()
        for gap in proof['local_prg_gaps']:
            start = gap['bank'] * BANK_SIZE + int(gap['cpu_start'], 16) - BANK_SIZE
            gaps.update(range(start, start + gap['size']))
        result = coverage(bank0, bank1, lengths, gaps, trace)
        if (digest_file(proof_path) != proof_sha
                or digest_file(input_path(ROOT, target, os.environ.get('BADP_ROM') or None)) != expected['reference_sha256']
                or digest_file(ROOT / 'src/us-v1.5/rom.s') != verified['source_sha256']
                or digest_file(ROOT / 'config/source-us-v1.5.json') != verified['source_map_sha256']
                or digest_file(ROOT / 'tools/trace_runtime_extents.py') != expected['collector_sha256']
                or {name: digest_file(ROOT / name) for name in RUNTIME_INPUTS} != expected['runtime_input_sha256']
                or path.read_bytes() != trace_raw):
            raise ValueError('trace or source changed during inventory')
        result.update({'target': 'us-v1.5', 'reference_sha256': trace['reference_sha256'],
                       'source_sha256': verified['source_sha256'], 'source_map_sha256': verified['source_map_sha256'],
                       'trace_sha256': hashlib.sha256(trace_raw).hexdigest(),
                       'interpretation': 'sampled reference-only paths under the recorded emulator mapping; not complete coverage'})
        output = path.parent / 'runtime-extents.json'
        if output.is_symlink():
            raise ValueError('refusing a symlinked output')
        with tempfile.TemporaryDirectory(prefix='runtime-extents-', dir=path.parent) as temporary:
            candidate = Path(temporary) / 'result.json'
            candidate.write_text(json.dumps(result, indent=2) + '\n')
            candidate.replace(output)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'runtime extent inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
