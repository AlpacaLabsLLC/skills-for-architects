"""Generated discovery metadata has one authority and remains portable outside a checkout."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('capabilities', ROOT / 'tools/validators/capabilities.py')
capabilities = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capabilities)


class Capabilities(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='as-capabilities-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'package'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', '.DS_Store'))

    def registry(self):
        return json.loads((self.root / 'corpus/components.json').read_text())

    def save(self, document):
        (self.root / 'corpus/components.json').write_text(json.dumps(document))

    def test_generation_is_idempotent_and_does_not_replace_skill_bodies(self):
        definitions = capabilities.definitions(self.root)
        required = {'skill:lighting-report-extract', 'skill:schedule-quantity-reconcile',
                    'skill:product-data-import', 'skill:product-cut-sheet', 'skill:spec-book',
                    'skill:product-library', 'skill:product-spec-pdf-parser', 'skill:product-url-clip',
                    'skill:studio', 'skill:project', 'skill:workplan', 'skill:norma'}
        self.assertTrue(required <= {row['id'] for row in definitions})
        bodies = {row['path']: (self.root / row['path']).read_text().split('\n---\n', 1)[1] for row in definitions}
        first = capabilities.generate(self.root, write=True)
        second = capabilities.generate(self.root, write=True)
        self.assertEqual(first, second)
        capabilities.generate(self.root)
        self.assertEqual(bodies, {path: (self.root / path).read_text().split('\n---\n', 1)[1] for path in bodies})
        catalog = json.loads((self.root / 'corpus/capabilities.json').read_text())
        self.assertEqual(catalog['generated_from'], 'corpus/components.json')
        self.assertEqual(len({row['id'] for row in catalog['capabilities']}), len(definitions))
        self.assertTrue(all((self.root / row['path']).is_file() for row in catalog['capabilities']))

    def test_plugin_description_and_generated_catalog_drift_fail(self):
        for relative in ('skills/product-cut-sheet/SKILL.md', 'corpus/capabilities.json', 'docs/capabilities.md'):
            path = self.root / relative
            original = path.read_text()
            path.write_text(original.replace('description:', 'description: STALE', 1) if relative.endswith('SKILL.md') else original + '\nSTALE\n')
            with self.subTest(path=relative), self.assertRaisesRegex(ValueError, 'stale'):
                capabilities.generate(self.root)
            path.write_text(original)

    def test_definitions_reject_missing_and_ambiguous_resource_contracts(self):
        original = self.registry()
        mutations = [lambda row: row['capability']['references'].append('missing/resource.md'),
                     lambda row: row['capability']['references'].append('../outside.md'),
                     lambda row: row['capability']['references'].append(row['capability']['references'][0]),
                     lambda row: row['capability'].update(hostContract='skills/project/host-contract.json'),
                     lambda row: row['capability'].update(executionOwner='server'),
                     lambda row: row['capability']['handoffs'].append(dict(target='skill:missing', when='requested')),
                     lambda row: row['capability']['conditionalReferences'].append(dict(path=row['capability']['references'][0], when='sometimes'))]
        for mutation in mutations:
            document = copy.deepcopy(original)
            row = next(row for row in document['components'] if row['id'] == 'skill:product-cut-sheet')
            mutation(row); self.save(document)
            with self.assertRaises(ValueError):
                capabilities.definitions(self.root)

    def test_existing_dependency_and_identity_guards_are_preserved(self):
        original = self.registry()
        for mutation in (lambda rows: rows.append(copy.deepcopy(rows[0])),
                         lambda rows: rows[0]['dependencies'].append('skill:missing'),
                         lambda rows: rows[0]['dependencies'].append(rows[0]['id'])):
            document = copy.deepcopy(original); mutation(document['components']); self.save(document)
            with self.assertRaises(ValueError):
                capabilities.definitions(self.root)

    def test_source_definition_is_the_only_description_authority(self):
        document = self.registry()
        row = next(row for row in document['components'] if row['id'] == 'skill:product-cut-sheet')
        row['capability']['description'] = 'Prepare one explicitly selected specification sheet with host execution.'
        self.save(document)
        with self.assertRaisesRegex(ValueError, 'stale'):
            capabilities.generate(self.root)
        capabilities.generate(self.root, write=True)
        catalog = json.loads((self.root / 'corpus/capabilities.json').read_text())
        derived = next(item for item in catalog['capabilities'] if item['id'] == row['id'])
        self.assertEqual(derived['description'], row['capability']['description'])
        self.assertIn(json.dumps(row['capability']['description']), (self.root / row['path']).read_text())

    def test_required_and_conditional_dependencies_remain_explicit(self):
        rows = {row['id']: row for row in capabilities.definitions(self.root)}
        for key in ('skill:product-cut-sheet', 'skill:spec-book'):
            self.assertTrue({'tools/renderers/ffe-output-contract.md', 'tools/renderers/document-design-contract.md',
                             'schema/product-identity.schema.json', 'schema/ffe-output.schema.json'}
                            <= set(rows[key]['references']))
        self.assertTrue(all(row['executionOwner'] == 'host' for row in rows.values()))
        self.assertTrue(rows['skill:product-data-import']['conditionalReferences'])
        self.assertTrue({'skills/product-cut-sheet/SKILL.md', 'tools/renderers/ffe-output-contract.md',
                         'tools/transformers/evidence-contracts.md'} <= set(rows['skill:spec-book']['references']))
        self.assertTrue(set(rows['skill:product-cut-sheet']['references']) <= set(rows['skill:spec-book']['references']))
        self.assertTrue({'schema/product-observations.md', 'schema/product-observation.schema.json',
                         'tools/transformers/ffe-intake-contract.md', 'schema/product-identity.schema.json'}
                        <= set(rows['skill:product-data-import']['references']))
        conditional = {key: {ref['path']: ref['when'] for ref in row.get('conditionalReferences', [])}
                       for key, row in rows.items()}
        self.assertIn('tools/transformers/evidence-contracts.md', rows['skill:product-spec-pdf-parser']['references'])
        self.assertIn('tools/workspace/ffe-records-contract.md', conditional['skill:product-data-import'])
        for key in ('skill:product-data-import', 'skill:product-spec-pdf-parser', 'skill:product-url-clip',
                    'skill:product-data-cleanup', 'skill:product-enrich', 'skill:product-research',
                    'skill:product-spec-bulk-fetch', 'skill:product-audit',
                    'skill:product-cut-sheet', 'skill:spec-book'):
            paths = rows[key]['references'] + list(conditional[key])
            self.assertTrue({'schema/product-observations.md', 'schema/product-observation.schema.json'}
                            <= set(rows[key]['references']))
            self.assertFalse(any('/scripts/' in ref or ref.endswith('.py') for ref in paths))
            self.assertNotIn('tool:local-runner', rows[key]['dependencies'])
        self.assertIn('tools/transformers/evidence-contracts.md', rows['skill:product-data-cleanup']['references'])
        self.assertTrue({'tools/validators/ffe-audit-contract.md', 'schema/ffe-audit.schema.json'}
                        <= set(rows['skill:product-audit']['references']))
        self.assertIn('rules/professional-disclaimer.md', conditional['skill:workplan'])
        self.assertIn('docs/workspace-model.md', rows['skill:studio']['references'])
        self.assertIn('skills/project/references/context-resolution.md', rows['skill:studio']['references'])
        self.assertFalse(any('/scripts/' in ref or ref.endswith('.py') for ref in rows['skill:studio']['references']))
        self.assertNotIn('tool:local-runner', rows['skill:studio']['dependencies'])
        for row in rows.values():
            if 'tool:local-runner' in row['dependencies']:
                self.assertIn('tools/runner/operations.json', row['references'])
        self.assertNotIn('tool:local-runner', rows['skill:norma-support']['dependencies'])

    def test_export_preserves_all_native_names_and_description_values(self):
        import yaml
        registry = self.registry()
        source = {row['id']: row for row in registry['components'] if row['category'] == 'skills'}
        self.assertEqual(set(source), {'skill:' + p.parent.name for p in (self.root / 'skills').glob('*/SKILL.md')})
        names = []
        for row in source.values():
            instruction = (self.root / row['path']).read_text()
            frontmatter = yaml.safe_load(instruction.split('---\n', 2)[1])
            names.append(frontmatter['name'])
            self.assertEqual(row['id'], 'skill:' + frontmatter['name'])
            if row.get('capability'):
                self.assertEqual(frontmatter['description'], row['capability']['description'])
        self.assertEqual(len(names), len(set(names)))
        # A copied package validates without git metadata; this is export evidence,
        # not proof that a particular native host selected or registered the skills.
        capabilities.generate(self.root)


if __name__ == '__main__':
    unittest.main()
