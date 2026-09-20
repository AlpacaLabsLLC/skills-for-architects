"""Support permission/discovery invariants; not model or email acceptance."""
import importlib.util
from pathlib import Path
import unittest
import re

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('host_contracts', ROOT / 'tools/validators/host_contracts.py')
host = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host)


class SupportContract(unittest.TestCase):
    def setUp(self):
        self.contract = host.load(ROOT)

    def test_email_catalog_matches_the_canonical_skill_catalog(self):
        catalog = (ROOT / 'skills/README.md').read_text()
        expected = re.findall(r'^\| \[`/as:([^`]+)`\]\([^)]*\) \| (.*?) \|$', catalog, re.M)
        support = (ROOT / 'skills/norma-support/references/conversation-knowledge.md').read_text()
        section = support.split('## Arch Studio skill catalog snapshot\n', 1)[1]
        actual = re.findall(r'^\| ([a-z][a-z0-9-]*) \| (.*?) \|$', section, re.M)
        self.assertGreater(len(expected), 5)
        self.assertEqual(actual, expected)
        for name, _ in actual:
            self.assertTrue((ROOT / 'skills' / name / 'SKILL.md').is_file())

    def test_generic_support_needs_no_workspace_runner_or_private_account(self):
        mode = host.select(self.contract, 'skill:norma-support', 'answer')
        self.assertEqual(mode['required'], [])
        self.assertEqual(mode['effects'], ['none'])

    def test_support_cannot_own_project_or_database_records(self):
        component = self.contract['components']['skill:norma-support']
        self.assertEqual(component['owned_records'], [])
        self.assertNotIn('record-write', [mode['mode'] for mode in component['modes']])
        self.assertNotIn('workbook-edit', [mode['mode'] for mode in component['modes']])

    def test_conversational_support_has_no_execution_or_output_mode(self):
        component = self.contract['components']['skill:norma-support']
        self.assertEqual([mode['mode'] for mode in component['modes']], ['answer'])

    def test_domain_handoff_preserves_authority(self):
        component = self.contract['components']['skill:norma-support']
        self.assertEqual(component['delegation'], 'inherit-scope-target-permissions-and-evidence')
        host.validate(self.contract, ROOT)


if __name__ == '__main__':
    unittest.main()
