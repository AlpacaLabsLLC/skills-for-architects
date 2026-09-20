"""Synthetic durable URL clip-log tests; no transport or customer sources."""
import importlib.util
import json
import multiprocessing
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('clip_log', ROOT / 'tools/workspace/clip_log.py')
clip = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(clip)


def observation():
    return {
        'schema_version': 1, 'observation_id': 'ee8e2e63-2027-413a-994d-d6f3bccba093', 'observed_at': '2026-09-01T12:00:00Z',
        'source': {'kind': 'url', 'reference': 'https://example.com/chair?variant=blue&token=SECRET', 'content_sha256': None},
        'product': {'manufacturer': 'Synthetic Works', 'model': 'Chair', 'manufacturer_sku': 'C-02', 'vendor_item_id': 'V-37', 'storefront_id': None},
        'configuration': {'selected': {'finish': 'Blue'}, 'available': {'finish': ['Blue', 'Red']}},
        'fields': [{'field': 'image', 'kind': 'image', 'value': 'https://images.example.com/chair.jpg?X-Amz-Signature=SECRET',
                    'status': 'observed', 'locator': 'https://example.com/locator?sig=SECRET', 'unit': None, 'meaning': None,
                    'currency': None, 'price_basis': None, 'variant_match': 'exact'}]
    }


def hold_lock(project, ready):
    with clip.locked(clip.root_for(project)):
        ready.put(True)
        time.sleep(0.4)


