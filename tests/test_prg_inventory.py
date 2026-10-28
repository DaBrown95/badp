"""PRG use accounting tests use synthetic spans and trace metadata only."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.native_control_flow import dispatch_lookup_spans
from tools.prg_inventory import (_optional_trace, expansion_counts, palette_script_spans,
                                 palette_setup_spans, script_graph_spans, summarize)


class PrgInventoryTests(unittest.TestCase):
    def test_conditional_expansion_counts_unique_physical_bytes_and_preserves_baseline(self):
        self.assertEqual(expansion_counts([(1, 3), (2, 2)], [(1, 4), (4, 2)]),
                         {'baseline_bytes': 3, 'expanded_bytes': 5, 'added_bytes': 2})
        with self.assertRaisesRegex(ValueError, 'lost baseline'):
            expansion_counts([(1, 2)], [(2, 2)])
        for invalid in ([(-1, 1)], [(0x7fff, 2)], [(True, 1)], [(0, 0)]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                expansion_counts([], invalid)

    def test_dispatch_aliases_are_retained_and_physical_bytes_count_once(self):
        spans = dispatch_lookup_spans()
        result = summarize({'native_dispatch_lookup_bytes': spans, 'source_code': [(0x570f, 59)]})
        self.assertEqual(result['category_bytes']['native_dispatch_lookup_bytes'], 965)
        self.assertEqual(result['source_and_candidate_data_bytes'], 59)
        self.assertEqual(sum(size for _, size in spans), 1024)
        overlap = [r for r in result['evidence_spans'] if r['physical_prg_offset'] == 0x570f][0]
        self.assertEqual(overlap['uses'], ['source_code', 'native_dispatch_lookup_bytes'])

    def test_aliases_overlap_and_banks_are_counted_physically_once(self):
        result = summarize({'source_code': [(0, 3), (0, 3)],
                            'source_data': [(8, 2)],
                            'candidate_map_chunks': [(2, 3), (10, 2)],
                            'candidate_sprite_bytes': [(4, 1)],
                            'candidate_script_bytes': [(3, 2)],
                            'candidate_record_bytes': [(3, 1), (8, 1)]}, bank_size=8, bank_count=2)
        counts = result['category_bytes']
        self.assertEqual((counts['source_code'], counts['source_data']), (3, 2))
        self.assertEqual((counts['candidate_map_chunks'], counts['candidate_sprite_bytes']), (5, 1))
        self.assertEqual(result['source_and_candidate_data_bytes'], 2)
        self.assertEqual(result['map_and_candidate_script_bytes'], 2)
        self.assertEqual(result['record_and_candidate_script_bytes'], 1)
        self.assertEqual(result['uncatalogued_bytes'], 7)
        self.assertEqual([(s['bank'], s['physical_prg_offset'], s['size'])
                          for s in result['uncatalogued_spans']], [(0, 5, 3), (1, 12, 4)])
        groups = {tuple(g['uses']): g['bytes'] for g in result['use_combinations']}
        self.assertEqual(groups[('source_code', 'candidate_map_chunks')], 1)
        self.assertEqual(groups[('candidate_map_chunks', 'candidate_sprite_bytes', 'candidate_script_bytes')], 1)
        self.assertEqual(sum(groups.values()), 16)

    def test_evidence_partition_retains_holes_overlaps_and_bank_boundary(self):
        result = summarize({'source_code': [(0, 2)],
                            'candidate_script_bytes': [(1, 2), (4, 1)]},
                           bank_size=4, bank_count=2)
        spans = result['evidence_spans']
        self.assertEqual([(s['physical_prg_offset'], s['size'], s['uses']) for s in spans],
                         [(0, 1, ['source_code']),
                          (1, 1, ['source_code', 'candidate_script_bytes']),
                          (2, 1, ['candidate_script_bytes']), (3, 1, []),
                          (4, 1, ['candidate_script_bytes']), (5, 3, [])])
        self.assertEqual(spans[4]['bank'], 1)
        self.assertEqual(spans[4]['cpu_start'], '0x8000')
        self.assertEqual(sum(s['size'] for s in spans), 8)

    def test_rejects_invalid_or_cross_bank_spans(self):
        for span in ((7, 2), (15, 2), (0, 0), (-1, 1), (True, 1), (0, '1')):
            with self.subTest(span=span), self.assertRaises(ValueError):
                summarize({'source_code': [span]}, bank_size=8, bank_count=2)
        with self.assertRaises(ValueError):
            summarize({'unknown': [(0, 1)]}, bank_size=8, bank_count=2)

    def test_unreferenced_map_slot_does_not_hide_candidate_script(self):
        result = summarize({'candidate_unreferenced_map_slots': [(1, 4)],
                            'candidate_script_bytes': [(3, 3)]}, bank_size=8, bank_count=1)
        self.assertEqual(result['category_bytes']['candidate_unreferenced_map_slots'], 4)
        self.assertEqual(result['unreferenced_map_slot_and_candidate_script_bytes'], 2)
        self.assertEqual(result['map_and_candidate_script_bytes'], 0)
        self.assertEqual(result['source_and_candidate_data_bytes'], 0)
        self.assertEqual(result['uncatalogued_bytes'], 3)
        groups = {tuple(g['uses']): g['bytes'] for g in result['use_combinations']}
        self.assertEqual(groups[('candidate_unreferenced_map_slots', 'candidate_script_bytes')], 2)

    def test_candidate_audio_remains_distinct_from_runtime_observations(self):
        result = summarize({'observed_audio_commands': [(0, 2)],
                            'candidate_audio_commands': [(1, 3)]}, bank_size=8, bank_count=1)
        self.assertEqual(result['observed_and_candidate_audio_bytes'], 1)
        self.assertEqual(result['uncatalogued_bytes'], 4)
        self.assertEqual(result['category_bytes']['observed_audio_commands'], 2)
        self.assertEqual(result['category_bytes']['candidate_audio_commands'], 3)

    def test_script_inventory_keeps_both_graphs_and_inline_tables(self):
        def location(offset):
            return {'bank_offset': offset, 'physical_prg_offset': offset}
        descriptor_graph = {'unprocessed': [], 'nodes': [
            {'location': location(2), 'length': 2}]}
        direct_graph = {'unprocessed': [], 'nodes': [
            {'location': location(2), 'length': 2,
             'lookup_records': [{'location': location(8), 'size': 4}]},
            {'location': location(0x7fff), 'length': 2}]}
        spans = script_graph_spans([descriptor_graph, direct_graph])
        self.assertEqual(spans, [(2, 2), (2, 2), (8, 4)])
        result = summarize({'candidate_script_bytes': spans}, bank_size=0x8000, bank_count=1)
        self.assertEqual(result['category_bytes']['candidate_script_bytes'], 6)
        direct_graph['unprocessed'] = [1]
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            script_graph_spans([descriptor_graph, direct_graph])

    def test_static_sprite_evidence_does_not_hide_observed_overlap(self):
        result = summarize({'candidate_sprite_bytes': [(0, 2)],
                            'candidate_sprite_static_bytes': [(1, 3)]}, bank_size=8, bank_count=1)
        self.assertEqual(result['observed_and_static_sprite_bytes'], 1)
        self.assertEqual(result['uncatalogued_bytes'], 4)
        self.assertEqual(result['category_bytes']['candidate_sprite_static_bytes'], 3)

    def test_map_and_text_headers_do_not_claim_payloads(self):
        result = summarize({'source_data': [(1, 2), (6, 2)],
                            'candidate_map_header_bytes': [(1, 2)],
                            'candidate_map_grid_bytes': [(3, 3)],
                            'packed_text_header_bytes': [(6, 2)],
                            'packed_text_payload_bytes': [(8, 3)]}, bank_size=16, bank_count=1)
        self.assertEqual(result['source_and_candidate_map_header_bytes'], 2)
        self.assertEqual(result['source_and_candidate_map_grid_bytes'], 0)
        self.assertEqual(result['source_and_packed_text_header_bytes'], 2)
        self.assertEqual(result['source_and_packed_text_payload_bytes'], 0)
        self.assertEqual(result['source_and_candidate_data_bytes'], 4)

    def test_ppu_control_and_payload_ownership_are_counted_separately(self):
        result = summarize({'source_data': [(1, 2)],
                            'candidate_ppu_control_bytes': [(1, 2)],
                            'candidate_ppu_payload_bytes': [(2, 2)]}, bank_size=8, bank_count=1)
        self.assertEqual(result['source_and_candidate_ppu_control_bytes'], 2)
        self.assertEqual(result['source_and_candidate_ppu_payload_bytes'], 1)
        self.assertEqual(result['category_bytes']['candidate_ppu_payload_bytes'], 2)
        self.assertEqual(result['source_and_candidate_data_bytes'], 2)

    def test_ppu_stream_overlap_is_not_silently_assigned_exclusively(self):
        result = summarize({'candidate_script_bytes': [(2, 3)],
                            'candidate_ppu_stream_bytes': [(4, 2)]}, bank_size=8, bank_count=1)
        groups = {tuple(g['uses']): g['bytes'] for g in result['use_combinations']}
        self.assertEqual(groups[('candidate_script_bytes', 'candidate_ppu_stream_bytes')], 1)
        self.assertEqual(result['uncatalogued_bytes'], 4)

    def test_trace_identity_and_missing_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script, trace = root / 'test.lua', root / 'trace.json'
            script.write_text('-- synthetic trace script\n')
            source_hash = hashlib.sha256(script.read_bytes()).hexdigest()
            self.assertIsNone(_optional_trace(trace, script, 'reference', 'core'))
            data = {'reference_sha256': 'reference', 'script_sha256': source_hash,
                    'emulator_core_sha256': 'core',
                    'results': {'noah': {}, 'moses': {}, 'david': {}}}
            trace.write_text(json.dumps(data))
            self.assertEqual(_optional_trace(trace, script, 'reference', 'core'), data)
            for field in ('reference_sha256', 'script_sha256', 'emulator_core_sha256', 'results'):
                damaged = dict(data)
                damaged[field] = 'wrong' if field != 'results' else {'noah': {}}
                trace.write_text(json.dumps(damaged))
                with self.subTest(field=field), self.assertRaises(ValueError):
                    _optional_trace(trace, script, 'reference', 'core')
            trace.unlink()
            trace.symlink_to(root / 'missing')
            with self.assertRaisesRegex(ValueError, 'symlinked trace'):
                _optional_trace(trace, script, 'reference', 'core')

    def test_named_palette_script_paths_include_dynamic_exclusions_and_shared_headers(self):
        region = {'id': 'bank0-palette-header-8004', 'bank': 0, 'cpu': '0x8004', 'size': 3, 'kind': 'data'}
        source = ("BogusSetBackgroundPalettePointer Bank0::PaletteHeader8004\n"
                  "BogusSetSpritePalettePointer Bank0::PaletteHeader8004 ; synthetic\n"
                  "BogusSetSpritePalettePointer $0000\nBogusSetBackgroundPalettePointer $FFFF\n")
        self.assertEqual(palette_script_spans(source, [region]), [(4, 3), (7, 16), (4, 3), (8, 15)])
        for changed_source, changed_regions in ((source, []),
                                                (source.replace('PaletteHeader8004', 'PaletteHeader8005'), [region]),
                                                (source.replace('Bank0::PaletteHeader8004', '$8004'), [region]),
                                                (source, [{**region, 'bank': 1}])):
            with self.subTest(source=changed_source), self.assertRaises(ValueError):
                palette_script_spans(changed_source, changed_regions)

    def test_palette_setup_respects_sprite_skip_and_bank_bounds(self):
        pointers = bytes([4, 0x80, 4, 0x80])
        self.assertEqual(palette_setup_spans(pointers, sprite=False, bank_size=32),
                         [(4, 3), (7, 16), (4, 3), (7, 16)])
        self.assertEqual(palette_setup_spans(pointers[:2], sprite=True, bank_size=32),
                         [(4, 3), (8, 15)])
        for invalid in (b'', b'\x00', bytes([0, 0x7f]), bytes([16, 0x80])):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                palette_setup_spans(invalid, sprite=False, bank_size=32)


if __name__ == '__main__':
    unittest.main()
