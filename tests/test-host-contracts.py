"""Declarative capability/receipt checks; no host or provider operations are performed."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('host_contracts', ROOT / 'tools/validators/host_contracts.py')
host = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(host)


class Contracts(unittest.TestCase):
    def setUp(self):
        self.document = host.load(ROOT)

    def test_inventory(self):
        host.validate(self.document, ROOT)

    def test_on_disk_index_matches_schema(self):
        schema = json.loads((ROOT / 'schema/host-contracts.schema.json').read_text())
        index = json.loads((ROOT / 'corpus/host-contracts.json').read_text())
        host.schema_check(index, schema, schema)

    def test_delegating_skill_preserves_authority(self):
        self.document['components']['skill:project']['delegation'] = 'not-applicable'
        with self.assertRaises(ValueError):
            host.validate(self.document, ROOT)

    def test_nonowner_cannot_declare_record_write(self):
        self.document['components']['skill:master-schedule']['owned_records'] = []
        with self.assertRaises(ValueError):
            host.validate(self.document, ROOT)

    def test_profile_cannot_masquerade_as_another_mode(self):
        self.document['profiles']['answer']['mode'] = 'research'
        with self.assertRaises(ValueError):
            host.validate(self.document, ROOT)

    def test_unknown_capability_and_policy_escape(self):
        for change in ('capability', 'policy'):
            document = copy.deepcopy(self.document)
            if change == 'capability':
                document['profiles']['answer']['required'] = ['gmail-implies-sheets']
            else:
                document['policy'] = '../outside.md'
            with self.assertRaises(ValueError):
                host.validate(document, ROOT)

    def test_missing_component(self):
        self.document['components'].pop('skill:architecture-knowledge')
        with self.assertRaises(ValueError):
            host.validate(self.document, ROOT)

    def test_unknown_mode_and_permission(self):
        for key, value in [('mode', 'magic'), ('permission', 'implicit-admin')]:
            document = copy.deepcopy(self.document)
            document['components']['skill:master-schedule']['modes'][0][key] = value
            with self.assertRaises(ValueError):
                host.validate(document, ROOT)

    def test_knowledge_does_not_require_workspace(self):
        mode = host.select(self.document, 'skill:architecture-knowledge', 'answer')
        self.assertEqual(mode['required'], [])

    def test_native_render_requires_actual_readback_without_mandatory_process(self):
        for name in ('product-cut-sheet', 'spec-book'):
            mode = host.select(self.document, 'skill:' + name, 'render')
            self.assertTrue({'file.read', 'file.write', 'document.render', 'document.inspect'} <= set(mode['required']))
            self.assertNotIn('process.run', mode['required'])
            self.assertIn('process.run', mode['optional'])
        # Native scaffold validation uses available host parsing/file tools.
        mode = host.select(self.document, 'skill:skill-maker', 'file-output')
        self.assertTrue({'file.read', 'file.write'} <= set(mode['required']))
        self.assertNotIn('process.run', mode['required'])
        self.assertIn('process.run', mode['optional'])

    def test_url_and_pdf_parsers_declare_conditional_workbook_modes(self):
        for name in ['product-spec-bulk-fetch', 'product-spec-pdf-parser']:
            for mode in ['workbook-read', 'workbook-edit']:
                self.assertIn('spreadsheet.read', host.select(self.document, 'skill:' + name, mode)['required'])

    def evidence(self):
        return {'target': 'sheets:isolated/Appliances/A1:R14',
                'destination_kind': 'provider',
                'capabilities': ['spreadsheet.read', 'spreadsheet.edit', 'spreadsheet.features', 'spreadsheet.backup'],
                'access_target': 'sheets:isolated/Appliances/A1:R14', 'access_checked': True,
                'authorized': True, 'preserved': True, 'conflicts_resolved': True,
                'readback': {'kind': 'provider', 'target': 'sheets:isolated/Appliances/A1:R14', 'fresh': True}}

    def test_gmail_is_not_sheets(self):
        evidence = self.evidence()
        evidence['capabilities'] = ['email.read']
        self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'blocked')

    def test_read_only_cannot_edit(self):
        evidence = self.evidence()
        evidence['capabilities'].remove('spreadsheet.edit')
        self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'blocked')

    def test_edit_requires_provider_readback(self):
        for kind in ['local-export', None]:
            evidence = self.evidence()
            evidence['readback']['kind'] = kind
            self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'unverified')

    def test_https_sheets_is_still_provider(self):
        evidence = self.evidence()
        target = 'https://docs.google.com/spreadsheets/d/isolated/edit#gid=0'
        evidence.update(target=target, access_target=target)
        evidence['readback'].update(target=target, kind='local-export')
        self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'unverified')
        evidence.pop('destination_kind')
        self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'blocked')

    def test_native_workbook_requires_native_readback(self):
        evidence = self.evidence()
        target = '/isolated/accepted-appliance-schedule.xlsx'
        evidence.update(target=target, access_target=target)
        evidence['readback']['target'] = target
        evidence['destination_kind'] = 'local'
        evidence['readback']['kind'] = 'provider'
        self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'unverified')
        evidence['readback']['kind'] = 'native'
        self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'evidence-conforms')

    def test_provider_target_cannot_be_labeled_local(self):
        for target in ['sheets:isolated/Appliances/A1:R14', 'https://docs.google.com/spreadsheets/d/isolated/edit#gid=0']:
            with self.subTest(target=target):
                evidence = self.evidence()
                evidence.update(target=target, access_target=target, destination_kind='local')
                evidence['readback'].update(target=target, kind='native')
                self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'blocked')

    def test_write_modes_cannot_downgrade_effect_or_permission(self):
        cases = [('skill:master-schedule', 'workbook-edit'), ('skill:project', 'record-write'),
                 ('skill:csv-to-sif', 'file-output'), ('skill:spec-book', 'render'),
                 ('skill:resize-images', 'image-transform'), ('skill:studio-feedback', 'external-open')]
        for component, mode in cases:
            for patch in [{'effects': []}, {'effects': ['none']}, {'permission': 'read-within-scope'},
                          {'effects': [], 'permission': 'read-within-scope'}]:
                with self.subTest(component=component, patch=patch):
                    document = copy.deepcopy(self.document)
                    selection = next(m for m in document['components'][component]['modes'] if m['mode'] == mode)
                    selection.update(patch)
                    with self.assertRaises(ValueError):
                        host.validate(document, ROOT)

    def test_native_record_modes_use_file_capabilities_without_mandatory_process(self):
        for component, declaration in self.document['components'].items():
            if declaration.get('execution', {}).get('model') != 'harness-native':
                continue
            for mode in declaration['modes']:
                if mode['mode'] not in ('record-read', 'record-write'):
                    continue
                with self.subTest(component=component, mode=mode['mode']):
                    selected = host.select(self.document, component, mode['mode'])
                    self.assertIn('file.read', selected['required'])
                    self.assertNotIn('process.run', selected['required'])
                    if mode['mode'] == 'record-write':
                        self.assertIn('file.write', selected['required'])

    def test_unconverted_workflow_retains_its_own_declared_requirements(self):
        # Keep this legacy-declaration boundary stable as real workflows migrate.
        document = copy.deepcopy(self.document)
        declaration = document['components']['skill:epd-parser']
        declaration.pop('execution', None)
        mode = next(m for m in declaration['modes'] if m['mode'] == 'record-write')
        mode.update(required=['file.read', 'file.write', 'process.run'], optional=[])
        self.assertIn('process.run', host.select(document, 'skill:epd-parser', 'record-write')['required'])

    def test_native_output_cannot_declare_write_without_actual_readback(self):
        for component, declaration in self.document['components'].items():
            if declaration.get('execution', {}).get('model') != 'harness-native':
                continue
            for selected in declaration['modes']:
                if selected['mode'] != 'file-output':
                    continue
                with self.subTest(component=component):
                    mode = host.select(self.document, component, 'file-output')
                    self.assertTrue({'file.read', 'file.write'} <= set(mode['required']))
                    for required in (['file.write'], ['file.read'], []):
                        invalid = copy.deepcopy(self.document)
                        output = next(m for m in invalid['components'][component]['modes'] if m['mode'] == 'file-output')
                        output.update(required=required, optional=[])
                        message = 'native file output requires' if required == ['file.write'] else 'Unsafe mutation declaration'
                        with self.assertRaisesRegex(ValueError, message):
                            host.validate(invalid, ROOT)
        # This change applies to declared native workflows, not the legacy shared profile.
        self.assertEqual(self.document['profiles']['file-output']['required'], ['file.write'])

    def test_native_execution_requires_an_existing_nonexecutable_contract(self):
        native = {'model': 'harness-native', 'contract': 'docs/workspace-model.md',
                  'operations': ['context.resolve', 'tasks.update']}
        self.document['components']['skill:tasklist']['execution'] = native
        host.validate(self.document, ROOT)
        for path in ['../outside.md', '/tmp/contract.md', 'docs/missing.md',
                     'skills/receive/scripts/records.py', 'docs\\workspace-model.md']:
            with self.subTest(path=path):
                invalid = copy.deepcopy(self.document)
                invalid['components']['skill:tasklist']['execution']['contract'] = path
                with self.assertRaises(ValueError):
                    host.validate(invalid, ROOT)

    def test_native_task_reads_and_writes_do_not_require_a_process(self):
        for mode, required in [('record-read', {'file.read'}),
                               ('record-write', {'file.read', 'file.write'})]:
            selection = host.select(self.document, 'skill:tasklist', mode)
            self.assertEqual(set(selection['required']), required)
            self.assertIn('process.run', selection['optional'])
        evidence = {'target': '/synthetic/project/TASKS.csv', 'access_target': '/synthetic/project/TASKS.csv',
                    'access_checked': True, 'capabilities': ['file.read', 'file.write'],
                    'authorized': True, 'preserved': True, 'conflicts_resolved': True,
                    'readback': {'target': '/synthetic/project/TASKS.csv', 'fresh': True}}
        result = host.assess(self.document, 'skill:tasklist', 'record-write', evidence)
        self.assertEqual(result['status'], 'evidence-conforms')
        self.assertFalse(result['execution_verified'])

    def test_native_declaration_is_not_an_execution_binding(self):
        native = {'model': 'harness-native', 'contract': 'docs/workspace-model.md',
                  'operations': ['tasks.update']}
        for patch in [{'model': 'local-runner'}, {'operations': []},
                      {'operations': ['tasks.update', 'tasks.update']},
                      {'operations': ['python run.py']}, {'handler': 'dispatch'}]:
            with self.subTest(patch=patch):
                document = copy.deepcopy(self.document)
                document['components']['skill:tasklist']['execution'] = dict(native, **patch)
                with self.assertRaises(ValueError):
                    host.validate(document, ROOT)

    def test_native_procedure_can_omit_registered_operations_without_record_authority(self):
        native = {'model': 'harness-native', 'contract': 'skills/tool-catalog/SKILL.md', 'operations': []}
        self.document['components']['skill:tool-catalog']['execution'] = native
        host.validate(self.document, ROOT)
        for mode in ('record-read', 'record-write'):
            document = copy.deepcopy(self.document)
            document['components']['skill:tool-catalog']['modes'].append({'mode': mode})
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'record modes require'):
                host.validate(document, ROOT)

    def test_valid_evidence_is_not_execution_proof(self):
        result = host.assess(self.document, 'skill:master-schedule', 'workbook-edit', self.evidence())
        self.assertEqual(result['status'], 'evidence-conforms')
        self.assertFalse(result['execution_verified'])

    def test_wrong_target_denied_or_conflicting(self):
        for key, value in [('access_target', 'sheets:wrong'), ('access_checked', False), ('authorized', False), ('preserved', False), ('conflicts_resolved', False)]:
            evidence = self.evidence()
            evidence[key] = value
            self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'blocked')

    def test_wrong_or_stale_readback(self):
        for key, value in [('target', 'sheets:wrong'), ('fresh', False)]:
            evidence = self.evidence()
            evidence['readback'][key] = value
            self.assertEqual(host.assess(self.document, 'skill:master-schedule', 'workbook-edit', evidence)['status'], 'unverified')


if __name__ == '__main__':
    unittest.main()
