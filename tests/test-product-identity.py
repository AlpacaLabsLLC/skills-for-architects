"""Synthetic FF&E identity, source diagnostic and filename mapping contracts."""
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/transformers'))
from product_identity import validate_tag, output_names, tag_match
from ffe_intake import manifest


class ProductIdentity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='as-identity-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'source.txt').write_text('Sanitized evidence')
        self.base = dict(schema_version=1, mode='one-off', job_id='identity-test',
                         sources=[dict(id='source', kind='file', reference='source.txt', sha256=None, status='available')],
                         selected_tags=['SX.A-001'], template=None, record_basis=None,
                         supersedes=None, actor='Synthetic tester', reason='Explicit one-off test')

    def test_all_26_sanitized_dotted_tags_roundtrip_intake(self):
        tags = [f'SX.{"A" if i % 2 else "B"}-{i:03}' for i in range(1, 27)]
        self.base['selected_tags'] = tags
        receipt = manifest(self.root, self.base, standalone=True)
        accepted = json.loads((self.root / receipt['path']).read_text())
        self.assertEqual(accepted['selected_tags'], tags)
        self.assertEqual(output_names([dict(tag=tag) for tag in tags], 1), [tag + '.pdf' for tag in tags])

    def test_legacy_and_shared_maximum_lengths(self):
        for length in (1, 64, 65, 80):
            tag = 'I' * length
            validate_tag(tag, 'selected_tags[0]')
            self.assertEqual(output_names([dict(tag=tag)], 1), [tag + '.pdf'])
        for tag in ('I' * 81, '', '.hidden', '../outside', 'A/../B', 'A/B', r'A\B', 'A:B', 'A B', 'A\nB', 'Café'):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                validate_tag(tag, 'tag')
        self.base['selected_tags'] = ['AP-01', 'legacy_02', 'I' * 80]
        self.assertFalse(manifest(self.root, self.base, standalone=True)['adoption_performed'])

    def test_identity_is_not_a_job_id(self):
        self.base['job_id'] = 'job.with.dots'
        with self.assertRaisesRegex(ValueError, 'job_id'):
            manifest(self.root, self.base, standalone=True)

    def test_public_schema_pattern_uses_absolute_end_not_line_end(self):
        schema = json.loads((ROOT / 'schema/product-identity.schema.json').read_text())
        # JSON Schema patterns search rather than fullmatch; a trailing newline is still invalid.
        for kind, value in (('tag', 'SAFE\n'), ('filename', 'SAFE.pdf\n')):
            self.assertIsNone(re.search(schema['$defs'][kind]['pattern'], value))
        self.assertIsNotNone(re.search(schema['$defs']['tag']['pattern'], 'SX.A-001'))

    def test_explicit_reversible_mapping_and_case_collisions(self):
        groups = [dict(tag='CON', filename='console-fixture.pdf'), dict(tag='A.', filename='A-dot.pdf'),
                  dict(tag='TAG-A'), dict(tag='tag-a', filename='lowercase-tag-a.pdf')]
        names = output_names(groups, 2)
        self.assertEqual(dict(zip(names, [row['tag'] for row in groups]))['console-fixture.pdf'], 'CON')
        self.assertEqual(names, ['console-fixture.pdf', 'A-dot.pdf', 'TAG-A.pdf', 'lowercase-tag-a.pdf'])
        for bad in ([dict(tag='A'), dict(tag='A', filename='other.pdf')],
                    [dict(tag='A'), dict(tag='a')],
                    [dict(tag='A'), dict(tag='B', filename='a.pdf')],
                    [dict(tag='A', filename='combined.pdf')]):
            with self.assertRaises(ValueError):
                output_names(bad, 2)

    def test_unsafe_names_fail_until_explicit_mapping(self):
        for tag in ('CON', 'con.any', 'NUL', 'COM1', 'LPT9', 'A.', 'combined'):
            validate_tag(tag, 'tag')
            with self.assertRaisesRegex(ValueError, 'filename'):
                output_names([dict(tag=tag)], 2)
            self.assertEqual(output_names([dict(tag=tag, filename='resolved.pdf')], 2), ['resolved.pdf'])
        for name in ('../outside.pdf', '/outside.pdf', r'A\B.pdf', 'A/B.pdf', 'A:1.pdf', 'CON.pdf',
                     'A..pdf', 'A.PDF', 'combined.pdf', 'I' * 81 + '.pdf'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                output_names([dict(tag='A', filename=name)], 2)

    def test_only_version_one_can_use_legacy_manifest_fallback(self):
        self.assertEqual(output_names([dict(tag='OLD-MAPPED')], 1, prepared=True), ['OLD-MAPPED.pdf'])
        with self.assertRaisesRegex(ValueError, 'filename'):
            output_names([dict(tag='A')], 2, prepared=True)
        with self.assertRaisesRegex(ValueError, 'schema_version'):
            output_names([dict(tag='A')], True)
        with self.assertRaisesRegex(ValueError, 'filename'):
            output_names([dict(tag='A', filename='mapped.pdf')], 1)

    def test_exact_pdf_tag_tokens_not_filename_or_variants(self):
        for content in ('SX.A-001', 'Tag: SX.A-001 | Fixture', '(SX.A-001)'):
            self.assertIsNotNone(tag_match('SX.A-001', content))
        for content in ('SX.A-001.pdf', 'SX.A-001a', 'SX.A-001-wide', 'OTHER-SX.A-001', 'SX-A-001'):
            self.assertIsNone(tag_match('SX.A-001', content))

    def test_indexed_identity_errors_and_no_partial_writes(self):
        for tags, match in ((['GOOD', 'bad/tag'], r'selected_tags\[1\]'),
                            (['GOOD', 'GOOD'], r'selected_tags\[1\].*duplicate')):
            self.base['selected_tags'] = tags
            with self.assertRaisesRegex(ValueError, match):
                manifest(self.root, self.base, standalone=True)
            self.assertFalse((self.root / 'ffe').exists())

    def test_missing_null_invalid_hash_diagnostics(self):
        for change, pattern in ((lambda row: row.pop('sha256'), r'sources\[0\].*sha256.*required'),
                                (lambda row: row.update(sha256='invalid'), r'sources\[0\]\.sha256.*64'),
                                (lambda row: row.update(sha256='0' * 64), r'sources\[0\]\.sha256.*mismatch')):
            candidate = copy.deepcopy(self.base); change(candidate['sources'][0])
            with self.assertRaisesRegex(ValueError, pattern):
                manifest(self.root, candidate, standalone=True)
            self.assertFalse((self.root / 'ffe').exists())
        receipt = manifest(self.root, self.base, standalone=True)
        accepted = json.loads((self.root / receipt['path']).read_text())
        self.assertEqual(len(accepted['sources'][0]['sha256']), 64)
        url = copy.deepcopy(self.base); url['job_id'] = 'url'
        url['sources'][0].update(kind='url', reference='https://example.test/fixture')
        with self.assertRaisesRegex(ValueError, r'sources\[0\]\.sha256.*captured'):
            manifest(self.root, url, standalone=True)
        url['sources'][0]['status'] = 'unavailable'
        receipt = manifest(self.root, url, standalone=True)
        self.assertIsNone(json.loads((self.root / receipt['path']).read_text())['sources'][0]['sha256'])


if __name__ == '__main__':
    unittest.main()
