"""Synthetic regressions: no customer files, live network or canonical writes."""
import importlib.util
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/transformers'))
from pdf_evidence import bind_link, extract_pdf
from dimension_values import normalize
from drawing_quantities import summarize
from schedule_reconcile import reconcile
from delivery_coverage import assess


class EvidenceReliability(unittest.TestCase):
    def test_independent_forward_invalid_evidence_cases(self):
        for meaning in ('unknown', ' ', {}, None):
            self.assertEqual(normalize(dict(raw='W80cm', unit='cm', axes={'W':80}, meaning=meaning))['status'], 'unresolved')
        with self.assertRaises(ValueError):
            normalize(dict(raw='huge', unit='cm', axes={'W':10**400}, meaning='overall'))
        with self.assertRaises(ValueError):
            reconcile({}, {})
        with self.assertRaises(ValueError):
            reconcile([dict(tag='A', scope='floor', unit='each', source='p1', quantity=10**400)], [])
        key = dict(document_sha256='a'*64, physical_page=1, annotation_index=0)
        for row in (key, dict(key, uri=None, bbox=[0,0,1,1]), dict(key, uri='https://:443/chair', bbox=[0,0,1,1]), dict(key, uri='https://example.test/item')):
            with self.assertRaises(ValueError):
                bind_link([row], key)

    def test_same_page_and_suffix_never_join_across_documents(self):
        first = dict(document_sha256='a'*64, physical_page=1, annotation_index=0,
                     uri='https://example.test/easel', bbox=[0, 0, 10, 10])
        second = dict(first, document_sha256='b'*64, uri='https://example.test/lamp')
        key = {k: first[k] for k in ('document_sha256', 'physical_page', 'annotation_index')}
        self.assertEqual(bind_link([second, first], key)['uri'], first['uri'])
        with self.assertRaises(ValueError):
            bind_link([second], key)
        with self.assertRaises(ValueError):
            bind_link([first, first], key)
        with self.assertRaises(ValueError):
            bind_link([first], {'physical_page': 1})

    def test_real_pdf_annotation_and_physical_page_identity(self):
        import fitz
        with self.assertRaises(ValueError):
            extract_pdf(b'%PDF-1.7\ntruncated')
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((20, 30), 'Printed page 91')
        page.insert_link({'kind': fitz.LINK_URI, 'from': fitz.Rect(20, 20, 150, 35), 'uri': 'https://example.test/item?variant=2'})
        payload = doc.tobytes(); doc.close()
        result = extract_pdf(payload)
        self.assertEqual(result['pages'][0]['physical_page'], 1)
        self.assertIsNone(result['pages'][0]['printed_page'])
        self.assertEqual(result['annotations'][0]['uri'], 'https://example.test/item?variant=2')
        self.assertTrue(result['pages'][0]['words'])
        self.assertEqual(result, extract_pdf(payload))

    def test_raster_only_page_is_unparsed_not_empty_or_ocr_verified(self):
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        raster = fitz.Pixmap(fitz.csRGB, (0, 0, 20, 20), False)
        raster.clear_with(200)
        page.insert_image(fitz.Rect(20, 20, 120, 120), pixmap=raster)
        payload = doc.tobytes(); doc.close()
        result = extract_pdf(payload)
        self.assertEqual(len(result['pages']), 1)
        self.assertTrue(result['pages'][0]['text_layer_empty'])
        self.assertEqual(result['pages'][0]['words'], [])
        self.assertIsNone(result['pages'][0]['printed_page'])
        self.assertFalse(result['ocr_performed'])
        self.assertFalse(result['product_associations_inferred'])

    def page_fixture(self):
        import fitz
        doc = fitz.open()
        for label in ('91', '93', 'OCR label 94'):
            page = doc.new_page()
            page.insert_text((20, 30), label)
        payload = doc.tobytes(); doc.close()
        mapping = dict(schema_version=1, document_sha256=hashlib.sha256(payload).hexdigest(), page_count=3,
                       entries=[dict(physical_page=1, printed_page='91', status='visual-reviewed', evidence='synthetic reviewer A: footer region'),
                                dict(physical_page=2, printed_page='93', status='visual-reviewed', evidence='synthetic reviewer A: footer region'),
                                dict(physical_page=3, printed_page='94', status='ocr-unverified', evidence='synthetic OCR assertion, not visually checked')])
        return payload, mapping

    def test_page_map_binds_actual_bytes_without_numbering_or_ocr_inference(self):
        payload, mapping = self.page_fixture(); before = copy.deepcopy(mapping)
        result = extract_pdf(payload, mapping)
        self.assertEqual([page['physical_page'] for page in result['pages']], [1, 2, 3])
        self.assertEqual([page['printed_page'] for page in result['pages']], ['91', '93', None])
        self.assertNotIn('92', [page['printed_page'] for page in result['pages']])
        self.assertEqual(result['page_map'], mapping)
        self.assertEqual(mapping, before)
        self.assertFalse(result['page_map_source_verified'])
        self.assertFalse(result['ocr_performed'])
        self.assertNotIn('page_map', extract_pdf(payload))
        result['page_map']['entries'][0]['evidence'] = 'modified output'
        self.assertEqual(mapping, before)

    def test_page_map_rejects_source_version_missing_duplicate_and_invented_pages(self):
        payload, mapping = self.page_fixture()
        mutations = [lambda m: m.update(document_sha256='f' * 64), lambda m: m.update(page_count=True),
                     lambda m: m.update(schema_version=True), lambda m: m.update(page_count=4),
                     lambda m: m['entries'].pop(), lambda m: m['entries'][0].update(physical_page=True),
                     lambda m: m['entries'][0].update(physical_page=4), lambda m: m['entries'][0].update(physical_page=2),
                     lambda m: m['entries'][0].update(printed_page='93'), lambda m: m['entries'][0].update(printed_page=None),
                     lambda m: m['entries'][0].update(evidence=' '), lambda m: m['entries'][0].update(status='automatically-verified'),
                     lambda m: m.update(offset=90)]
        for mutate in mutations:
            candidate = copy.deepcopy(mapping); mutate(candidate)
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                extract_pdf(payload, candidate)
        with self.assertRaises(ValueError):
            extract_pdf(payload, None)
        # Even a byte-only PDF revision cannot inherit old page-map authority.
        with self.assertRaises(ValueError):
            extract_pdf(payload + b'\n% source revision\n', mapping)
        unresolved = copy.deepcopy(mapping)
        unresolved['entries'][0].update(printed_page=None, status='unresolved')
        self.assertIsNone(extract_pdf(payload, unresolved)['pages'][0]['printed_page'])

    def test_page_map_cli_rejects_null_and_duplicate_json_keys_without_writes(self):
        payload, mapping = self.page_fixture()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source = root / 'catalogue.pdf'; source.write_bytes(payload)
            map_path = root / 'map.json'
            for text in ('null', json.dumps(mapping).replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1')):
                map_path.write_text(text)
                result = subprocess.run([sys.executable, str(ROOT / 'tools/transformers/pdf_evidence.py'), 'extract', str(source), '--page-map', str(map_path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2); self.assertEqual(result.stdout, '')
                self.assertEqual(source.read_bytes(), payload); self.assertEqual(map_path.read_text(), text)

    def test_explicit_dimensions_and_conversion(self):
        result = normalize({'raw': 'W80 D60 H75 cm', 'unit': 'cm', 'meaning': 'overall',
                            'axes': {'W': 80, 'D': 60, 'H': 75}}, 'mm')
        self.assertEqual(result['axes'], {'W': 800, 'D': 600, 'H': 750})
        self.assertEqual(result['source']['raw'], 'W80 D60 H75 cm')
        self.assertEqual(normalize({'raw': 'L1900 B850 H1050', 'unit': 'mm', 'meaning': 'overall',
                                   'axes': {'L': 1900, 'B': 850, 'H': 1050}})['status'], 'unresolved')

    def test_dimensions_do_not_guess_units_or_axis_order(self):
        for value in ({'raw': '32 x 24 x 30', 'unit': None, 'axes': {'W': 32, 'D': 24, 'H': 30}, 'meaning': 'overall'},
                      {'raw': '80 x 60 cm', 'unit': 'cm', 'axes': {}, 'meaning': 'overall'}):
            self.assertEqual(normalize(value)['status'], 'unresolved')
        with self.assertRaises(ValueError):
            normalize({'raw': 'bad', 'unit': 'cm', 'meaning': 'overall', 'axes': {'W': float('nan')}})
        with self.assertRaises(ValueError):
            normalize({'raw': 'bad', 'unit': 'cm', 'meaning': 'overall', 'axes': {'W': True}})

    def test_instances_not_unique_labels_count_and_legend_excluded(self):
        with self.assertRaises(ValueError):
            summarize([None])
        rows = [dict(instance_id=str(i), document_sha256='a'*64, physical_page=1,
                     bbox=[i*10, 0, i*10+8, 8], tag='CH-A', scope='floor-1',
                     classification='instance', reviewed=True) for i in range(12)]
        rows += [dict(rows[0], instance_id='legend', bbox=[0, 50, 8, 58], classification='legend'),
                 dict(rows[0], instance_id='note', bbox=[0, 60, 8, 68], classification='note')]
        result = summarize(rows)
        with self.assertRaises(ValueError):
            summarize([dict(rows[0], bbox=[0, 0, 10**400, 8])])
        self.assertEqual(result['counts'][0]['quantity'], 12)
        self.assertEqual(result['excluded'], ['legend', 'note'])
        with self.assertRaises(ValueError):
            summarize(rows + [rows[0]])
        duplicate = dict(rows[0], instance_id='different-id')
        with self.assertRaises(ValueError):
            summarize(rows + [duplicate])
        rows[0]['reviewed'] = False
        self.assertFalse(summarize(rows)['complete'])

    def test_reconciliation_preserves_scope_unknown_and_conflict(self):
        def row(tag, value, scope='floor-1'):
            return dict(tag=tag, quantity=value, unit='each', scope=scope, source='sheet-1')
        result = reconcile([row('A', 12), row('B', None)], [row('A', 3), row('B', 0), row('C', 2)])
        self.assertEqual([r['status'] for r in result], ['conflict', 'unknown', 'missing-left'])
        self.assertEqual(reconcile([row('A', 12)], [row('A', 12, 'floor-2')])[0]['status'], 'missing-right')
        with self.assertRaises(ValueError):
            reconcile([row('A', 12), row('A', 12)], [])

    def test_absent_quantity_is_invalid_while_null_and_missing_rows_stay_distinct(self):
        row = dict(tag='A', scope='floor', unit='each', source='source.pdf#physical-page=1', quantity=None)
        self.assertEqual(reconcile([row], [dict(row, quantity=0)])[0]['status'], 'unknown')
        self.assertEqual(reconcile([row], [])[0]['status'], 'missing-right')
        del row['quantity']
        with self.assertRaises(ValueError):
            reconcile([row], [])

    def test_sourced_cross_package_buy_once_notes_survive_without_implicit_merging(self):
        note = dict(document_sha256='a' * 64, physical_page=3, printed_page='91',
                    region='package overlap note', text='F-01 uses lighting L-01; F-02 uses lighting L-02; procure each pair once')
        left = [dict(tag=tag, scope='furniture', unit='each', quantity=1, source='furniture.pdf#physical-page=3',
                     overlap_note=note, proposed_pair=pair) for tag, pair in [('F-01', 'L-01'), ('F-02', 'L-02')]]
        right = [dict(tag=tag, scope='lighting', unit='each', quantity=1, source='lighting.pdf#physical-page=8')
                 for tag in ['L-01', 'L-02']]
        result = reconcile(left, right)
        self.assertEqual(len(result), 4)
        self.assertEqual({row['status'] for row in result}, {'missing-left', 'missing-right'})
        preserved = [row['left'] for row in result if row['left']]
        self.assertEqual([row['proposed_pair'] for row in preserved], ['L-01', 'L-02'])
        self.assertTrue(all(row['overlap_note'] == note for row in preserved))
        self.assertTrue(all('procurement_total' not in row for row in result))

    def test_coverage_cannot_silently_drop_lighting(self):
        result = assess(['chair', 'lamp'], [{'item': 'chair', 'status': 'verified', 'artifact': 'chair.pdf', 'sha256': 'a'*64}])
        self.assertFalse(result['complete'])
        self.assertEqual(result['missing'], ['lamp'])
        result = assess(['chair', 'lamp'], [dict(item='chair', status='unresolved', reason='No image'),
                                          dict(item='lamp', status='unresolved', reason='No renderer')])
        self.assertTrue(result['accounted_for'])
        self.assertFalse(result['complete'])
        with self.assertRaises(ValueError):
            assess(['chair'], [dict(item='chair', status='verified')])


if __name__ == '__main__':
    unittest.main()