class ClipLogTests(unittest.TestCase):
    def test_unknown_prior_is_rejected_before_log_append(self):
        with self.assertRaises(ValueError):
            clip.start(self.root, {'url': 'https://example.com/chair', 'configuration': {}}, 'new',
                       'ee8e2e63-2027-413a-994d-d6f3bccba093')
        self.assertFalse((self.root / 'ffe/clips/events.jsonl').exists())

    def test_start_replay_checks_missing_artifact(self):
        result = self.start(); clip.finish(self.root, 'capture-a', 'blocked')
        (self.root / 'ffe/clips/captures' / (result['capture_id'] + '.json')).unlink()
        with self.assertRaises((ValueError, OSError)):
            self.start()

    def test_existing_ancestry_is_synced_before_writer_yields(self):
        (self.root / 'ffe/clips/captures').mkdir(parents=True)
        with patch.object(clip, 'sync_directory') as sync:
            with clip.locked(clip.root_for(self.root)):
                self.assertIn((self.root.resolve(),), [call.args for call in sync.call_args_list])

    def test_encoded_secret_components_are_redacted(self):
        for url in ('https://example.com/%74oken/SECRET', 'https://example.com/access_token/SECRET',
                    'https://example.com/#access_token%3DSECRET'):
            with self.subTest(url=url):
                self.assertNotIn('SECRET', clip.redact_url(url)['url'])

    def test_capture_schema_and_runtime_reject_malformed_nested_metadata(self):
        result = self.start()
        start = clip.event_lines(clip.root_for(self.root))[0]
        document = clip.artifact(result['capture_id'], start, 'blocked', None, None, None)
        import copy
        mutations = [lambda d: d.update(schema_version=True), lambda d: d.update(created_at='nonsense'),
                     lambda d: d['urls'].update(resolved_url={'url': 42, 'redacted_components': False}),
                     lambda d: d['provenance'].update(extra='unexpected'),
                     lambda d: d['request']['submitted_url'].update(url='not-url')]
        for mutate in mutations:
            bad = copy.deepcopy(document); mutate(bad)
            bad['request']['fingerprint'] = clip.digest(clip.canonical({k:v for k,v in bad['request'].items() if k != 'fingerprint'}))
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                clip.validate_capture(bad, result['capture_id'], 'capture-a')
            with self.subTest(schema_mutate=mutate), self.assertRaises(ValueError):
                clip.validate_structure(bad, 'clip-capture.schema.json')

    def test_event_schema_and_runtime_are_closed_at_nested_request(self):
        self.start(); event = clip.event_lines(clip.root_for(self.root))[0]
        clip.validate_structure(event, 'clip-event.schema.json')
        event['request']['submitted_url']['redacted_components'] = [42]
        for validate in (clip.validate_event, lambda value: clip.validate_structure(value, 'clip-event.schema.json')):
            with self.assertRaises(ValueError): validate(event)

    def test_persisted_request_rejects_unredacted_secret_with_valid_hash(self):
        request = {'submitted_url': {'url': 'https://example.com/chair?token=SECRET', 'redacted_components': []},
                   'configuration': {}}
        request['fingerprint'] = clip.digest(clip.canonical(request))
        with self.assertRaises(ValueError): clip.validate_request(request)

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        (self.root / 'PROJECT.md').write_text('# synthetic\n')

    def tearDown(self):
        self.folder.cleanup()

    def start(self, request='capture-a'):
        return clip.start(self.root, {'url': 'https://example.com/chair?variant=blue&sku=C-02&token=SECRET#finish-blue',
                                      'configuration': {'finish': 'Blue'}}, request)

    def test_variant_preserved_secrets_redacted_everywhere_and_no_adoption(self):
        result = self.start()
        done = clip.finish(self.root, 'capture-a', 'success', observation(),
                           'https://dealer.example/chair?signature=SECRET&variant=blue',
                           'https://maker.example/chair?api_key=SECRET&sku=C-02')
        self.assertEqual(done['state'], 'terminal')
        persisted = b''.join(path.read_bytes() for path in (self.root / 'ffe/clips').rglob('*') if path.is_file())
        self.assertNotIn(b'SECRET', persisted)
        self.assertIn(b'variant=blue', persisted); self.assertIn(b'sku=C-02', persisted)
        capture = json.loads((self.root / 'ffe/clips/captures' / (result['capture_id'] + '.json')).read_bytes())
        self.assertFalse(capture['adoption_performed'])
        self.assertFalse((self.root / 'product-library.csv').exists())
        self.assertFalse((self.root / 'ffe/items').exists())

    def test_same_request_replays_and_intentional_reclip_is_new_linked_capture(self):
        first = self.start(); clip.finish(self.root, 'capture-a', 'blocked')
        replay = self.start()
        self.assertEqual(replay['capture_id'], first['capture_id']); self.assertEqual(replay['state'], 'replayed-terminal')
        second = clip.start(self.root, {'url': 'https://example.com/chair?variant=blue&sku=C-02', 'configuration': {'finish': 'Blue'}},
                            'capture-b', first['capture_id'])
        self.assertNotEqual(second['capture_id'], first['capture_id'])
        with self.assertRaises(ValueError):
            clip.start(self.root, {'url': 'https://example.com/other', 'configuration': {}}, 'capture-a')

    def test_hard_crash_after_artifact_recovers_terminal_and_before_artifact_stays_incomplete(self):
        first = self.start()
        root = clip.root_for(self.root)
        events = clip.event_lines(root); start_event = events[0]
        document = clip.artifact(first['capture_id'], start_event, 'partial', observation(), None, None)
        clip.publish_capture(root, document)  # simulated process death before terminal append
        recovered = clip.recover(self.root, 'capture-a')
        self.assertEqual(recovered['state'], 'recovered-terminal')
        clip.start(self.root, {'url': 'https://example.com/other', 'configuration': {}}, 'capture-b')
        self.assertEqual(clip.recover(self.root, 'capture-b')['state'], 'incomplete')

    def test_malformed_or_tampered_history_refuses_without_repair(self):
        self.start()
        log = self.root / 'ffe/clips/events.jsonl'
        original = log.read_bytes(); log.write_bytes(original + b'{')
        with self.assertRaises(ValueError): clip.history(self.root)
        self.assertEqual(log.read_bytes(), original + b'{')

    def test_history_is_local_and_filters_without_network(self):
        self.start(); clip.finish(self.root, 'capture-a', 'not-product')
        history = clip.history(self.root, url='https://example.com/chair?variant=blue&sku=C-02&token=ANY#finish-blue')
        self.assertEqual(len(history['captures']), 1)
        self.assertFalse(history['network_performed']); self.assertFalse(history['adoption_performed'])

    def test_history_on_a_project_without_clips_does_not_create_state(self):
        self.assertEqual(clip.history(self.root)['captures'], [])
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ['PROJECT.md'])

    def test_unattempted_started_and_host_blocked_outcomes_are_not_origin_dead(self):
        self.assertEqual(clip.history(self.root, url='https://example.com/unattempted')['captures'], [])
        self.start()
        self.assertEqual(clip.history(self.root)['captures'][0]['state'], 'incomplete')
        log = self.root / 'ffe/clips/events.jsonl'; original = log.read_bytes()
        with self.assertRaises(ValueError):
            clip.finish(self.root, 'capture-a', 'dead')
        self.assertEqual(log.read_bytes(), original)
        clip.finish(self.root, 'capture-a', 'blocked')
        result = clip.history(self.root)
        self.assertEqual(result['captures'][0]['outcome'], 'blocked')
        self.assertFalse(result['network_performed'])
        self.assertEqual(clip.history(self.root, url='https://example.com/unattempted')['captures'], [])

    def test_cooperating_writer_lock_refuses_second_writer(self):
        ready = multiprocessing.Queue(); process = multiprocessing.Process(target=hold_lock, args=(str(self.root), ready))
        process.start(); ready.get(timeout=3)
        with self.assertRaises(ValueError): self.start()
        process.join(timeout=3); self.assertEqual(process.exitcode, 0)

    def test_secret_named_configuration_is_refused(self):
        with self.assertRaises(ValueError):
            clip.start(self.root, {'url': 'https://example.com/chair', 'configuration': {'token': 'SECRET'}}, 'capture-a')

    def test_secret_path_fragment_and_observation_configuration_are_not_persistable(self):
        self.assertNotIn('SECRET', clip.redact_url('https://example.com/token/SECRET#access_token=SECRET')['url'])
        self.start(); document = observation(); document['configuration']['selected']['token'] = 'SECRET'
        with self.assertRaises(ValueError): clip.finish(self.root, 'capture-a', 'failed', document)

    def test_one_off_destination_needs_no_project_marker(self):
        target = Path(tempfile.mkdtemp())
        try:
            result = clip.start(target, {'url': 'https://example.com/chair?variant=blue', 'configuration': {}}, 'one-off', one_off=True)
            self.assertTrue((target / 'ffe/clips/events.jsonl').is_file())
            self.assertFalse((target / 'PROJECT.md').exists())
            self.assertEqual(result['state'], 'started')
        finally:
            import shutil; shutil.rmtree(target)

    def test_started_attempt_appears_in_history_and_bad_replay_is_refused(self):
        self.start()
        self.assertEqual(clip.history(self.root)['captures'][0]['state'], 'incomplete')
        log = self.root / 'ffe/clips/events.jsonl'
        event = json.loads(log.read_text().strip()); event['schema_version'] = True
        log.write_bytes(clip.canonical(event) + b'\n')
        with self.assertRaises(ValueError): clip.start(self.root, {'url': 'https://example.com/chair', 'configuration': {}}, 'capture-b')


if __name__ == '__main__':
    unittest.main()
