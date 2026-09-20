"""Check completion guidance and required package closure, not user-workflow success."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion_capabilities', ROOT / 'tools/validators/capabilities.py')
capabilities = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capabilities)


class CompletionReporting(unittest.TestCase):
    def test_shared_reference_distinguishes_evidence_and_completion(self):
        text = (ROOT / 'docs/completion-reporting.md').read_text()
        for phrase in ('Source data', 'Arch Studio instructions', 'Host operations', 'Outputs',
                       'Validation', 'Unresolved items', 'Canonical writes', 'Full completion',
                       'Partial or blocked', 'Instructions delivered', 'Use Norma',
                       '2 of 3', 'write outcome is unknown', 'machine-contract fields'):
            self.assertIn(phrase, text)
        for file in ('docs/host-harness-contract.md', 'docs/host-adapters.md', 'skills/norma/SKILL.md', 'skills/studio/SKILL.md'):
            self.assertIn('completion-reporting.md', (ROOT / file).read_text())

    def test_every_declared_critical_capability_requires_the_same_reference(self):
        definitions = capabilities.definitions(ROOT)
        components = json.loads((ROOT / 'corpus/components.json').read_text())['components']
        self.assertEqual({row['id'] for row in definitions},
                         {row['id'] for row in components if row.get('capability')})
        for row in definitions:
            with self.subTest(component=row['id']):
                self.assertIn('docs/completion-reporting.md', row['references'])
                self.assertNotIn('docs/completion-reporting.md', [r['path'] for r in row.get('conditionalReferences', [])])
        capabilities.generate(ROOT)

    def test_missing_or_undeclared_reporting_resource_fails_package_validation(self):
        with tempfile.TemporaryDirectory(prefix='as-completion-') as tmp:
            root = Path(tmp) / 'package'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '__pycache__', '.DS_Store'))
            registry = root / 'corpus/components.json'
            original = registry.read_text()
            document = json.loads(original)
            row = next(r for r in document['components'] if r['id'] == 'skill:spec-book')
            row['capability']['references'].remove('docs/completion-reporting.md')
            registry.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, 'required host references'):
                capabilities.definitions(root)
            registry.write_text(original)
            (root / 'docs/completion-reporting.md').unlink()
            with self.assertRaises(ValueError):
                capabilities.definitions(root)


if __name__ == '__main__':
    unittest.main()
