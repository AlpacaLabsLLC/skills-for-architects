"""Synthetic report observations only; no customer inputs or PDF extraction claims."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/transformers'))
from lighting_report import normalize
from schedule_reconcile import reconcile


def source(page=1, digest='a' * 64, printed='187', locator='luminaire list row 1'):
    return dict(document_sha256=digest, physical_page=page, printed_page=printed, locator=locator)


def inventory(identifier='first', quantity=29, **changes):
    row = dict(observation_id=identifier, inventory_id='room-a/lamp-1',
               identity_evidence=dict(source=source(), basis='Same explicit room inventory row'),
               scope=dict(kind='room', id='building-1/room-a'), room='Room A',
               scene=dict(status='not-reported', name=None), surface='workplane',
               tag='L-01', variant=None, quantity=quantity, raw_quantity=str(quantity),
               unit='each', source=source())
    row.update(changes)
    return row


def result(identifier='metric-1', **changes):
    row = dict(result_id=identifier, scope=dict(kind='room', id='building-1/room-a'),
               room='Room A', scene=dict(status='not-reported', name=None),
               surface='workplane', metric='average illuminance', value=559,
               raw_value='559', unit='lx', condition='calculation height 0.8 m',
               source=source(3, printed='189', locator='surface result table'))
    row.update(changes)
    return row


def request(rows, results=None):
    return dict(schema_version=1, inventory_observations=rows, calculation_results=results or [])


class LightingReport(unittest.TestCase):
    def test_known_29_not_58_across_two_calculation_surfaces(self):
        rows = []
        for n, quantity in enumerate((9, 4, 5, 11), 1):
            for surface in ('workplane-a', 'workplane-b'):
                rows.append(inventory(f'{n}/{surface}', quantity, inventory_id=f'room-a/L-{n}',
                                      tag=f'L-{n}', surface=surface,
                                      source=source(3, locator=f'{surface}/inventory row {n}')))
        metrics = [result(), result('metric-2', surface='workplane-b', value=378, raw_value='378')]
        normalized = normalize(request(rows, metrics))
        self.assertEqual(sum(row['quantity'] for row in normalized['inventory']), 29)
        self.assertEqual(len(normalized['inventory']), 4)
        self.assertTrue(all(len(row['observations']) == 2 for row in normalized['inventory']))
        self.assertEqual(normalized['calculation_results'], metrics)
        self.assertFalse(normalized['source_verified'])
        self.assertFalse(normalized['coverage_verified'])

    def test_equal_rooms_scenes_variants_and_source_versions_stay_separate(self):
        first = inventory()
        alternatives = [dict(room='Room B'), dict(scope=dict(kind='room', id='building-2/room-a')),
                        dict(scene=dict(status='reported', name='evening')), dict(variant='wide optic'),
                        dict(source=source(digest='b' * 64),
                             identity_evidence=dict(source=source(digest='b' * 64), basis='Other report version')),
                        dict(inventory_id='second-inventory')]
        for patch in alternatives:
            with self.subTest(patch=patch):
                normalized = normalize(request([first, inventory('second', **patch)]))
                self.assertEqual(len(normalized['inventory']), 2)
                self.assertEqual([row['quantity'] for row in normalized['inventory']], [29, 29])

    def test_scene_and_room_inventory_are_distinct(self):
        rows = [inventory(scene=dict(status='reported', name='day')),
                inventory('second', scope=dict(kind='scene', id='building-1/room-a'),
                          scene=dict(status='reported', name='day'))]
        self.assertEqual(len(normalize(request(rows))['inventory']), 2)
        with self.assertRaisesRegex(ValueError, 'scene'):
            normalize(request([inventory(scope=dict(kind='scene', id='day'))]))

    def test_unknown_and_not_applicable_scene_are_not_conflated(self):
        rows = [inventory(), inventory('second', scene=dict(status='not-applicable', name=None))]
        self.assertEqual(len(normalize(request(rows))['inventory']), 2)
        with self.assertRaisesRegex(ValueError, 'scene.name'):
            normalize(request([inventory(scene=dict(status='reported', name=None))]))

    def test_missing_identity_is_not_deduced_from_equal_counts_or_labels(self):
        rows = [inventory('first', inventory_id=None, identity_evidence=None),
                inventory('second', inventory_id=None, identity_evidence=None)]
        groups = normalize(request(rows))['inventory']
        self.assertEqual(len(groups), 2)
        self.assertEqual([row['status'] for row in groups], ['unresolved-identity'] * 2)
        self.assertTrue(all(row['quantity'] is None for row in groups))
        self.assertEqual(groups[0]['observations'][0]['quantity'], 29)

    def test_identity_requires_source_backed_evidence(self):
        for patch in (dict(identity_evidence=None),
                      dict(identity_evidence=dict(source=source(digest='b' * 64), basis='Wrong version')),
                      dict(room=None)):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                normalize(request([inventory(**patch)]))

    def test_zero_null_and_conflicting_quantities(self):
        for values, status, quantity in (([0, 0], 'resolved', 0), ([None, None], 'unknown', None),
                                          ([0, None], 'unknown', None), ([29, 30], 'conflict', None),
                                          ([None, 29, 30], 'conflict', None)):
            groups = normalize(request([inventory(str(i), value) for i, value in enumerate(values)]))['inventory']
            self.assertEqual((groups[0]['status'], groups[0]['quantity']), (status, quantity))
            self.assertEqual([row['quantity'] for row in groups[0]['observations']], values)

    def test_repeated_page_retains_every_observation_and_locator(self):
        rows = [inventory(), inventory('again', source=source(4, printed=None, locator='repeated table'))]
        original = copy.deepcopy(rows)
        group = normalize(request(rows))['inventory'][0]
        self.assertEqual(group['quantity'], 29)
        self.assertEqual(group['observations'], original)
        group['observations'][0]['source']['printed_page'] = 'mutated copy'
        self.assertEqual(rows, original)

    def test_duplicate_ids_and_malformed_numbers_reject(self):
        with self.assertRaisesRegex(ValueError, 'observation_id'):
            normalize(request([inventory(), inventory()]))
        with self.assertRaisesRegex(ValueError, 'result_id'):
            normalize(request([], [result(), result()]))
        for invalid in (True, -1, float('nan'), float('inf'), 10**400, '29'):
            with self.subTest(invalid=repr(invalid)), self.assertRaisesRegex(ValueError, 'quantity'):
                normalize(request([inventory(quantity=invalid)]))
        for invalid in (True, float('nan'), 10**400):
            with self.assertRaisesRegex(ValueError, 'value'):
                normalize(request([], [result(value=invalid)]))

    def test_source_locators_and_required_keys_are_validated(self):
        for field, value in (('document_sha256', None), ('document_sha256', 'not-a-hash'),
                             ('physical_page', 0), ('physical_page', True), ('printed_page', 187),
                             ('locator', '')):
            row = inventory(); row['source'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                normalize(request([row]))
        row = inventory(); del row['source']['document_sha256']
        with self.assertRaisesRegex(ValueError, 'document_sha256'):
            normalize(request([row]))

    def test_unversioned_legacy_data_never_silently_reinterpreted(self):
        for invalid in ([inventory()], {'inventory_observations': [inventory()]},
                        dict(request([inventory()]), schema_version=True),
                        dict(request([inventory()]), schema_version=2), request([])):
            with self.assertRaises(ValueError):
                normalize(invalid)

    def test_legacy_reconciliation_requires_explicit_consumer_scope(self):
        groups = normalize(request([inventory(), inventory('again', surface='ceiling')]))['inventory']
        group = groups[0]
        # Caller explicitly selects the resolved room inventory. No implicit scene/variant projection.
        left = [dict(tag=group['tag'], scope=group['scope']['id'], unit=group['unit'],
                     quantity=group['quantity'], source=json.dumps(group['observations']))]
        right = [dict(left[0], source='schedule row 1')]
        self.assertEqual(reconcile(left, right)[0]['status'], 'match')
        distinct = normalize(request([inventory(), inventory('evening', scene=dict(status='reported', name='evening'))]))['inventory']
        self.assertEqual(len(distinct), 2)
        careless_projection = [dict(tag=row['tag'], scope=row['scope']['id'], unit=row['unit'],
                                    quantity=row['quantity'], source=json.dumps(row['observations'])) for row in distinct]
        with self.assertRaisesRegex(ValueError, 'Duplicate comparison key'):
            reconcile(careless_projection, right)

    def test_cli_rejects_duplicate_json_keys_and_preserves_input(self):
        with tempfile.TemporaryDirectory(prefix='as-lighting-report-') as tmp:
            file = Path(tmp) / 'input.json'
            file.write_text(json.dumps(request([inventory()])))
            original = file.read_bytes()
            command = [sys.executable, str(ROOT / 'tools/transformers/lighting_report.py'), str(file)]
            ran = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, ran.stderr)
            self.assertEqual(json.loads(ran.stdout)['inventory'][0]['quantity'], 29)
            self.assertEqual(file.read_bytes(), original)
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ['input.json'])
            file.write_text('{"schema_version": 1, "schema_version": 1}')
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertIn('duplicate JSON key', rejected.stderr)


if __name__ == '__main__':
    unittest.main()
