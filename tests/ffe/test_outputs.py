"""Synthetic contract tests; host visual attestations here are fixtures, not client proof."""
import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'tools/renderers/ffe_outputs.py'
DESIGN = ROOT / 'tools/renderers/document_contracts.py'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pdf(path, texts):
    """Small valid, text-searchable PDF fixture; no renderer dependency."""
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'', b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    page_ids = []
    for text in texts:
        page_id = len(objects) + 1
        page_ids.append(page_id)
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {page_id+1} 0 R >>'.encode())
        escaped = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        stream = f'BT /F1 12 Tf 50 740 Td ({escaped}) Tj ET'.encode()
        objects.append(f'<< /Length {len(stream)} >>\nstream\n'.encode() + stream + b'\nendstream')
    objects[1] = f'<< /Type /Pages /Count {len(texts)} /Kids [{" ".join(str(i)+" 0 R" for i in page_ids)}] >>'.encode()
    data = b'%PDF-1.4\n'
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n'
    offset = len(data)
    data += f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode()
    data += b''.join(f'{position:010d} 00000 n \n'.encode() for position in offsets[1:])
    data += f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{offset}\n%%EOF\n'.encode()
    path.write_bytes(data)


class Outputs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.snapshot = {'schema_version': 1, 'schedule_id': 'schedule-1', 'revision': 1, 'hash': 'a'*64, 'source': {'sha256': 'b'*64}, 'items': [{'item_id': f'item-{n}', 'revision': 1, 'tag': f'AP-{n:02}', 'fields': {'Product': f'Appliance {n}', 'Net': 'CONFIDENTIAL-TRADE-PRICE'}} for n in range(1, 14)]}
        self.contract = {'schema_version': 1, 'mode': 'adopted', 'audience': 'client', 'allowed_fields': ['Product'], 'template_accepted': True, 'layout_requirements': ['Letter portrait; fixture'], 'missing_image_policy': 'labeled-placeholder', 'combined_pdf': True, 'outputs': [{'tag': f'AP-{n:02}', 'item_ids': [f'item-{n}'], 'expected_pages': 1} for n in range(1,14)]}
        self.template = self.root / 'template.pdf'
        pdf(self.template, ['Accepted fixture template'])
        self.save()
        result=subprocess.run([sys.executable,str(DESIGN),'resolve','--kind','spec-book','--page','letter','--orientation','portrait','--measurement-units','imperial','--output',str(self.root/'design.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def save(self):
        (self.root / 'input.json').write_text(json.dumps(self.snapshot))
        (self.root / 'contract.json').write_text(json.dumps(self.contract))

    def command(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(HELPER), *map(str,args)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stdout + result.stderr)
        return json.loads(result.stdout if result.stdout else result.stderr)

    def prepare(self, name='job', ok=True):
        self.save()
        return self.command('prepare','--input',self.root/'input.json','--contract',self.root/'contract.json','--template',self.template,'--design',self.root/'design.json','--output',self.root/name,ok=ok)

    def render(self, name='job'):
        job = self.root/name
        for n in range(1,14):
            pdf(job/'delivery'/f'AP-{n:02}.pdf', [f'AP-{n:02} Appliance {n} Product image unavailable'])
        pdf(job/'delivery/combined.pdf', [f'AP-{n:02} Appliance {n} Product image unavailable' for n in range(1,14)])
        self.inspect(name)

    def inspect(self, name='job'):
        job = self.root/name
        manifest = json.loads((job/'internal/manifest.json').read_text())
        inspection = {'fingerprint':manifest['fingerprint'],'artifacts':{}}
        for file in (job/'delivery').glob('*.pdf'):
            inspection['artifacts'][file.name] = {'sha256':sha(file.read_bytes()),'template_sha256':sha(self.template.read_bytes()),'rendered_pages_inspected':True,'layout_matches':True,'images_checked':True,'links_checked':True,'audience_checked':True,'page_geometry_checked':True,'overflow_checked':True,'image_resolution_checked':True,'design_fingerprint':manifest['design']['fingerprint'],'evidence':'synthetic fixture contract only; not customer visual proof'}
        (job/'internal/inspection.json').write_text(json.dumps(inspection))

    def check(self, name='job', receipt='receipt.json', ok=True):
        return self.command('check','--job',self.root/name,'--input',self.root/'input.json','--contract',self.root/'contract.json','--template',self.template,'--design',self.root/'design.json','--inspection',self.root/name/'internal/inspection.json','--receipt',self.root/name/'internal'/receipt,ok=ok)

    def test_projection_scope_and_no_overwrite(self):
        self.prepare()
        render = (self.root/'job/render/data.json').read_text()
        self.assertNotIn('CONFIDENTIAL',render)
        self.assertNotIn('Net',render)
        self.assertIn('Product image unavailable',render)
        self.prepare(ok=False)

    def test_block_missing_image_and_unsafe_tag(self):
        self.contract['missing_image_policy']='block'
        self.prepare(ok=False)
        self.contract['missing_image_policy']='labeled-placeholder'
        self.contract['outputs'][0]['tag']='../outside'
        self.prepare(ok=False)
        self.assertFalse((self.root/'job').exists())

    def test_scope_and_template_fail_closed(self):
        self.contract['outputs'].pop()
        self.prepare(ok=False)
        self.contract['template_accepted']=False
        self.prepare(ok=False)

    def test_bundle_escape_and_fake_image(self):
        self.contract['outputs'][0]['images']={'item-1': {'path':'../outside.png','source':'test','status':'exact'}}
        self.prepare(ok=False)
        (self.root/'fake.png').write_text('<html>Not an image</html>')
        self.contract['outputs'][0]['images']['item-1']['path']='fake.png'
        self.prepare(ok=False)

    def test_image_bundle_containment_and_symlink_ancestors(self):
        images = self.root / 'images'; images.mkdir()
        import base64
        image = images / 'selected.png'
        image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a2XcAAAAASUVORK5CYII='))
        self.contract['outputs'][0]['images'] = {'item-1': dict(path='images/selected.png', source='sanitized image', status='exact')}
        self.prepare('valid-bundle')
        (self.root / 'linked-images').symlink_to(images, target_is_directory=True)
        (images / 'linked.png').symlink_to(image)
        for path in ('linked-images/selected.png', 'images/linked.png', 'images/../images/selected.png', str(image)):
            self.contract['outputs'][0]['images']['item-1']['path'] = path
            refused = self.prepare('rejected-bundle', ok=False)
            self.assertIn('outputs[0].images[item-1].path', refused['error'])
            self.assertFalse((self.root / 'rejected-bundle').exists())

    def custom_scope(self, tags, version=1, filenames=None):
        self.snapshot['items'] = [dict(item_id=f'item-{n}', revision=1, tag=tag, fields={'Product': f'Fixture {n}'})
                                  for n, tag in enumerate(tags)]
        self.contract['schema_version'] = version
        self.contract['outputs'] = [dict(tag=tag, item_ids=[f'item-{n}'], expected_pages=1)
                                    for n, tag in enumerate(tags)]
        for group, filename in zip(self.contract['outputs'], filenames or []):
            if filename is not None:
                group['filename'] = filename

    def render_custom_scope(self, name='job'):
        manifest = json.loads((self.root / name / 'internal/manifest.json').read_text())
        for group in manifest['outputs']:
            pdf(self.root / name / 'delivery' / group.get('filename', group['tag'] + '.pdf'),
                [group['tag'] + ' Product image unavailable'])
        pdf(self.root / name / 'delivery/combined.pdf',
            [group['tag'] + ' Product image unavailable' for group in manifest['outputs']])
        self.inspect(name)

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_26_dotted_ids_intake_prepare_render_check(self):
        tags = [f'SX.{"A" if i % 2 else "B"}-{i:03}' for i in range(1, 27)]
        spec = importlib.util.spec_from_file_location('identity_intake', ROOT / 'tools/transformers/ffe_intake.py')
        intake = importlib.util.module_from_spec(spec); spec.loader.exec_module(intake)
        (self.root / 'source.txt').write_text('Sanitized source')
        request = dict(schema_version=1, mode='one-off', job_id='exact-identities',
                       sources=[dict(id='source', kind='file', reference='source.txt', sha256=None, status='available')],
                       selected_tags=tags, template=None, record_basis=None, supersedes=None,
                       actor='Test', reason='Explicit sanitized intake')
        accepted = intake.manifest(self.root, request, standalone=True)
        self.custom_scope(tags)
        self.snapshot['source'] = dict(input_hash=accepted['input_hash'], selected_tags=tags)
        self.prepare(); self.render_custom_scope()
        checked = self.check()
        self.assertEqual(checked['mechanical_status'], 'passed')
        self.assertFalse(checked['workflowCompleted'])
        self.assertEqual(checked['visual_inspection'], {'status':'host-reported','independent':False})
        self.assertEqual([entry['file'] for entry in checked['verified_artifacts']], [tag + '.pdf' for tag in tags] + ['combined.pdf'])
        self.assertEqual([entry['tag'] for entry in checked['outputs']], tags)

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_v2_mapped_identity_roundtrip_and_resume_invalidation(self):
        tags = ['CON', 'A.', 'CASE-A', 'case-a']
        filenames = ['console.pdf', 'A-dot.pdf', None, 'lowercase-a.pdf']
        self.custom_scope(tags, 2, filenames)
        self.prepare(); self.render_custom_scope()
        checked = self.check()
        self.assertEqual(checked['schema_version'], 2)
        self.assertEqual([group['tag'] for group in checked['outputs']], tags)
        self.assertEqual([group['filename'] for group in checked['outputs']], ['console.pdf', 'A-dot.pdf', 'CASE-A.pdf', 'lowercase-a.pdf'])
        self.prepare('same')
        reused = self.command('resume', '--previous', self.root / 'job', '--job', self.root / 'same', '--receipt', self.root / 'job/internal/receipt.json')
        self.assertEqual(len(reused['reusable']), 4)
        self.contract['outputs'][0]['filename'] = 'console-changed.pdf'
        self.prepare('changed-mapping')
        changed = self.command('resume', '--previous', self.root / 'job', '--job', self.root / 'changed-mapping', '--receipt', self.root / 'job/internal/receipt.json')
        self.assertEqual(changed['invalidated'], ['console-changed.pdf'])
        self.assertEqual(len(changed['reusable']), 3)
        self.assertTrue((self.root / 'job/delivery/console.pdf').is_file())

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_pdf_identity_cannot_be_replaced_with_filename_or_wrong_variant(self):
        self.custom_scope(['SX.A-001'], 2, ['mapped-file.pdf'])
        self.prepare(); self.render_custom_scope(); self.check()
        for index, wrong in enumerate(('mapped-file.pdf', 'SX.A-001.pdf', 'SX.A-001-wide', 'SX-A-001')):
            pdf(self.root / 'job/delivery/mapped-file.pdf', [wrong + ' Product image unavailable'])
            self.inspect()
            rejected = self.check(receipt=f'wrong-identity-{index}.json', ok=False)
            self.assertTrue(any('expected tag not found' in message for message in rejected['failures']))

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_extended_length_and_v1_manifest_remain_readable(self):
        self.custom_scope(['I' * 64, 'i' * 80])
        self.prepare(); self.render_custom_scope()
        original = (self.root / 'job/internal/manifest.json').read_bytes()
        checked = self.check()
        self.assertEqual(checked['schema_version'], 1)
        self.assertTrue(all('filename' not in entry for entry in checked['outputs']))
        self.assertEqual((self.root / 'job/internal/manifest.json').read_bytes(), original)
        self.contract['schema_version'] = 2
        self.prepare('version-two')
        reused = self.command('resume', '--previous', self.root / 'job', '--job', self.root / 'version-two', '--receipt', self.root / 'job/internal/receipt.json')
        self.assertEqual(len(reused['reusable']), 2)

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_legacy_output_tag_mapping_is_preserved_without_reverse_inference(self):
        self.custom_scope(['OLD-MAPPED'])
        self.snapshot['items'][0]['tag'] = 'SX.A-001'
        self.prepare(); self.render_custom_scope()
        before = (self.root / 'input.json').read_bytes()
        checked = self.check()
        self.assertEqual(checked['outputs'][0]['tag'], 'OLD-MAPPED')
        self.assertNotIn('filename', checked['outputs'][0])
        self.assertEqual((self.root / 'input.json').read_bytes(), before)

    def test_malformed_v2_manifest_does_not_use_legacy_fallback(self):
        self.custom_scope(['SAFE'], 2)
        self.prepare()
        manifest_file = self.root / 'job/internal/manifest.json'
        document = json.loads(manifest_file.read_text()); del document['outputs'][0]['filename']
        manifest_file.write_text(json.dumps(document))
        rejected = self.check(ok=False)
        self.assertIn('filename', rejected['error'])

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_derived_identity_and_mapping_cannot_override_original_contract(self):
        self.custom_scope(['SOURCE-ID'], 2, ['approved.pdf'])
        self.prepare(); self.render_custom_scope(); self.check()
        for index, (field, value) in enumerate((('filename', 'unapproved.pdf'), ('tag', 'WRONG-ID'))):
            name = f'tampered-{index}'
            self.prepare(name)
            manifest_file = self.root / name / 'internal/manifest.json'
            render_file = self.root / name / 'render/data.json'
            manifest = json.loads(manifest_file.read_text())
            render = json.loads(render_file.read_text())
            manifest['outputs'][0][field] = value
            render['outputs'][0][field] = value
            render_file.write_text(json.dumps(render))
            manifest['render_sha256'] = sha(render_file.read_bytes())
            manifest_file.write_text(json.dumps(manifest))
            self.render_custom_scope(name)
            rejected = self.check(name, ok=False)
            self.assertIn('contract', rejected['error'])
            rejected = self.command('resume', '--previous', self.root / 'job', '--job', self.root / name,
                                    '--receipt', self.root / 'job/internal/receipt.json', ok=False)
            self.assertIn('contract', rejected['error'])
            rejected = self.command('resume', '--previous', self.root / name, '--job', self.root / 'job',
                                    '--receipt', self.root / 'job/internal/receipt.json', ok=False)
            self.assertIn('contract', rejected['error'])

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_real_pdf_complete_missing_and_leakage(self):
        self.prepare()
        self.render()
        result=self.check()
        self.assertEqual(result['mechanical_status'], 'passed')
        self.assertFalse(result['workflowCompleted'])
        self.assertEqual(len(result['verified_artifacts']),14)
        (self.root/'job/delivery/AP-13.pdf').unlink()
        self.assertFalse(self.check(receipt='missing.json',ok=False)['workflowCompleted'])
        pdf(self.root/'job/delivery/AP-13.pdf',['AP-13 CONFIDENTIAL-TRADE-PRICE Product image unavailable'])
        self.inspect()
        result=self.check(receipt='leak.json',ok=False)
        self.assertTrue(any('non-allowlisted' in v for v in result['failures']))
        self.assertTrue((self.root/'job/internal/receipt.json').exists())

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_stale_and_selective_resume(self):
        self.prepare()
        self.render()
        self.check()
        self.snapshot['items'][4]['revision']=2
        self.snapshot['items'][4]['fields']['Product']='Corrected AP-05'
        self.snapshot['revision']=2
        self.save()
        self.check(receipt='stale.json',ok=False)
        self.prepare('new')
        result=self.command('resume','--previous',self.root/'job','--job',self.root/'new','--receipt',self.root/'job/internal/receipt.json')
        self.assertEqual(result['invalidated'],['AP-05.pdf'])
        self.assertEqual(len(result['reusable']),12)
        self.snapshot['source']={'sha256':'c'*64}
        self.prepare('changed-source')
        result=self.command('resume','--previous',self.root/'job','--job',self.root/'changed-source','--receipt',self.root/'job/internal/receipt.json')
        self.assertEqual(len(result['invalidated']),13)

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_final_pdf_change_requires_fresh_inspection_of_exact_bytes(self):
        self.prepare()
        self.render()
        self.assertEqual(self.check()['mechanical_status'], 'passed')
        original_receipt = (self.root/'job/internal/receipt.json').read_bytes()
        pdf(self.root/'job/delivery/AP-01.pdf', ['AP-01 Corrected layout Product image unavailable'])
        stale = self.check(receipt='after-layout-stale.json', ok=False)
        self.assertFalse(stale['workflowCompleted'])
        self.assertTrue(any('stale artifact inspection hash' in failure for failure in stale['failures']))
        self.inspect()  # Synthetic attestation only; actual visual review remains a separate host gate.
        self.assertEqual(self.check(receipt='after-layout-reviewed.json')['mechanical_status'], 'passed')
        self.assertEqual((self.root/'job/internal/receipt.json').read_bytes(), original_receipt)

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_front_matter_does_not_mask_content_order(self):
        self.contract['front_matter_pages']=1
        self.prepare()
        self.render()
        index='Index ' + ' '.join(f'AP-{n:02}' for n in range(1,14))
        pdf(self.root/'job/delivery/combined.pdf',[index]+[f'AP-{n:02} Product image unavailable' for n in range(1,14)])
        self.inspect()
        self.assertEqual(self.check()['mechanical_status'], 'passed')
        pdf(self.root/'job/delivery/combined.pdf',[index]+[f'AP-{n:02} Product image unavailable' for n in range(13,0,-1)])
        self.inspect()
        result=self.check(receipt='reversed-content.json',ok=False)
        self.assertTrue(any('order differs' in value for value in result['failures']))

    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('pypdf'), 'managed PyMuPDF/pypdf unavailable; PDF integration requires both')
    def test_false_pdf_and_uninspected_and_order(self):
        self.prepare()
        self.render()
        (self.root/'job/delivery/AP-01.pdf').write_text('<html>AP-01</html>')
        self.inspect()
        self.check(ok=False)
        self.render()
        inspection=self.root/'job/internal/inspection.json'
        body=json.loads(inspection.read_text())
        body['artifacts']['AP-05.pdf']['rendered_pages_inspected']=False
        inspection.write_text(json.dumps(body))
        self.check(receipt='uninspected.json',ok=False)
        pdf(self.root/'job/delivery/combined.pdf',[f'AP-{n:02} Product image unavailable' for n in range(13,0,-1)])
        self.inspect()
        result=self.check(receipt='order.json',ok=False)
        self.assertTrue(any('order differs' in v for v in result['failures']))
        pdf(self.root/'job/delivery/AP-01.pdf',['AP-010 Wrong tag Product image unavailable'])
        self.inspect()
        result=self.check(receipt='wrongtag.json',ok=False)
        self.assertTrue(any('expected tag not found' in v for v in result['failures']))
        pdf(self.root/'job/delivery/AP-01.pdf',['AP-01 No image disclosure'])
        self.inspect()
        result=self.check(receipt='imagelabel.json',ok=False)
        self.assertTrue(any('image disclosure missing' in v for v in result['failures']))


if __name__ == '__main__':
    unittest.main()
