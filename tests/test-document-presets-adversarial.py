#!/usr/bin/env python3
"""Independent physical-size acceptance; no private content or render engine."""
import json
import hashlib
import shutil
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ.get('AS_TEST_OUTPUTS_ROOT',ROOT))
HELPER=SOURCE/'tools/renderers/document_contracts.py'
EXPECTED=json.loads((ROOT/'tests/ffe/page-size-expectations.json').read_text())
NAMES={name:name for name in EXPECTED['presets']}

class PhysicalSizes(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def resolve(self,page='letter',orientation='portrait',units='metric',extra=(),ok=True):
        target=self.root/f'resolved-{len(list(self.root.iterdir()))}.json'
        cmd=[sys.executable,str(HELPER),'resolve','--kind','product-cut-sheet','--page',page,'--orientation',orientation,'--measurement-units',units,'--output',str(target),*extra]
        result=subprocess.run(cmd,capture_output=True,text=True)
        if ok:
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            return json.loads(target.read_text())
        self.assertNotEqual(result.returncode,0,result.stdout)
        self.assertFalse(target.exists(),'failed resolution must not emit an apparently valid design')
    def test_all_presets_in_both_orientations(self):
        for name,(width,height,unit) in EXPECTED['presets'].items():
            factor=72 if unit=='in' else 72/25.4
            for orientation in ['portrait','landscape']:
                with self.subTest(name=name,orientation=orientation):
                    resolved=self.resolve(NAMES[name],orientation)
                    w,h=(width,height) if orientation=='portrait' else (height,width)
                    self.assertAlmostEqual(resolved['page']['width_pt'],w*factor,delta=EXPECTED['point_tolerance'])
                    self.assertAlmostEqual(resolved['page']['height_pt'],h*factor,delta=EXPECTED['point_tolerance'])
    def test_measurement_policy_does_not_change_paper(self):
        a=self.resolve('a4',units='metric');b=self.resolve('a4',units='imperial')
        for key in ['width_pt','height_pt']:self.assertEqual(a['page'][key],b['page'][key])
    def test_custom_metric_and_imperial(self):
        for w,h,unit in EXPECTED['custom_cases']:
            for orientation in ['portrait','landscape']:
                factor=72 if unit=='in' else 72/25.4
                r=self.resolve('custom',orientation,extra=['--custom-width',str(w),'--custom-height',str(h),'--custom-units',unit])
                expected=(w,h) if orientation=='portrait' else (h,w)
                self.assertAlmostEqual(r['page']['width_pt'],expected[0]*factor,delta=.05)
                self.assertAlmostEqual(r['page']['height_pt'],expected[1]*factor,delta=.05)
    def test_invalid_custom_sizes_fail_closed(self):
        for value in ['0','-1','nan','inf']:
            with self.subTest(value=value):self.resolve('custom',extra=['--custom-width',value,'--custom-height','300','--custom-units','mm'],ok=False)
    def override(self,name,label):
        root=self.root/name
        directory=root/'standards/documents';directory.mkdir(parents=True)
        original=SOURCE/'studio/standards/documents'
        for file in original.iterdir():
            if file.is_file():shutil.copyfile(file,directory/file.name)
        md=directory/'design-system.md';md.write_text(md.read_text()+'\n'+label+'\n')
        manifest=directory/'design-system.json';data=json.loads(manifest.read_text());data['assets']['design-system.md']=hashlib.sha256(md.read_bytes()).hexdigest();manifest.write_text(json.dumps(data))
        return root
    def test_project_override_precedes_studio(self):
        studio=self.override('studio','Synthetic studio override');(studio/'STUDIO.md').write_text('# Synthetic studio')
        project=self.override('project','Synthetic project override')
        r=self.resolve(extra=['--studio',str(studio),'--project-assets',str(project)])
        identity=next(i for i in r['identities'] if i['id']=='as.document-design-system')
        self.assertEqual(identity['layer'],'project')
        texts=''.join(a['text'] for a in r['assets'])
        self.assertIn('Synthetic project override',texts)
        self.assertNotIn('Synthetic studio override',texts)
        self.assertNotIn(str(self.root),json.dumps(r))
    def test_corrupt_override_cannot_fall_back(self):
        project=self.override('project','Synthetic override')
        (project/'standards/documents/design-system.md').write_text('Corrupt asset without manifest update')
        self.resolve(extra=['--project-assets',str(project)],ok=False)
    def test_missing_declared_asset_blocks_resolution(self):
        project=self.override('project','Synthetic override')
        (project/'standards/documents/design-system.md').unlink()
        self.resolve(extra=['--project-assets',str(project)],ok=False)
    def test_shared_style_changes_cut_sheet_and_book_without_skill_edits(self):
        project=self.override('project','Synthetic override')
        def both():
            results=[]
            for kind in ['product-cut-sheet','spec-book']:
                target=self.root/('style-'+kind+'-'+str(len(list(self.root.iterdir())))+'.json')
                r=subprocess.run([sys.executable,str(HELPER),'resolve','--kind',kind,'--page','letter','--orientation','portrait','--measurement-units','metric','--project-assets',str(project),'--output',str(target)],capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr)
                results.append(json.loads(target.read_text())['fingerprint'])
            return results
        before=both()
        manifest=project/'standards/documents/design-system.json';d=json.loads(manifest.read_text());d['layouts']['compact']['body_pt']=11;manifest.write_text(json.dumps(d))
        after=both()
        self.assertTrue(all(a!=b for a,b in zip(before,after)))
    def test_unknown_preset_no_silent_fallback(self):self.resolve('A4-ish',ok=False)
    def test_invalid_orientation_no_silent_rotation(self):self.resolve(orientation='auto',ok=False)
    def test_invalid_units_not_inferred(self):self.resolve('custom',extra=['--custom-width','8','--custom-height','10','--custom-units','cm'],ok=False)

if __name__=='__main__':unittest.main()
