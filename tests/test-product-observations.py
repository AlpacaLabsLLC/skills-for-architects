"""Synthetic, read-only observation/record boundary tests."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('observations', ROOT / 'tools/transformers/product_observations.py')
observations = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(observations)
OID = 'ee8e2e63-2027-413a-994d-d6f3bccba093'
IID = '9d160a78-6ec9-48f0-a3f9-3a1effea7b0f'


def field(name='finish', value='Blue', kind='text', **kwargs):
    return dict(field=name, kind=kind, value=value, status='observed', locator='table#selected-finish',
                unit=None, meaning=None, currency=None, price_basis=None, variant_match='exact', **kwargs)


def observation():
    return {'schema_version': 1, 'observation_id': OID, 'observed_at': '2026-09-01T12:00:00Z',
            'source': {'kind': 'url', 'reference': 'https://example.com/chair?variant=blue&sku=C-02', 'content_sha256': None},
            'product': {'manufacturer': 'Synthetic Works', 'model': 'Chair', 'manufacturer_sku': 'C-02', 'vendor_item_id': 'V-37', 'storefront_id': None},
            'configuration': {'selected': {'finish': 'Blue'}, 'available': {'finish': ['Blue', 'Red']}},
            'fields': [field()]}


def item():
    return {'item_id': IID, 'revision': 3, 'tag': 'AP-01',
            'fields': {'manufacturer': 'Synthetic Works', 'model': 'Chair', 'finish': 'Red', 'notes': 'User override'},
            'provenance': {'finish': {'status': 'supplied', 'source': 'user correction'}}, 'decision_refs': ['decisions/0001-selection.md']}


def binding():
    return {'observation_id': OID, 'item_id': IID, 'expected_revision': 3, 'fields': {'finish': 'finish'}}


class ObservationContract(unittest.TestCase):
    def test_batch_rejects_custom_pilot_shape_and_duplicates(self):
        self.assertEqual(observations.validate_batch([observation()])['count'], 1)
        for values in ([], [observation(), observation()],
                       [observation(), {'identity': {}, 'dimensions_as_printed': '80 x 60'}]):
            with self.assertRaises(ValueError):
                observations.validate_batch(values)

    def test_wrong_product_binding_blocks_missing_field_proposal(self):
        for identity in ('manufacturer', 'model', 'manufacturer_sku', 'vendor_item_id', 'storefront_id'):
            original = item(); original['fields'].pop('finish')
            original['fields'][identity] = 'Another product'
            document = observation(); document['product'][identity] = 'Captured product'
            result = observations.adapt([document], [original], [binding()])
            self.assertNotIn('finish', result['record_proposal']['items'][0]['fields'])
            self.assertEqual(result['conflicts'][0]['code'], 'product-identity-conflict')
            self.assertEqual(result['audit_observations'][0]['status'], 'unavailable')

    def test_schema_vocabulary_fails_closed(self):
        with self.assertRaises(ValueError):
            observations.check('a', {'type': 'string', 'maxLength': 0}, {})

    def test_schema_preflight_rejects_unsupported_assertions_in_branches(self):
        for schema in (
            {'if': {'maxLength': 0}, 'then': {'const': 'b'}},
            {'oneOf': [{'maxLength': 0}, {'type': 'string'}]},
            {'$ref': '#/$defs/text', 'const': 'b', '$defs': {'text': {'type': 'string'}}},
            {'properties': {'unused': {'maxLength': 0}}},
        ):
            with self.subTest(schema=schema), self.assertRaises(ValueError):
                observations.check('a', schema, schema)

    def test_invalid_record_provenance_rejected(self):
        original = item(); original['provenance']['finish']['status'] = 'guessed'
        with self.assertRaises(ValueError):
            observations.adapt([observation()], [original], [binding()])

    def test_dimension_semantics_and_price_basis_survive_projection(self):
        document = observation()
        dimension = field('width', 32, 'quantity'); dimension.update(unit='in', meaning='overall width')
        price = field('price', 100, 'price'); price.update(currency='USD', price_basis='per pair, tax excluded')
        document['fields'] = [dimension, price]
        selected = binding(); selected['fields'] = {'width': 'width', 'price': 'price'}
        result = observations.adapt([document], [item()], [selected])
        self.assertEqual(result['audit_observations'][0]['value'], {'value': 32, 'unit': 'in', 'meaning': 'overall width'})
        self.assertEqual(result['audit_observations'][1]['value'], {'amount': 100, 'currency': 'USD', 'basis': 'per pair, tax excluded'})

    def test_unadopted_observation_has_no_item_binding_and_preserves_variant_urls(self):
        document = observation()
        before = copy.deepcopy(document)
        observations.validate(document)
        self.assertEqual(document, before)
        self.assertNotIn('item_id', document)

    def test_available_offerings_do_not_invent_selected_product_or_manufacturer_sku(self):
        document = observation()
        document['product'].update(manufacturer_sku=None, vendor_item_id='store-offering-7', storefront_id='listing-12')
        document['configuration']['selected'] = {}
        document['fields'] = [field(value=None)]
        document['fields'][0].update(status='unknown', variant_match='family')
        original = item(); original['fields'].pop('finish')
        result = observations.adapt([document], [original], [binding()])
        self.assertNotIn('finish', result['record_proposal']['items'][0]['fields'])
        self.assertIsNone(document['product']['manufacturer_sku'])
        self.assertEqual(document['product']['vendor_item_id'], 'store-offering-7')
        self.assertEqual(document['configuration']['available']['finish'], ['Blue', 'Red'])
        self.assertFalse(result['adoption_performed'])

    def test_price_provenance_keeps_vendor_url_date_currency_basis_and_configuration_certainty(self):
        document = observation()
        document['source']['reference'] = 'https://vendor.example/chair?finish=blue&offering=37'
        price = field('price', 125, 'price'); price.update(currency='USD', price_basis='per pair, excluding tax')
        document['fields'] = [price]
        selected = binding(); selected['fields'] = {'price': 'list_price'}
        result = observations.adapt([document], [item()], [selected])
        proposed = result['record_proposal']['items'][0]
        self.assertEqual(proposed['fields']['list_price'], {'amount': 125, 'currency': 'USD', 'basis': 'per pair, excluding tax'})
        self.assertEqual(proposed['provenance']['list_price']['source'], document['source']['reference'])
        self.assertEqual(proposed['provenance']['list_price']['retrieved_at'], document['observed_at'])
        document['fields'][0]['variant_match'] = 'family'
        self.assertNotIn('list_price', observations.adapt([document], [item()], [selected])['record_proposal']['items'][0]['fields'])

    def test_rejects_missing_currency_status_and_invented_fields(self):
        for mutate in [lambda d: d['fields'][0].pop('currency'),
                       lambda d: d['fields'][0].update(status='verified-by-ai'),
                       lambda d: d.update(item_id=IID),
                       lambda d: d['source'].update(cookies='secret'),
                       lambda d: d.update(schema_version=True)]:
            with self.subTest(mutate=mutate):
                document = observation()
                mutate(document)
                with self.assertRaises(ValueError):
                    observations.validate(document)

    def test_price_unknown_currency_is_explicit_and_not_adoptable(self):
        document = observation()
        document['fields'] = [field('price', 99.50, 'price')]
        observations.validate(document)
        selected = binding(); selected['fields'] = {'price': 'list_price'}
        result = observations.adapt([document], [item()], [selected])
        value = result['audit_observations'][0]['value']
        self.assertEqual(value['currency'], None)
        self.assertNotIn('list_price', result['record_proposal']['items'][0]['fields'])
        self.assertTrue(result['notices'])

    def test_unknown_or_unavailable_cannot_carry_asserted_values(self):
        for status in ('unknown', 'unavailable'):
            document = observation()
            document['fields'][0]['status'] = status
            with self.assertRaises(ValueError):
                observations.validate(document)

    def test_prices_and_dimensions_reject_wrong_metadata_types(self):
        for value in (True, 'USD 99', float('nan')):
            document = observation(); document['fields'] = [field('price', value, 'price')]
            with self.assertRaises(ValueError):
                observations.validate(document)
        document = observation(); document['fields'][0]['currency'] = 'USD'
        with self.assertRaises(ValueError):
            observations.validate(document)

    def test_requires_explicit_selected_binding_and_matching_revision(self):
        for selections in ([], [dict(binding(), expected_revision=2)], [dict(binding(), item_id='wrong')],
                           [dict(binding(), fields={})], [dict(binding(), fields={'unknown': 'finish'})]):
            with self.assertRaises(ValueError):
                observations.adapt([observation()], [item()], selections)

    def test_conflict_preserves_user_fields_identity_provenance_and_input_bytes(self):
        document, original, selected = observation(), item(), binding()
        before = copy.deepcopy((document, original, selected))
        result = observations.adapt([document], [original], [selected])
        self.assertEqual((document, original, selected), before)
        self.assertEqual(result['record_proposal']['items'][0], original)
        self.assertEqual(result['conflicts'][0]['recorded'], 'Red')
        self.assertEqual(result['conflicts'][0]['observed'], 'Blue')
        self.assertTrue(result['requires_review'])
        self.assertFalse(result['specification_mutated'])

    def test_missing_field_can_be_proposed_without_adoption(self):
        original = item(); original['fields'].pop('finish'); original['provenance'].pop('finish')
        result = observations.adapt([observation()], [original], [binding()])
        proposed = result['record_proposal']['items'][0]
        self.assertEqual(proposed['fields']['finish'], 'Blue')
        self.assertEqual((proposed['item_id'], proposed['revision'], proposed['tag']), (IID, 3, 'AP-01'))
        self.assertEqual(result['expected_item_revisions'], {IID: 3})

    def test_existing_blank_is_a_preserved_user_value(self):
        original = item(); original['fields']['finish'] = ''
        result = observations.adapt([observation()], [original], [binding()])
        self.assertEqual(result['record_proposal']['items'][0]['fields']['finish'], '')
        self.assertTrue(result['conflicts'])

    def test_multiple_sources_do_not_silently_pick_a_value(self):
        first = observation(); second = copy.deepcopy(first)
        second['observation_id'] = '5dfd1e52-4ac2-439c-aa8c-09373fdc84f1'
        second['fields'][0]['value'] = 'Green'
        original = item(); original['fields'].pop('finish')
        selections = [binding(), dict(binding(), observation_id=second['observation_id'])]
        result = observations.adapt([first, second], [original], selections)
        self.assertNotIn('finish', result['record_proposal']['items'][0]['fields'])
        self.assertEqual(result['conflicts'][0]['code'], 'conflicting-observations')

    def test_inference_and_family_image_never_become_exact_selection(self):
        for status, match in [('inferred', 'exact'), ('observed', 'family')]:
            document = observation()
            document['fields'] = [field('image', 'https://example.com/family.jpg', 'image')]
            document['fields'][0].update(status=status, variant_match=match)
            selected = binding(); selected['fields'] = {'image': 'image'}
            result = observations.adapt([document], [item()], [selected])
            self.assertNotIn('image', result['record_proposal']['items'][0]['fields'])
            self.assertTrue(result['notices'])

    def test_output_is_accepted_by_existing_audit_and_record_interfaces(self):
        audit_spec = importlib.util.spec_from_file_location('audit', ROOT / 'tools/validators/ffe_audit.py')
        audit = importlib.util.module_from_spec(audit_spec); audit_spec.loader.exec_module(audit)
        record_spec = importlib.util.spec_from_file_location('record', ROOT / 'tools/workspace/ffe_records.py')
        record = importlib.util.module_from_spec(record_spec); record_spec.loader.exec_module(record)
        original = item(); original['fields'].pop('finish'); original['provenance'].pop('finish')
        result = observations.adapt([observation()], [original], [binding()])
        report = audit.audit({'schema_version': 1, 'mode': 'snapshot', 'started_at': '2026-09-01T12:00:00Z',
                              'items': [original], 'observations': result['audit_observations']})
        self.assertFalse(report['specification_mutated'])
        accepted = record.validate_items(result['record_proposal']['items'], [original])
        self.assertEqual(accepted[0]['fields']['finish'], 'Blue')

    def test_cli_validation_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'observation.json'; path.write_text(json.dumps(observation()))
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / 'tools/transformers/product_observations.py'), 'validate', str(path)],
                                    cwd=folder, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(folder).iterdir()), [path])
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
