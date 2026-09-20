import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preference', ROOT / 'tools/transformers/assistant_preference.py')
preference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preference)


class PreferenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='as-preference-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.target = self.root / 'AGENTS.md'

    def run_plan(self, action='enable', scope='project'):
        plan = preference.preview(self.target, scope, action)
        receipt = preference.apply(plan, plan['plan_sha256'])
        return plan, receipt

    def test_preview_has_no_writes_and_requires_explicit_target_scope_and_approval(self):
        plan = preference.preview(self.target, 'project', 'enable')
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(plan['operation'], 'create')
        self.assertIn(preference.PREFERENCE, plan['diff'])
        with self.assertRaises(preference.PreferenceError):
            preference.apply(plan, 'yes')
        self.assertEqual(list(self.root.iterdir()), [])
        for target, scope in [('AGENTS.md', 'project'), (self.target, 'global'), (self.root / 'missing' / 'AGENTS.md', 'user')]:
            with self.assertRaises(preference.PreferenceError):
                preference.preview(target, scope, 'enable')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_create_repeat_remove_and_absent_remove_do_not_claim_registration(self):
        plan, receipt = self.run_plan(scope='user')
        self.assertEqual(receipt['status'], 'preference-bytes-updated')
        self.assertEqual(receipt['norma_registration'], 'not-performed')
        self.assertEqual(receipt['future_selection'], 'not-verified')
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)
        before = self.target.stat().st_mtime_ns
        repeated, receipt = self.run_plan(scope='user')
        self.assertEqual(repeated['operation'], 'noop')
        self.assertEqual(receipt['status'], 'unchanged')
        self.assertEqual(self.target.stat().st_mtime_ns, before)
        self.run_plan('remove', 'user')
        self.assertEqual(self.target.read_bytes(), b'')
        missing = self.root / 'CLAUDE.md'
        remove = preference.preview(missing, 'user', 'remove')
        self.assertEqual(preference.apply(remove, remove['plan_sha256'])['status'], 'unchanged')
        self.assertFalse(missing.exists())

    def test_unrelated_bytes_roundtrip_including_bom_crlf_and_missing_final_newline(self):
        for original in [b'# Project\nKeep this.\n', b'# Project\r\nKeep this.\r\n', b'no final newline', b'\xef\xbb\xbf# BOM\r\nKeep this.', b'']:
            with self.subTest(original=original):
                self.target.write_bytes(original)
                os.chmod(self.target, 0o640)
                self.run_plan()
                content = self.target.read_bytes()
                if original.startswith(b'\xef\xbb\xbf'):
                    self.assertTrue(content.startswith(b'\xef\xbb\xbf'))
                self.run_plan('remove')
                self.assertEqual(self.target.read_bytes(), original)
                self.assertEqual(self.target.stat().st_mode & 0o777, 0o640)
                self.assertFalse(list(self.root.glob('.as-preference-*')))

    def test_update_changes_only_owned_block_and_diff_is_complete(self):
        original = ('# Before\r\n' + preference.START + '\r\nOld content\r\n' + preference.END + '\r\n# After with no newline').encode()
        self.target.write_bytes(original)
        plan, _ = self.run_plan()
        data = self.target.read_bytes()
        self.assertTrue(data.startswith(b'# Before\r\n'))
        self.assertTrue(data.endswith(b'# After with no newline'))
        self.assertIn(b'\r\n' + preference.PREFERENCE.encode() + b'\r\n', data)
        self.assertIn('-Old content', plan['diff'])
        self.assertNotIn('# After', plan['diff'])
        self.run_plan('remove')
        self.assertEqual(self.target.read_bytes(), b'# Before\r\n# After with no newline')

    def test_duplicate_partial_nested_or_inline_markers_are_not_repaired(self):
        block = preference.START + '\nold\n' + preference.END + '\n'
        for text in [block * 2, preference.START, preference.END, preference.END + '\n' + preference.START,
                     preference.START + '\n' + block + preference.END, 'inline ' + block, preference.FAMILY + 'start\n']:
            self.target.write_text(text)
            with self.subTest(text=text), self.assertRaises(preference.PreferenceError):
                preference.preview(self.target, 'project', 'enable')
            self.assertEqual(self.target.read_text(), text)

    def test_stale_source_and_edited_plans_cannot_use_original_approval(self):
        self.target.write_text('Original')
        plan = preference.preview(self.target, 'project', 'enable')
        for key, value in [('scope', 'user'), ('target', str(self.root / 'CLAUDE.md')), ('diff', 'hide the edit'), ('after_sha256', 'sha256:' + '0' * 64)]:
            changed = copy.deepcopy(plan)
            changed[key] = value
            changed['plan_sha256'] = preference.plan_digest(changed)
            with self.subTest(key=key), self.assertRaises(preference.PreferenceError):
                preference.apply(changed, plan['plan_sha256'])
            # Even an approval input recomputed from a fabricated diff does not
            # bypass independent transformation from the live target bytes.
            if key in ('diff', 'after_sha256'):
                with self.assertRaises(preference.PreferenceError):
                    preference.apply(changed, changed['plan_sha256'])
        self.target.write_text('Concurrent user edit')
        with self.assertRaises(preference.PreferenceError):
            preference.apply(plan, plan['plan_sha256'])
        self.assertEqual(self.target.read_text(), 'Concurrent user edit')
        self.assertFalse((self.root / 'CLAUDE.md').exists())

    def test_symlink_ancestor_target_hardlink_and_nonregular_files_fail_closed(self):
        real = self.root / 'real'
        real.mkdir()
        (real / 'AGENTS.md').write_text('Keep')
        alias = self.root / 'alias'
        alias.symlink_to(real, target_is_directory=True)
        self.target.symlink_to(real / 'AGENTS.md')
        for target in [self.target, alias / 'AGENTS.md', real]:
            with self.assertRaises(preference.PreferenceError):
                preference.preview(target, 'project', 'enable')
        hardlink = self.root / 'hard.md'
        os.link(real / 'AGENTS.md', hardlink)
        with self.assertRaises(preference.PreferenceError):
            preference.preview(hardlink, 'project', 'enable')
        self.assertEqual((real / 'AGENTS.md').read_text(), 'Keep')

    def test_readonly_target_and_change_immediately_before_publication_preserve_file(self):
        self.target.write_text('Keep')
        os.chmod(self.target, 0o400)
        plan = preference.preview(self.target, 'project', 'enable')
        with self.assertRaises(preference.PreferenceError):
            preference.apply(plan, plan['plan_sha256'])
        self.assertEqual(self.target.read_text(), 'Keep')
        os.chmod(self.target, 0o600)
        plan = preference.preview(self.target, 'project', 'enable')
        original_fsync = preference.os.fsync
        def race(fd):
            original_fsync(fd)
            self.target.write_text('New user content')
        with patch.object(preference.os, 'fsync', side_effect=race), self.assertRaises(preference.PreferenceError):
            preference.apply(plan, plan['plan_sha256'])
        self.assertEqual(self.target.read_text(), 'New user content')
        self.assertFalse(list(self.root.glob('.as-preference-*')))

    def test_proposed_size_is_checked_before_writing_and_exact_bound_remains_reversible(self):
        self.target.write_bytes(b'x' * preference.MAX_BYTES)
        with self.assertRaisesRegex(preference.PreferenceError, 'proposed instruction file exceeds'):
            preference.preview(self.target, 'project', 'enable')
        self.assertEqual(self.target.stat().st_size, preference.MAX_BYTES)
        self.assertEqual(self.target.read_bytes(), b'x' * preference.MAX_BYTES)
        original = b'x' * (preference.MAX_BYTES - len(preference.transform(b'', 'enable')))
        self.target.write_bytes(original)
        self.run_plan()
        self.assertEqual(self.target.stat().st_size, preference.MAX_BYTES)
        self.run_plan('remove')
        self.assertEqual(self.target.read_bytes(), original)

    def test_parent_namespace_swap_before_final_check_changes_neither_target(self):
        current = self.root / 'current'
        current.mkdir()
        moved = self.root / 'moved'
        target = current / 'AGENTS.md'
        target.write_text('Approved original')
        plan = preference.preview(target, 'project', 'enable')
        original_fsync = preference.os.fsync
        def race(fd):
            original_fsync(fd)
            current.rename(moved)
            current.mkdir()
            (current / 'AGENTS.md').write_text('Unrelated replacement')
        with patch.object(preference.os, 'fsync', side_effect=race), self.assertRaisesRegex(preference.PreferenceError, 'parent namespace changed'):
            preference.apply(plan, plan['plan_sha256'])
        self.assertEqual((moved / 'AGENTS.md').read_text(), 'Approved original')
        self.assertEqual(target.read_text(), 'Unrelated replacement')
        self.assertFalse(list(moved.glob('.as-preference-*')))
        self.assertFalse(list(current.glob('.as-preference-*')))

    def test_cli_saved_plan_and_external_digest_bind_actual_edit(self):
        script = ROOT / 'tools/transformers/assistant_preference.py'
        command = [sys.executable, str(script)]
        result = subprocess.run(command + ['preview', '--target', str(self.target), '--scope', 'project', '--action', 'enable'], capture_output=True, text=True, check=True)
        plan = json.loads(result.stdout)
        plan_file = self.root / 'plan.json'
        plan_file.write_text(result.stdout)
        applied = subprocess.run(command + ['apply', '--plan', str(plan_file), '--approval-digest', plan['plan_sha256']], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(applied.stdout)['status'], 'preference-bytes-updated')
        self.assertIn(preference.PREFERENCE, self.target.read_text())


if __name__ == '__main__':
    unittest.main()
