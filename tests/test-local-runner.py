"""Local engineering fixtures; these do not establish actual host/OS acceptance."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import subprocess
import asyncio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/runner'))
from package import seal, verify
from run import execute, registry
from lint import check


def module(path):
    spec = importlib.util.spec_from_file_location('fixture_' + Path(path).stem, ROOT / path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


class Runner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='Arch Studio runner é ')
        cls.root = Path(cls.tmp.name).resolve()
        cls.package = cls.root / 'package'
        shutil.copytree(ROOT, cls.package, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__', '.DS_Store', 'node_modules'))
        cls.manifest = seal(cls.package, 'a' * 40)
        (cls.package / 'as-package.json').write_text(json.dumps(cls.manifest))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def call(self, operation, value):
        return execute({'schema_version': 1, 'operation': operation,
                        'release_digest': self.manifest['release_digest'], 'input': value}, self.package / 'as-package.json')

    def test_fixtures_cover_current_registry(self):
        self.assertEqual(check(ROOT)['operations'], len(registry(ROOT)))

    def test_structured_pure_operation_and_repeat(self):
        value = {'data': {'raw': '24 inches wide', 'axes': {'W': 24}, 'unit': 'in', 'meaning': 'overall'}, 'unit': 'mm'}
        first = self.call('dimension_values.normalize', value)
        self.assertEqual(first['status'], 'ok', first)
        self.assertEqual(first['result']['axes'], {'W': 609.6})
        self.assertEqual(first, self.call('dimension_values.normalize', value))
        self.assertFalse(first['workflow_completed'])

    def test_accepted_membership_eleven_not_ten_and_other_sizes(self):
        for size in (3, 11):
            expected = [str(i) for i in range(size)]
            entries = [{'item': item, 'status': 'verified', 'artifact': item + '.pdf', 'sha256': 'a' * 64} for item in expected]
            self.assertTrue(self.call('delivery_coverage.assess', {'data': {'expected': expected, 'entries': entries}})['result']['complete'])
            missing = self.call('delivery_coverage.assess', {'data': {'expected': expected, 'entries': entries[:-1]}})['result']
            self.assertEqual(missing['missing'], [expected[-1]])
            self.assertFalse(missing['complete'])
            self.assertFalse(missing['evidence_verified'])

    def test_unknown_and_extra_fields_fail(self):
        self.assertEqual(self.call('shell.execute', {})['error']['code'], 'unknown_operation')
        self.assertEqual(self.call('dimension_values.normalize', {'data': {}, 'command': 'anything'})['status'], 'error')

    def test_large_desktop_request_and_child_timeout_are_bounded_errors(self):
        self.assertEqual(self.call('dimension_values.normalize', {'data': 'x' * (5 * 1024 * 1024)})['error']['code'], 'invalid_request')
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('fixture', 120)):
            result = self.call('dimension_values.normalize', {'data': {}})
        self.assertEqual(result['status'], 'error')

    def test_official_sdk_stdio_adapter_uses_same_package_and_operation(self):
        from mcp import Client, StdioServerParameters
        async def exercise():
            connection = StdioServerParameters(command=sys.executable, args=[str(self.package / 'tools/runner/desktop.py'), '--package-manifest', str(self.package / 'as-package.json')])
            async with Client(connection) as client:
                result = await client.call_tool('as_execute_operation', {'request': {
                    'schema_version': 1, 'operation': 'dimension_values.normalize',
                    'release_digest': self.manifest['release_digest'],
                    'input': {'data': {'raw': '1 inch', 'axes': {'W': 1}, 'unit': 'in', 'meaning': 'overall'}, 'unit': 'mm'}}})
                content = result.structured_content
                self.assertEqual(content['status'], 'ok', content)
                self.assertEqual(content['result']['axes']['W'], 25.4)
                self.assertFalse(content['workflow_completed'])
        asyncio.run(exercise())

    def test_altered_or_missing_support_fails_before_writes(self):
        path = self.package / 'tools/transformers/product_identity.py'
        original = path.read_bytes()
        destination = self.root / 'never-written'
        for mutation in ('alter', 'remove'):
            try:
                if mutation == 'alter': path.write_bytes(original + b'\n# altered\n')
                else: path.unlink()
                result = self.call('update_preference.enable', {'state_directory': str(destination)})
                self.assertEqual(result['error']['code'], 'package_mismatch')
                self.assertFalse(destination.exists())
            finally:
                path.write_bytes(original)

    def test_missing_managed_dependency_fails_before_resize(self):
        destination = self.root / 'no-images'
        with patch('run.importlib.metadata.version', return_value='wrong'):
            result = self.call('resize_images.resize', {'folder': str(destination), 'modes': ['web']})
        self.assertEqual(result['error']['code'], 'installation_required')
        self.assertFalse(destination.exists())

    def test_current_write_repeat_and_nonascii_space_path(self):
        destination = self.root / 'Préférences with spaces'
        result = self.call('update_preference.enable', {'state_directory': str(destination)})
        self.assertEqual(result['status'], 'ok', result)
        self.assertEqual(result, self.call('update_preference.enable', {'state_directory': str(destination)}))
        self.assertEqual(len(list(destination.iterdir())), 1)
        self.assertTrue(self.call('update_preference.status', {'state_directory': str(destination)})['result']['enabled'])
        self.assertFalse(self.call('update_preference.disable', {'state_directory': str(destination)})['result']['enabled'])

    def test_portable_scaffold_validation_from_package(self):
        directory = self.root / 'synthetic-skill'; directory.mkdir()
        (directory / 'SKILL.md').write_text('---\nname: synthetic-skill\ndescription: Validate a synthetic fixture\n---\nProcedure\n')
        (directory / 'README.md').write_text('# Synthetic skill\n')
        result = self.call('skill_scaffold.validate', {'directory': str(directory)})
        self.assertEqual(result['status'], 'ok', result)
        self.assertTrue(result['result']['valid'])
        (directory / 'README.md').unlink()
        self.assertEqual(self.call('skill_scaffold.validate', {'directory': str(directory)})['status'], 'error')

    def test_document_owner_modules_run_from_same_verified_package(self):
        project = self.root / 'New project é'
        result = self.call('project.init', {'target': str(project), 'name': 'Synthetic', 'project_id': 'P1',
                           'kind': 'initiative', 'type': 'internal', 'status': 'active', 'client_code': 'INT',
                           'client': 'Internal', 'vocabularies': {'phases': ['main'], 'scopes': ['operations'],
                           'originators': ['firm']}, 'dry_run': False})
        self.assertEqual(result['status'], 'ok', result)
        source = self.root / 'synthetic drawing.pdf'; source.write_bytes(b'%PDF-synthetic')
        data = {'project_root': str(project), 'source_path': str(source), 'kind': 'drawing',
                'coordinates': {'phase': 'main', 'stage': '0-plan', 'scope': 'operations',
                                'originator': 'firm', 'date': '2026-09-13'}, 'dry_run': False}
        registered = self.call('documents.register', data)
        self.assertEqual(registered['status'], 'ok', registered)
        self.assertEqual(self.call('documents.query', {'project_root': str(project)})['result']['count'], 1)
        task = self.call('tasks.add', {'project_root': str(project), 'dry_run': False,
                        'task': {'description': 'Inspect synthetic candidate', 'source': 'conversation:2026-09-13#instruction-1'}})
        self.assertEqual(task['status'], 'ok', task)

    def test_resize_collisions_fail_before_output_and_valid_batch_reports_each(self):
        from PIL import Image
        images = self.root / 'images'; images.mkdir(exist_ok=True)
        for name in ('same.jpg', 'same.png'):
            Image.new('RGB', (8, 8)).save(images / name)
        result = self.call('resize_images.resize', {'folder': str(images), 'modes': ['web']})
        self.assertEqual(result['status'], 'error')
        self.assertFalse((images / 'resized-web').exists())
        (images / 'same.png').unlink()
        result = self.call('resize_images.resize', {'folder': str(images), 'modes': ['web']})
        self.assertEqual(result['status'], 'ok', result)
        self.assertEqual(result['result']['succeeded'], 1)
        hashes = {p.name: p.read_bytes() for p in (images / 'resized-web').iterdir()}
        self.assertEqual(self.call('resize_images.resize', {'folder': str(images), 'modes': ['web']})['status'], 'error')
        self.assertEqual(hashes, {p.name: p.read_bytes() for p in (images / 'resized-web').iterdir()})

    def test_quantity_two_linked_to_quantity_one_revision_rejected(self):
        helper = module('tools/transformers/delivery_coverage.py')
        artifact = self.root / 'Q-1.pdf'; artifact.write_bytes(b'%PDF-synthetic quantity 1')
        receipt = self.root / 'old-receipt.json'
        data = {'mechanical_status': 'passed', 'source_sha256': 'a' * 64, 'template_sha256': 'b' * 64,
                'outputs': [{'tag': 'Q-1', 'items': [{'item_id': 'selected', 'revision': 1}]}],
                'verified_artifacts': [{'file': 'Q-1.pdf', 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}]}
        receipt.write_text(json.dumps(data))
        expected = [{'item': 'selected', 'revision': 2, 'source_sha256': 'a' * 64, 'template_sha256': 'b' * 64,
                     'artifact': str(artifact), 'receipt': str(receipt)}]
        self.assertFalse(helper.verify_links(expected)['complete'])
        expected[0]['revision'] = 1
        self.assertTrue(self.call('delivery_coverage.verify-links', {'expected': expected})['result']['complete'])
        artifact.write_bytes(b'changed bytes')
        self.assertFalse(helper.verify_links(expected)['complete'])


class Workbook(unittest.TestCase):
    def test_allowed_values_preserve_formula_link_image_and_cache(self):
        helper = module('tools/validators/workbook_preservation.py')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            worksheet = '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1"><v>1</v></c><c r="B1"><f>A1*2</f><v>2</v></c><c r="C1" t="inlineStr"><is><t xml:space="preserve">  label  </t></is></c></row></sheetData></worksheet>'
            parts = {'[Content_Types].xml': b'<Types/>', 'xl/workbook.xml': b'<workbook/>',
                     'xl/worksheets/sheet1.xml': worksheet.encode(), 'xl/media/image1.png': b'original image',
                     'xl/worksheets/_rels/sheet1.xml.rels': b'original relationship'}
            def write(path, entries):
                with zipfile.ZipFile(path, 'w') as archive:
                    for name, value in entries.items(): archive.writestr(name, value)
            before = root / 'before.xlsx'; after = root / 'after.xlsx'; write(before, parts)
            allowed = [{'part': 'xl/worksheets/sheet1.xml', 'cell': 'A1', 'aspects': ['value']}]
            good = {**parts, 'xl/worksheets/sheet1.xml': worksheet.replace('<v>1</v>', '<v>3</v>').encode()}
            write(after, good)
            self.assertTrue(helper.compare(before, after, allowed)['preserved'])
            for part, value in [('xl/media/image1.png', b'changed image'),
                                ('xl/worksheets/_rels/sheet1.xml.rels', b'changed link'),
                                ('xl/worksheets/sheet1.xml', worksheet.replace('A1*2', 'A1*3').encode()),
                                ('xl/worksheets/sheet1.xml', worksheet.replace('<v>2</v>', '<v>99</v>').encode()),
                                ('xl/worksheets/sheet1.xml', worksheet.replace('  label  ', 'label').encode()),
                                ('xl/worksheets/sheet1.xml', worksheet.replace('</t>', '</t>changed-tail').encode())]:
                with self.subTest(part=part, value=value):
                    write(after, {**good, part: value})
                    self.assertFalse(helper.compare(before, after, allowed)['preserved'])


if __name__ == '__main__':
    unittest.main()
