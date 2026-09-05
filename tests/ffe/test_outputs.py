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

    @unittest.skipUnless(shutil.which('pdfinfo') and shutil.which('pdftotext') and importlib.util.find_spec('pypdf'), 'host Poppler/pypdf unavailable; PDF integration requires both')
    def test_real_pdf_complete_missing_and_leakage(self):
        self.prepare()
        self.render()
        result=self.check()
        self.assertTrue(result['workflowCompleted'])
        self.assertEqual(len(result['verified_artifacts']),14)
        (self.root/'job/delivery/AP-13.pdf').unlink()
        self.assertFalse(self.check(receipt='missing.json',ok=False)['workflowCompleted'])
        pdf(self.root/'job/delivery/AP-13.pdf',['AP-13 CONFIDENTIAL-TRADE-PRICE Product image unavailable'])
        self.inspect()
        result=self.check(receipt='leak.json',ok=False)
        self.assertTrue(any('non-allowlisted' in v for v in result['failures']))
        self.assertTrue((self.root/'job/internal/receipt.json').exists())

    @unittest.skipUnless(shutil.which('pdfinfo') and shutil.which('pdftotext') and importlib.util.find_spec('pypdf'), 'host Poppler/pypdf unavailable; PDF integration requires both')
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

    @unittest.skipUnless(shutil.which('pdfinfo') and shutil.which('pdftotext') and importlib.util.find_spec('pypdf'), 'host Poppler/pypdf unavailable; PDF integration requires both')
    def test_front_matter_does_not_mask_content_order(self):
        self.contract['front_matter_pages']=1
        self.prepare()
        self.render()
        index='Index ' + ' '.join(f'AP-{n:02}' for n in range(1,14))
        pdf(self.root/'job/delivery/combined.pdf',[index]+[f'AP-{n:02} Product image unavailable' for n in range(1,14)])
        self.inspect()
        self.assertTrue(self.check()['workflowCompleted'])
        pdf(self.root/'job/delivery/combined.pdf',[index]+[f'AP-{n:02} Product image unavailable' for n in range(13,0,-1)])
        self.inspect()
        result=self.check(receipt='reversed-content.json',ok=False)
        self.assertTrue(any('order differs' in value for value in result['failures']))

    @unittest.skipUnless(shutil.which('pdfinfo') and shutil.which('pdftotext') and importlib.util.find_spec('pypdf'), 'host Poppler/pypdf unavailable; PDF integration requires both')
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
