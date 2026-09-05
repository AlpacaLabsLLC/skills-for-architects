"""Shared-asset resolution and physical page geometry regression checks."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from test_outputs import ROOT, DESIGN, pdf, sha

sys.path.insert(0,str(ROOT/'tools/renderers'))
from ffe_outputs import verify_page_boxes


class DocumentDesign(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.counter=0

    def resolve(self, page='letter', orientation='portrait', extra=(), kind='spec-book', ok=True):
        self.counter+=1
        target=self.root/f'resolution-{self.counter}.json'
        result=subprocess.run([sys.executable,str(DESIGN),'resolve','--kind',kind,'--page',page,'--orientation',orientation,'--measurement-units','metric','--output',str(target),*map(str,extra)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0 if ok else 2,result.stdout+result.stderr)
        return json.loads(target.read_text()) if ok else None

    def test_all_named_physical_sizes_both_orientations(self):
        imperial={'letter':(8.5,11),'legal':(8.5,14),'tabloid':(11,17),'ansi-c':(17,22),'ansi-d':(22,34),'ansi-e':(34,44),'arch-a':(9,12),'arch-b':(12,18),'arch-c':(18,24),'arch-d':(24,36),'arch-e':(36,48),'arch-e1':(30,42)}
        metric={'a4':(210,297),'a3':(297,420),'a2':(420,594),'a1':(594,841),'a0':(841,1189)}
        for table,factor in [(imperial,72),(metric,72/25.4)]:
            for page,(w,h) in table.items():
                for orientation in ['portrait','landscape']:
                    result=self.resolve(page,orientation)
                    expected=(w*factor,h*factor) if orientation=='portrait' else (h*factor,w*factor)
                    self.assertAlmostEqual(result['page']['width_pt'],expected[0],places=5)
                    self.assertAlmostEqual(result['page']['height_pt'],expected[1],places=5)
                    self.assertEqual(result['page']['measurement_units'],'metric')
                    self.assertEqual(len(result['identities']),3)
                    self.assertNotIn(str(ROOT),json.dumps(result))

    def test_custom_and_invalid_dimensions(self):
        result=self.resolve('custom','landscape',extra=['--custom-width','10','--custom-height','16','--custom-units','in'])
        self.assertEqual(result['page']['width_pt'],1152)
        self.assertEqual(result['page']['height_pt'],720)
        for value in ['0','-1','nan','inf','10000']:
            self.resolve('custom',extra=['--custom-width',value,'--custom-height','16','--custom-units','in'],ok=False)
        self.resolve('custom',ok=False)
        self.resolve('letter',extra=['--custom-width','10','--custom-height','16','--custom-units','in'],ok=False)
        self.resolve('not-a-preset',ok=False)

    def override(self, name, text):
        root=self.root/name
        path=root/'standards/documents'
        path.mkdir(parents=True)
        (root/'STUDIO.md').write_text('# Studio')
        source=ROOT/'studio/standards/documents'
        data=json.loads((source/'design-system.json').read_text())
        (path/'design-system.md').write_bytes(text)
        data['assets']['design-system.md']=sha(text)
        (path/'design-system.json').write_text(json.dumps(data))
        return root

    def test_precedence_and_dependency_hashes(self):
        studio=self.override('studio',b'Studio branding\r\nExact CRLF bytes\r\n')
        project=self.override('project',b'Project accepted branding\n')
        baseline=self.resolve()
        studio_result=self.resolve(extra=['--studio',studio])
        project_result=self.resolve(extra=['--studio',studio,'--project-assets',project])
        self.assertEqual(studio_result['identities'][0]['layer'],'studio')
        self.assertEqual(project_result['identities'][0]['layer'],'project')
        self.assertNotEqual(baseline['fingerprint'],studio_result['fingerprint'])
        self.assertNotEqual(studio_result['fingerprint'],project_result['fingerprint'])
        # Both consumers see one shared change; neither skill needs editing.
        cut=self.resolve(extra=['--studio',studio],kind='product-cut-sheet')
        self.assertEqual(cut['identities'][0],studio_result['identities'][0])
        bad_preset=json.loads((studio/'standards/documents/design-system.json').read_text())
        bad_preset['presets']['letter']['width']=9
        (studio/'standards/documents/design-system.json').write_text(json.dumps(bad_preset))
        self.resolve(extra=['--studio',studio],ok=False)
        bad_preset['presets']['letter']['width']=8.5
        (studio/'standards/documents/design-system.json').write_text(json.dumps(bad_preset))
        (studio/'standards/documents/design-system.md').write_text('Changed without manifest update')
        self.resolve(extra=['--studio',studio],ok=False)
        (project/'standards/documents/design-system.md').unlink()
        self.resolve(extra=['--studio',studio,'--project-assets',project],ok=False)

    @unittest.skipUnless(importlib.util.find_spec('pypdf'), 'host pypdf unavailable; geometry acceptance requires it')
    def test_all_page_geometry_rotation_crop_and_unit(self):
        from pypdf import PdfReader,PdfWriter
        from pypdf.generic import NameObject,NumberObject
        source=self.root/'source.pdf'
        pdf(source,['AP-01','AP-02'])
        declared=self.resolve()['page']
        self.assertEqual(len(verify_page_boxes(source,declared)),2)
        for change in ['media','crop','rotate','unit']:
            reader=PdfReader(source)
            writer=PdfWriter()
            for index,page in enumerate(reader.pages):
                if index==1:
                    if change=='media':page.mediabox.upper_right=(700,900)
                    elif change=='crop':page.cropbox.upper_right=(600,780)
                    elif change=='rotate':page.rotate(90)
                    else:page[NameObject('/UserUnit')]=NumberObject(2)
                writer.add_page(page)
            target=self.root/(change+'.pdf')
            with target.open('wb') as handle:writer.write(handle)
            with self.assertRaises(ValueError,msg=change):verify_page_boxes(target,declared)


if __name__=='__main__':unittest.main()
