#!/usr/bin/env python3
"""Independent synthetic contract checks. No historical customer completion claims."""
import argparse
import copy
import contextlib
import io
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

records = load('records', Path(os.environ.get('AS_TEST_RECORDS_ROOT', ROOT)) / 'tools/workspace/ffe_records.py')
outputs = load('outputs', Path(os.environ.get('AS_TEST_OUTPUTS_ROOT', ROOT)) / 'tools/renderers/ffe_outputs.py')

class RecordAdversarial(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'PROJECT.md').write_text('# Synthetic fixture\n')
        self.first = records.write_revision(self.root, dict(name='Fixture', actor='Fixture user', reason='Explicit adoption', source={'file':'source.csv'}, items=[dict(tag='AP-01',fields={'finish':'White','quantity':1}),dict(tag='AP-02',fields={'finish':'Blue','quantity':2})]))
        self.sid = self.first['schedule_id']
    def tearDown(self):
        self.temp.cleanup()
    def proposal(self, record=None):
        return dict(name='Fixture',actor='Fixture user',reason='Explicit change',items=copy.deepcopy((record or self.first)['items']))
    def bytes(self):
        return {str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
    def test_stale_write_preserves_all_record_bytes(self):
        p=self.proposal(); p['items'][0]['fields']['finish']='Red'
        records.write_revision(self.root,p,self.sid,1)
        before=self.bytes()
        with self.assertRaises(ValueError): records.write_revision(self.root,p,self.sid,1)
        self.assertEqual(before,self.bytes())
    def test_retag_keeps_identity_and_old_revision(self):
        p=self.proposal(); p['items'][0]['tag']='AP-99'
        new=records.write_revision(self.root,p,self.sid,1)
        self.assertEqual(new['items'][0]['item_id'],self.first['items'][0]['item_id'])
        self.assertEqual(new['items'][0]['revision'],2)
        self.assertEqual(records.read_schedule(self.root,self.sid,1)['items'][0]['tag'],'AP-01')
    def test_removal_requires_explicit_intent_and_keeps_history(self):
        p=self.proposal(); p['items'].pop()
        before=self.bytes()
        with self.assertRaises(ValueError): records.write_revision(self.root,p,self.sid,1)
        self.assertEqual(before,self.bytes())
        new=records.write_revision(self.root,p,self.sid,1,True)
        self.assertEqual(len(new['items']),1)
        self.assertEqual(len(records.read_schedule(self.root,self.sid,1)['items']),2)
    def test_conflicting_workbook_change_is_readonly(self):
        p=self.proposal();p['items'][0]['fields']['finish']='Red'
        records.write_revision(self.root,p,self.sid,1)
        incoming=self.proposal();incoming['items'][0]['fields']['finish']='Green'
        before=self.bytes(); result=records.reconcile(self.root,self.sid,1,incoming)
        self.assertEqual(len(result['conflicts']),1)
        self.assertEqual(result['conflicts'][0]['base'],'White')
        self.assertEqual(before,self.bytes())
    def test_corrupt_snapshot_cannot_create_recovery(self):
        snap=records.snapshot(self.root,self.sid)
        folder=self.root/'ffe/recovery'/self.sid/snap['snapshot_id']
        (folder/'schedule.csv').write_text('damaged')
        with self.assertRaises(ValueError): records.recover(self.root,self.sid,snap['snapshot_id'],'recovered.csv')
        self.assertFalse((self.root/'recovered.csv').exists())
    def test_recovery_never_overwrites_unreviewed_file(self):
        snap=records.snapshot(self.root,self.sid)
        out=self.root/'work.csv';out.write_bytes(b'Unreviewed user changes')
        with self.assertRaises(FileExistsError): records.recover(self.root,self.sid,snap['snapshot_id'],'work.csv')
        self.assertEqual(out.read_bytes(),b'Unreviewed user changes')
    def test_failed_export_does_not_create_empty_artifact(self):
        out=self.root/'failed.csv'
        result=subprocess.run([sys.executable,records.__file__,'export','--project',str(self.root),'--schedule','11111111-1111-4111-8111-111111111111','--destination','failed.csv'],capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(out.exists())
    def test_explicit_symlink_project_refused(self):
        link=self.root/'alias';link.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):records.project_root(link)
    def test_tampered_item_blocks_schedule_read(self):
        ref=self.first['item_refs'][0];p=self.root/ref['path'];p.write_text(p.read_text().replace('White','Green'))
        with self.assertRaises(ValueError):records.read_schedule(self.root,self.sid)

class OutputAdversarial(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.snapshot={'source':{'file':'source.csv','revision':1},'items':[{'item_id':'item-1','revision':1,'fields':{'name':'Synthetic Product','trade_cost':'PRIVATE_SENTINEL_92842'}}]}
        self.contract={'schema_version':1,'mode':'one-off','audience':'client','template_accepted':True,'layout_requirements':['Single page'],'allowed_fields':['name'],'missing_image_policy':'labeled-placeholder','combined_pdf':False,'outputs':[{'tag':'AP-01','item_ids':['item-1'],'expected_pages':1}]}
        self.template=self.root/'template.txt';self.template.write_text('Synthetic reference')
    def tearDown(self):self.temp.cleanup()
    def prepare(self, name='job'):
        inp=self.root/'input.json';inp.write_text(json.dumps(self.snapshot))
        con=self.root/'contract.json';con.write_text(json.dumps(self.contract))
        with contextlib.redirect_stdout(io.StringIO()):
            outputs.prepare(argparse.Namespace(input=inp,contract=con,template=self.template,output=self.root/name))
        return self.root/name
    def test_client_render_data_does_not_contain_private_field(self):
        job=self.prepare()
        self.assertNotIn('PRIVATE_SENTINEL_92842',(job/'render/data.json').read_text())
    def test_missing_image_block_prevents_job_creation(self):
        self.contract['missing_image_policy']='block'
        with self.assertRaises(ValueError):self.prepare()
        self.assertFalse((self.root/'job').exists())
    def test_duplicate_group_membership_refused(self):
        self.contract['outputs'].append({'tag':'AP-02','item_ids':['item-1'],'expected_pages':1})
        with self.assertRaises(ValueError):self.prepare()
    def test_source_revision_change_invalidates_resume_fingerprint(self):
        old=self.prepare('old'); oldm=json.loads((old/'internal/manifest.json').read_text())
        self.snapshot['source']['revision']=2
        new=self.prepare('new'); newm=json.loads((new/'internal/manifest.json').read_text())
        self.assertNotEqual(oldm['outputs'][0]['fingerprint'],newm['outputs'][0]['fingerprint'])
    def test_template_change_invalidates_fingerprint(self):
        old=self.prepare('old');oldm=json.loads((old/'internal/manifest.json').read_text())
        self.template.write_text('Changed synthetic reference')
        new=self.prepare('new');newm=json.loads((new/'internal/manifest.json').read_text())
        self.assertNotEqual(oldm['outputs'][0]['fingerprint'],newm['outputs'][0]['fingerprint'])

if __name__=='__main__':unittest.main()
