"""Decode one audio command according to the reconstructed v1.5 interpreter.

This does not infer stream bounds or reachability. AudioReadCommand copies five
bytes, but the interpreter consumes different amounts according to the opcode.
"""
from __future__ import annotations


def decode_command(data: bytes) -> dict:
    """Decode one command; reject truncated input without reading a ROM."""
    if not data:
        raise ValueError('missing audio command')
    op = data[0]
    if op < 0xA0:
        kind, size = 'note', 1
    elif op < 0xC0:
        kind, size = 'instrument', 1
    elif op == 0xC0:
        kind, size = 'loop', 4
    elif op in (0xC2, 0xC3):
        kind, size = ('set_channel_mask' if op == 0xC2 else 'clear_channel_mask'), 1
    else:
        sub = op & 0x1F
        if sub < 4:
            kind, size = 'select_channel', 1
        elif sub < 8:
            kind, size = 'restore_pointer', 1
        elif sub < 12:
            kind, size = 'stop_voice', 1
        elif sub < 16:
            kind, size = 'write_register', 2
        elif sub < 20:
            kind, size = 'restart_channel', 1
        elif sub < 24:
            kind, size = 'enable_channel', 1
        elif sub == 24:
            kind, size = 'select_all_channels', 1
        elif sub == 25:
            kind, size = 'write_five', 5
        elif sub == 27:
            kind, size = 'delay', 2
        else:
            kind, size = 'default_control', 1
    if len(data) < size:
        raise ValueError('truncated audio command')
    result = {'kind': kind, 'opcode': op, 'size': size}
    if kind == 'note':
        result.update(duration_index=op >> 5, note_index=op & 0x1F)
    elif kind == 'instrument':
        result['instrument'] = op & 0x1F
    elif kind == 'loop':
        result.update(count=data[1], target=int.from_bytes(data[2:4], 'little'))
    elif kind == 'write_register':
        result.update(register=op & 3, value=data[1])
    elif kind == 'write_five':
        # The fifth register gets a stale stack byte, not a sixth source byte.
        result['source_values'] = list(data[1:5])
    elif kind == 'delay':
        result['duration'] = data[1]
    elif kind == 'select_channel':
        result['channel'] = op & 3
    return result


def inventory_observed(trace: dict, bank0: bytes, bank1: bytes) -> dict:
    """Validate and decode captured five-byte reads by physical PRG offset.

    A captured read is evidence of one entry, not an inferred stream boundary.
    Returned data includes game bytes and must remain local.
    """
    if len(bank0) != 0x8000 or len(bank1) != 0x8000:
        raise ValueError('expected two full PRG banks')
    entries = {}
    for scenario, result in trace['results'].items():
        for key, count in result['reads'].items():
            parts = key.split(':')
            if (len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 10
                    or type(count) is not int or count <= 0):
                raise ValueError('invalid observed audio read')
            try:
                offset = int(parts[0], 16)
                raw = bytes.fromhex(parts[1])
            except ValueError as exc:
                raise ValueError('invalid observed audio read') from exc
            if len(raw) != 5 or not 0 <= offset < 0x10000:
                raise ValueError('invalid observed audio read')
            bank, position = divmod(offset, 0x8000)
            if position + 5 > 0x8000:
                raise ValueError('observed audio read crosses a physical bank')
            expected = (bank0, bank1)[bank][position:position + 5]
            if raw != expected:
                raise ValueError('observed audio read differs from reference')
            if offset not in entries:
                entries[offset] = {'physical_prg_offset': offset, 'bank': bank,
                                   'cpu_address': 0x8000 + position,
                                   'command': decode_command(raw), 'scenarios': {}}
            observations = entries[offset]['scenarios']
            observations[scenario] = observations.get(scenario, 0) + count
    by_byte = {}
    for offset, entry in entries.items():
        for byte in range(offset, offset + entry['command']['size']):
            by_byte.setdefault(byte, []).append(offset)
    conflicts = [{'physical_prg_offset': byte, 'entries': starts}
                 for byte, starts in sorted(by_byte.items()) if len(starts) > 1]
    return {'commands': [entries[a] for a in sorted(entries)],
            'command_bytes': len(by_byte), 'conflicts': conflicts}


def main() -> int:
    import json
    import sys
    from .script_entries import ROOT, load_audited_banks

    try:
        target, bank0, bank1, _ = load_audited_banks()
        trace_path = ROOT / 'analysis/us-v1.5/audio-sweep.json'
        trace = json.loads(trace_path.read_text())
        reference = target['reference']['file']['sha256']
        if trace['reference_sha256'] != reference:
            raise ValueError('audio trace reference does not match the audited ROM')
        result = inventory_observed(trace, bank0, bank1)
        result.update(target='us-v1.5', reference_sha256=reference,
                      interpretation='observed entries only; stream boundaries and other paths unverified')
        analysis = ROOT / 'analysis'
        output = analysis / 'us-v1.5/audio-inventory.json'
        if analysis.is_symlink() or output.parent.is_symlink() or output.is_symlink():
            raise ValueError('refusing a symlinked analysis output')
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.resolve().is_relative_to(analysis.resolve()):
            raise ValueError('analysis output escapes its local directory')
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'commands': len(result['commands']),
                          'command_bytes': result['command_bytes'],
                          'conflicting_bytes': len(result['conflicts']),
                          'output': 'analysis/us-v1.5/audio-inventory.json'}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'audio inventory failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
