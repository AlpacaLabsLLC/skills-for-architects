"""Product CSV transaction behavior on isolated synthetic projects."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('product_library', ROOT / 'tools/workspace/product_library.py')
library = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(library)


class Transactions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'PROJECT.md').write_text('# Synthetic project\n')
        self.target = self.root / 'product-library.csv'

    def call(self, operation, request_id, expected='missing', **kwargs):
        return library.execute(self.root, operation, request_id, expected, **kwargs)

    def init(self):
        self.call('init', 'initialize')
        return library.sha(self.target.read_bytes())

    def test_preview_is_read_only_and_unknown_currency_stays_blank(self):
        result = library.preview(self.root, 'init')
        self.assertEqual(result['before_sha256'], 'missing')
        self.assertFalse(self.target.exists())
        self.assertFalse((self.root / 'ffe').exists())
        digest = self.init()
        self.call('append', 'first', digest, row={'SKU': 'A', 'List Price': '50'})
        rows = library.csv.parse_bytes(self.target.read_bytes(), library.csv.PRODUCT_HEADER, 'test')
        self.assertEqual(rows[1][library.csv.PRODUCT_HEADER.index('Currency')], '')

    def test_retry_exactly_once_and_payload_conflict(self):
        digest = self.init()
        kwargs = {'row': {'SKU': 'A', 'Selected Color/Finish': 'Blue', 'Tags': 'user-tag'}}
        receipt = self.call('append', 'first', digest, **kwargs)
        before = self.target.read_bytes()
        replay = self.call('append', 'first', digest, **kwargs)
        self.assertEqual(before, self.target.read_bytes())
        self.assertEqual(receipt['request_sha256'], replay['request_sha256'])
        self.assertTrue(replay['replayed'])
        with self.assertRaises(ValueError):
            self.call('append', 'first', digest, row={'SKU': 'B'})
        self.assertEqual(before, self.target.read_bytes())

    def test_stale_preview_and_malformed_csv_leave_bytes_unchanged(self):
        digest = self.init()
        self.call('append', 'first', digest, row={'SKU': 'A'})
        before = self.target.read_bytes()
        with self.assertRaises(ValueError):
            self.call('append', 'stale', digest, row={'SKU': 'B'})
        self.assertEqual(before, self.target.read_bytes())
        self.target.write_bytes(b'wrong,header\r\n')
        with self.assertRaises(ValueError):
            self.call('append', 'bad', library.sha(self.target.read_bytes()), row={'SKU': 'B'})
        self.assertEqual(self.target.read_bytes(), b'wrong,header\r\n')

    def test_partial_update_preserves_selection_and_user_overrides(self):
        digest = self.init()
        self.call('append', 'first', digest, row={'SKU': 'A', 'Selected Color/Finish': 'Blue', 'Tags': 'chosen'})
        self.call('update', 'second', library.sha(self.target.read_bytes()), row={'Lead Time': '8 weeks'}, match_column='SKU', match_value='A')
        rows = library.csv.parse_bytes(self.target.read_bytes(), library.csv.PRODUCT_HEADER, 'test')
        self.assertEqual(rows[1][19], 'Blue')
        self.assertEqual(rows[1][29], 'chosen')

    def test_append_validates_each_input_row_once(self):
        before = library.csv.encode_rows([list(library.csv.PRODUCT_HEADER)], library.csv.PRODUCT_HEADER)
        with patch.object(library.csv, 'validate_row', wraps=library.csv.validate_row) as validate:
            after = library.proposal(before, 'append', row=[{'SKU': 'A'}, {'SKU': 'B'}])
        self.assertEqual(validate.call_count, 2)
        rows = library.csv.parse_bytes(after, library.csv.PRODUCT_HEADER, 'test')
        self.assertEqual([row[8] for row in rows[1:]], ['A', 'B'])

    def test_empty_file_behavior_preserved(self):
        expected = library.csv.encode_rows([list(library.csv.PRODUCT_HEADER)], library.csv.PRODUCT_HEADER)
        self.assertEqual(library.proposal(b'', 'init'), expected)
        for operation in ('append', 'update'):
            with self.assertRaisesRegex(ValueError, 'existing library: file is empty'):
                library.proposal(b'', operation, row={'SKU': 'A'})

    def test_crash_after_csv_publish_resumes_without_duplicate(self):
        digest = self.init()
        with patch.object(library, 'publish_receipt', side_effect=OSError('interrupted receipt')):
            with self.assertRaises(OSError):
                self.call('append', 'first', digest, row={'SKU': 'A'})
        before = self.target.read_bytes()
        result = self.call('append', 'first', digest, row={'SKU': 'A'})
        self.assertEqual(before, self.target.read_bytes())
        self.assertTrue(result['recovered'])

    def test_crash_before_csv_publish_and_pending_conflict(self):
        digest = self.init()
        with patch.object(library.csv, 'atomic_write', side_effect=OSError('interrupted write')):
            with self.assertRaises(OSError):
                self.call('append', 'first', digest, row={'SKU': 'A'})
        with self.assertRaises(ValueError):
            self.call('append', 'other', digest, row={'SKU': 'B'})
        result = library.recover(self.root, 'first')
        self.assertTrue(result['recovered'])

    def test_recovery_refuses_unexpected_external_bytes(self):
        digest = self.init()
        with patch.object(library, 'publish_receipt', side_effect=OSError('interrupted receipt')):
            with self.assertRaises(OSError):
                self.call('append', 'first', digest, row={'SKU': 'A'})
        self.target.write_bytes(self.target.read_bytes() + self.target.read_bytes().splitlines(keepends=True)[1])
        before = self.target.read_bytes()
        with self.assertRaises(ValueError):
            library.recover(self.root, 'first')
        self.assertEqual(before, self.target.read_bytes())

    def test_request_path_and_symlink_refused(self):
        for request in ['../escape', '', 'a/b']:
            with self.assertRaises(ValueError):
                self.call('init', request)
        outside = self.root / 'other.csv'
        outside.write_text('retain')
        self.target.symlink_to(outside)
        with self.assertRaises(ValueError):
            self.call('init', 'symlink')
        self.assertEqual(outside.read_text(), 'retain')

    def test_lock_blocks_other_process(self):
        self.init()
        with library.locked(self.root):
            result = subprocess.run([sys.executable, str(ROOT / 'skills/product-library/scripts/csv-library.py'),
                                     'init', 'product', '--project', str(self.root)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('writer', result.stderr)

    def test_corrupt_receipt_or_artifact_blocks_retry(self):
        self.init()
        artifact = self.root / 'ffe/library/operations/initialize/after.csv'
        artifact.write_bytes(b'corrupt')
        before = self.target.read_bytes()
        with self.assertRaises(ValueError):
            self.call('init', 'initialize')
        self.assertEqual(before, self.target.read_bytes())

    def test_history_parents_synced_before_csv_publication(self):
        events = []
        sync = library.sync_directory
        atomic = library.csv.atomic_write
        def record_sync(path):
            events.append(('sync', Path(path).resolve()))
            sync(path)
        def record_write(*args, **kwargs):
            events.append(('csv', None))
            return atomic(*args, **kwargs)
        with patch.object(library, 'sync_directory', side_effect=record_sync), patch.object(library.csv, 'atomic_write', side_effect=record_write):
            self.init()
        before_write = events[:events.index(('csv', None))]
        for path in [self.root, self.root / 'ffe', self.root / 'ffe/library', self.root / 'ffe/library/operations']:
            self.assertIn(('sync', path.resolve()), before_write)

    def test_existing_history_parents_synced_before_csv_publication(self):
        # Another process may have created these entries but not synced them yet.
        (self.root / 'ffe/library/operations').mkdir(parents=True)
        events = []
        atomic = library.csv.atomic_write
        def record_write(*args, **kwargs):
            events.append(('csv', None))
            return atomic(*args, **kwargs)
        with patch.object(library, 'sync_directory', side_effect=lambda p: events.append(('sync', Path(p).resolve()))), patch.object(library.csv, 'atomic_write', side_effect=record_write):
            self.init()
        before_write = events[:events.index(('csv', None))]
        for path in [self.root, self.root / 'ffe', self.root / 'ffe/library']:
            self.assertIn(('sync', path.resolve()), before_write)


if __name__ == '__main__':
    unittest.main()
