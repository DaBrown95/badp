"""Proof freshness failures with synthetic bytes, without compiling game data."""
from contextlib import ExitStack
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import chr_assets
from tools.build_variant_source import digest
from tools.identify_rom import inspect_rom
from tools.verify_variant import ARTIFACTS, verify


class VariantProofTests(unittest.TestCase):
    def setUp(self):
        stack = ExitStack();self.addCleanup(stack.close)
        self.root = Path(stack.enter_context(tempfile.TemporaryDirectory()))
        self.directory = self.root / 'build/us-v1.4'
        self.directory.mkdir(parents=True)
        reference = b'NES\x1a\x04\x08' + bytes(10) + bytes(131072)
        self.target = {'id': 'us-v1.4', 'input_path': 'reference.nes', 'reference': inspect_rom(reference)}
        for name, value in {'reference.nes': reference, 'producer.py': b'synthetic verifier',
                            'config/tool.json': b'{}', 'config/link.cfg': b'link',
                            'include/nes.inc': b'include', 'src/reset.s': b'reset',
                            'src/common.s': b'synthetic common source',
                            'config/map.json': json.dumps({'regions': [], 'linker_config': 'config/link.cfg'}).encode(),
                            'config/cc65-toolchain.json': b'{"revision":"synthetic"}'}.items():
            self.write(self.root / name, value)
        asset = chr_assets.capture(reference[65552:], digest(reference), target='us-v1.4')
        changed_asset = chr_assets.changed_asset(asset)
        changed = chr_assets.encode(changed_asset, digest(reference), target='us-v1.4')
        negative = reference[:65552] + changed
        self.selected = {'chr': {'asset': asset, 'payload': reference[65552:], 'source': 'reference',
                                 'input_sha256': digest(chr_assets.serialize(asset)), 'options': {'target': 'us-v1.4'}}}
        self.regions = [{'bank': 0, 'cpu': '0x8000', 'size': 65536, 'kind': 'data'}]
        native = {'instruction_count': 0, 'instruction_code_bytes': 0}
        artifacts = {'bible-adventures.nes': reference, 'bible-adventures.dbg': b'debug', 'bible-adventures.map': b'map',
                     'source/rom.s': b'synthetic common source', 'source/nes.inc': b'include', 'source/link.cfg': b'link'}
        for name, value in {**artifacts, 'native-inventory.json': json.dumps(native).encode(),
                            'dispatch-inventory.json': b'{}', 'inputs/header.bin': reference[:16],
                            'inputs/chr.bin': reference[65552:], 'assets/chr.json': chr_assets.serialize(asset),
                            'controls/chr/asset.json': chr_assets.serialize(changed_asset),
                            'controls/chr/candidate.nes': negative}.items():self.write(self.directory / name, value)
        self.proof = dict(schema_version=1, target='us-v1.4', match=True,
                          reference_sha256=digest(reference), candidate_sha256=digest(reference),
                          source_sha256=digest(b'synthetic common source'), regions=self.regions,
                          input_sha256={'producer.py': digest(b'synthetic verifier')},
                          build_artifact_sha256={name: digest(artifacts[name]) for name in ARTIFACTS},
                          assets={'chr': {key: value for key, value in self.selected['chr'].items() if key not in ('asset', 'payload')}},
                          gaps=[], gap_sha256={}, source_control_checkpoint='analysis/us-v1.4/source-checkpoint/source-proof.json',
                          source_control_checkpoint_sha256='checkpoint', source_controls=1, symbol_controls=1,
                          native={'instructions': 0, 'bytes': 0}, counts=dict(code_bytes=0, data_bytes=65536, fill_bytes=0, local_prg_bytes=0, local_chr_bytes=65536),
                          asset_controls={'chr': {'candidate_sha256': digest(negative),
                                                 'changed_offsets': chr_assets.verify_control(reference, negative, 65552),
                                                 'asset_sha256': digest(chr_assets.serialize(changed_asset))}})
        self.proof['assets']['chr']['asset_sha256'] = digest(chr_assets.serialize(asset))
        profile = {'canonical_map': 'config/map.json', 'canonical_source': 'src/common.s', 'reset_source': 'src/reset.s', 'geometry': None}
        for name, value in {'load_profile': profile, 'compose': 'synthetic common source', 'target_regions': self.regions,
                            'source_regions': self.regions, 'input_names': {'producer.py'},
                            'verify_source': ({'controls': [1], 'symbol_controls': [1], 'gaps': []}, 'checkpoint'),
                            'native_inventory': native, 'dispatch_inventory': {}}.items():
            stack.enter_context(patch('tools.verify_variant.' + name, return_value=value))
        stack.enter_context(patch('tools.variant_assets.select', return_value=self.selected))
        stack.enter_context(patch('tools.variant_assets.spans', return_value={}))
        stack.enter_context(patch('tools.variant_assets.changed_payload', return_value=(changed_asset, changed)))
        self.save()

    @staticmethod
    def write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True);path.write_bytes(data)

    def save(self):
        (self.directory / 'proof.json').write_text(json.dumps(self.proof))

    def test_current_synthetic_build_and_stale_producer(self):
        self.assertEqual(verify(self.root, self.target)['data_bytes'], 65536)
        (self.root / 'producer.py').write_text('changed producer')
        with self.assertRaisesRegex(ValueError, 'inputs'):verify(self.root, self.target)

    def test_positive_and_negative_artifacts_must_match(self):
        (self.directory / 'source/rom.s').write_text('different assembly')
        with self.assertRaisesRegex(ValueError, 'artifact'):verify(self.root, self.target)
        (self.directory / 'source/rom.s').write_text('synthetic common source')
        (self.directory / 'controls/chr/candidate.nes').write_bytes((self.root / 'reference.nes').read_bytes())
        with self.assertRaises(ValueError):verify(self.root, self.target)

    def test_missing_asset_control_and_stale_checkpoint_fail_closed(self):
        controls = self.proof.pop('asset_controls');self.save()
        with self.assertRaisesRegex(ValueError, 'incomplete'):verify(self.root, self.target)
        self.proof['asset_controls'] = controls;self.proof['source_control_checkpoint_sha256'] = 'old';self.save()
        with self.assertRaisesRegex(ValueError, 'source-control'):verify(self.root, self.target)

    def test_changed_local_selection_is_not_credited(self):
        self.selected['chr']['source'] = 'local'
        with self.assertRaisesRegex(ValueError, 'selection'):verify(self.root, self.target)
