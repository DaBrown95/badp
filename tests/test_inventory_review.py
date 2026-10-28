import copy
import hashlib
import json
import tempfile
from pathlib import Path
import unittest

from tools.inventory_review import MECHANISMS, apply_review
from tools.progress import accepted_primary


class InventoryReviewTests(unittest.TestCase):
    def fixture(self, root):
        (root / 'evidence.txt').write_text('synthetic reviewed evidence')
        binding = dict(target='synthetic', reference_sha256='a' * 64,
                       source_sha256='b' * 64, source_map_sha256='c' * 64)
        decision = dict(kind='mechanism', state='closed', location='synthetic mechanism',
                        unknown='No reconstruction gap in this synthetic fixture.',
                        completion_effect='none', close_when='review source', decision='reviewed',
                        evidence=[dict(path='evidence.txt', scope='synthetic only',
                                       sha256=hashlib.sha256((root / 'evidence.txt').read_bytes()).hexdigest())])
        ledger = {**binding, 'schema_version': 1, 'review_input_sha256': {},
                  'decisions': [{**copy.deepcopy(decision), 'id': ident} for ident in sorted(MECHANISMS)]}
        audit = {**binding, 'prg_bytes': 4, 'representation_bytes': {'source_data': 4},
                 'regions': [dict(bank=0, cpu_start='0x8000', physical_prg_offset=0, size=4,
                                  representation='source_data', evidence_uses=['candidate_script_bytes', 'source_data'])]}
        return audit, ledger

    def test_complete_is_derived_and_overlaps_do_not_require_exclusivity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);audit, ledger = self.fixture(root)
            result = apply_review(audit, ledger, root)
            self.assertTrue(result['complete_executable_inventory'])
            self.assertEqual(result['inventory_review']['status'], 'accepted')
            self.assertEqual(result['regions'][0]['evidence_uses'], audit['regions'][0]['evidence_uses'])
            self.assertNotIn('exclusive_use_reviewed', result['regions'][0])

    def test_open_missing_and_stale_reviews_block_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);audit, ledger = self.fixture(root)
            variants = []
            altered = copy.deepcopy(ledger);altered['decisions'][0]['state'] = 'open';variants.append(altered)
            altered = copy.deepcopy(ledger);altered['decisions'].pop();variants.append(altered)
            altered = copy.deepcopy(ledger);altered['source_sha256'] = 'd' * 64;variants.append(altered)
            altered = copy.deepcopy(ledger);altered['review_input_sha256'] = {'changed-parser.py': 'e' * 64};variants.append(altered)
            altered = copy.deepcopy(ledger);altered['decisions'][0]['evidence'][0]['sha256'] = '0' * 64;variants.append(altered)
            for candidate in variants:
                with self.subTest(candidate=candidate['decisions'][0]['id']):
                    result = apply_review(audit, candidate, root)
                    self.assertFalse(result['complete_executable_inventory'])
                    self.assertTrue(result['inventory_review']['blockers'])
            (root / 'evidence.txt').unlink()
            self.assertFalse(apply_review(audit, ledger, root)['complete_executable_inventory'])

    def test_closing_storage_flag_cannot_hide_opaque_reconstruction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);audit, ledger = self.fixture(root)
            audit['regions'][0]['representation'] = 'unresolved_local'
            audit['representation_bytes'] = {'unresolved_local': 4}
            storage = copy.deepcopy(ledger['decisions'][0])
            storage.update(id='storage', kind='storage', bank=0, cpu=0x8000, size=4)
            ledger['decisions'].append(storage)
            result = apply_review(audit, ledger, root)
            self.assertFalse(result['complete_executable_inventory'])
            self.assertEqual(result['inventory_review']['opaque_storage_bytes'], 4)
            self.assertTrue(any(row['id'].startswith('opaque-') for row in result['inventory_review']['blockers']))

    def test_missing_evidence_duplicate_gate_and_unsafe_path_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);audit, ledger = self.fixture(root)
            for change in ('evidence', 'duplicate', 'path', 'scope', 'extent'):
                candidate = copy.deepcopy(ledger)
                if change == 'evidence':candidate['decisions'][0]['evidence'] = []
                elif change == 'duplicate':candidate['decisions'].append(candidate['decisions'][0])
                elif change == 'path':candidate['decisions'][0]['evidence'][0]['path'] = '../outside'
                elif change == 'scope':candidate['decisions'][0]['evidence'][0]['scope'] = ''
                else:
                    storage = copy.deepcopy(candidate['decisions'][0])
                    storage.update(id='storage', kind='storage', bank=1, cpu=0xffff, size=2)
                    candidate['decisions'].append(storage)
                with self.subTest(change=change), self.assertRaises(ValueError):
                    apply_review(audit, candidate, root)

    def test_progress_acceptance_recomputes_gates_and_requires_current_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);audit, ledger = self.fixture(root)
            for name in ('build/us-v1.5', 'analysis/us-v1.5', 'config'):
                (root / name).mkdir(parents=True)
            proof = root / 'build/us-v1.5/proof.json';proof.write_text('synthetic proof')
            ledger_path = root / 'config/inventory-review-us-v1.5.json'
            audit_path = root / 'analysis/us-v1.5/source-audit.json'
            verified = dict(code_bytes=0, data_bytes=4, fill_bytes=0,
                            source_sha256=audit['source_sha256'], source_map_sha256=audit['source_map_sha256'])
            target = {'reference': {'file': {'sha256': audit['reference_sha256']}, 'prg': {'size': 4}}}
            def save():
                ledger_path.write_text(json.dumps(ledger))
                audit.update(build_proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest(),
                             inventory_input_sha256={}, audit_input_sha256={
                                 'config/inventory-review-us-v1.5.json': hashlib.sha256(ledger_path.read_bytes()).hexdigest()})
                audit_path.write_text(json.dumps(audit))
            save()
            self.assertTrue(accepted_primary(root, target, verified))
            proof.write_text('different proof')
            self.assertFalse(accepted_primary(root, target, verified))
            save();ledger['decisions'][0]['state'] = 'open';save()
            audit['complete_executable_inventory'] = True;audit_path.write_text(json.dumps(audit))
            self.assertFalse(accepted_primary(root, target, verified))


if __name__ == '__main__':
    unittest.main()
