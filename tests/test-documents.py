import importlib.util
import json
import os
from pathlib import Path
import tempfile
import shutil
import unittest
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/receive/scripts'))
import documents as d
import workspaces as w
d=w.d

class Documents(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.base=Path(self.temp.name).resolve(); self.root=self.base/'Prójéct with spaces'
        self.init={'target':str(self.root),'name':'Project','project_id':'P001','type':'internal','status':'active','kind':'software','client':'Internal','client_code':'INT','vocabularies':{'phases':['alpha','beta'],'scopes':['design'],'originators':['firm']},'dry_run':False}
        w.dispatch('project.init',self.init)
        self.data={'project_root':str(self.root)}
        self.coords={'phase':'alpha','stage':'1-design','scope':'design','originator':'firm','date':'2026-09-13'}
    def tearDown(self): self.temp.cleanup()
    def put(self,name='source.pdf',content=b'%PDF-synthetic',**meta):
        source=self.base/name; source.write_bytes(content)
        return d.dispatch('documents.register',{**self.data,'source_path':str(source),'coordinates':self.coords,'kind':'drawing','metadata':meta,'dry_run':False})['document']
    def test_fresh_setup_and_registration(self):
        self.assertFalse((self.root/'decisions').exists())
        self.assertFalse((self.root/'TASKS.md').exists())
        row=self.put(); self.assertEqual(row['id'],'D000001'); self.assertEqual((self.base/'source.pdf').read_bytes(),b'%PDF-synthetic')
        self.assertTrue(d.verify(self.data)['valid'])
        self.assertEqual(self.put()['id'],row['id'])
        self.assertEqual(len(d.rows_for(self.root)),1)
    def test_revision_queries_and_provenance(self):
        first=self.put()
        second=self.put('revision.pdf',b'%PDF-revision',supersedes=first['id'],source={'type':'email','message_id':'synthetic-message','expires':'2026-09-01'},change_id='C001')
        result=d.query({**self.data,'filters':{'latest':True,'kind':'drawing'}})
        self.assertEqual(result['documents'][0]['id'],second['id'])
        self.assertEqual(d.query({**self.data,'filters':{'source_type':'email','change_id':'C001'}})['count'],1)
        self.assertIn('expired_source',[f['code'] for f in d.verify(self.data)['findings']])
    def test_invalid_input_never_writes(self):
        before=(self.root/'DOCUMENTS.csv').read_bytes()
        with self.assertRaises(d.DomainError): d.resolved({**self.data,'coordinates':{**self.coords,'phase':'unknown'},'kind':'drawing'})
        source=self.base/'bad.pdf'; source.write_bytes(b'bad')
        with self.assertRaises(d.DomainError): d.register({**self.data,'coordinates':self.coords,'kind':'drawing','source_path':str(source),'metadata':{'supersedes':'D000123'},'dry_run':False})
        self.assertEqual(before,(self.root/'DOCUMENTS.csv').read_bytes())
    def test_move_keeps_identity_and_relative_links(self):
        row=self.put()
        note=self.put('note.md',b'[drawing](source.pdf)\n')
        result=d.move({**self.data,'id':row['id'],'expected_sha256':row['sha256'],'coordinates':{**self.coords,'phase':'beta'},'dry_run':False})
        self.assertEqual(result['document']['id'],row['id'])
        self.assertEqual(result['document']['sha256'],row['sha256'])
        self.assertFalse((self.root/row['path']).exists())
        changed=(self.root/note['path']).read_text()
        self.assertIn('../../../../../beta/',changed)
        self.assertTrue(d.verify(self.data)['valid'])
    def test_failure_rolls_back_every_written_byte(self):
        row=self.put(); before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        os.environ['AS_DOCUMENT_TEST_FAIL_AFTER']='1'
        try:
            with self.assertRaises(OSError): d.move({**self.data,'id':row['id'],'expected_sha256':row['sha256'],'coordinates':{**self.coords,'phase':'beta'},'dry_run':False})
        finally: os.environ.pop('AS_DOCUMENT_TEST_FAIL_AFTER')
        after={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
    def test_custom_and_empty_template(self):
        text=(self.root/'PROJECT.md').read_text().replace(d.DEFAULT_TEMPLATE,'{scope}/{phase}/{date}/{originator}/{stage}')
        (self.root/'PROJECT.md').write_text(text)
        row=self.put(); self.assertEqual(row['path'],'design/alpha/2026-09-13/firm/1-design/source.pdf')
        scoped=d.resolved({**self.data,'record':'SCHEDULE.csv','coordinates':self.coords})
        self.assertEqual(scoped['path'],'design/alpha/1-design/SCHEDULE.csv')
        (self.root/'PROJECT.md').write_text(text.replace('{scope}/{phase}/{date}/{originator}/{stage}',''))
        p=d.resolved({**self.data,'coordinates':self.coords,'kind':'drawing','path':'chosen folder'})
        self.assertEqual(p['folder'],'chosen folder')
    def test_package_preserves_tree(self):
        source=self.base/'package'; (source/'nested').mkdir(parents=True); (source/'nested/sheet.pdf').write_bytes(b'%PDF-package')
        result=d.register({**self.data,'source_path':str(source),'coordinates':self.coords,'kind':'drawing-package','dry_run':False})
        self.assertTrue((self.root/result['document']['path']/'nested/sheet.pdf').exists())
        self.assertTrue(d.verify(self.data)['valid'])
    def test_studio_portfolio_and_context(self):
        studio=self.base/'studio'; w.dispatch('studio.init',{'target':str(studio),'name':'Studio','task_mode':'portfolio','dry_run':False})
        project=studio/'Projects/P'; w.dispatch('project.init',{**self.init,'target':str(project),'studio_root':str(studio),'task_mode':'portfolio'})
        w.dispatch('studio.register',{'studio_root':str(studio),'project_root':str(project),'dry_run':False})
        result=w.dispatch('context.resolve',{'path':str(project)})
        self.assertEqual(result['task_register'],str(studio/'TASKS.csv'))
        self.assertFalse((project/'TASKS.csv').exists())
    def test_symlink_and_path_escape(self):
        link=self.root/'outside'; link.symlink_to(self.base,target_is_directory=True)
        with self.assertRaises(d.DomainError): d.inside(self.root,'outside/secret.pdf')
        with self.assertRaises(d.DomainError): d.inside(self.root,'../secret.pdf')

    def test_vocabulary_rename_moves_all_documents_together(self):
        drawing=self.put(); note=self.put('note.md',b'[sheet](source.pdf)\n')
        result=w.dispatch('project.vocab',{**self.data,'axis':'phase','action':'rename','old':'alpha','value':'renamed','dry_run':False})
        self.assertEqual({r['id'] for r in result['documents']},{drawing['id'],note['id']})
        self.assertTrue(all(row['phase']=='renamed' for row in d.rows_for(self.root)))
        self.assertTrue(d.verify(self.data)['valid'])
        self.assertIn('renamed',(self.root/'PROJECT.md').read_text())

    def test_vocabulary_rename_failure_preserves_manifest_and_documents(self):
        self.put(); before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        os.environ['AS_DOCUMENT_TEST_FAIL_AFTER']='2'
        try:
            with self.assertRaises(OSError): w.dispatch('project.vocab',{**self.data,'axis':'phase','action':'rename','old':'alpha','value':'new','dry_run':False})
        finally: os.environ.pop('AS_DOCUMENT_TEST_FAIL_AFTER')
        self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_studio_status_change_and_moved_identity(self):
        studio=self.base/'office'; w.studio_init({'target':str(studio),'name':'Office','dry_run':False})
        project=studio/'Projects/First name'; w.project_init({**self.init,'target':str(project),'created':'2024-02-29','status':'archived'})
        w.studio_operation('register',{'studio_root':str(studio),'project_root':str(project),'dry_run':False})
        moved=studio/'Projects/Confirmed renamed folder'; project.rename(moved)
        result=w.resolve_context({'path':str(moved)})
        self.assertEqual(result['status'],'archived'); self.assertEqual(result['project_root'],str(moved))
        status=w.studio_operation('status',{'studio_root':str(studio)})
        self.assertTrue(status['projects'][0]['path_drift']); self.assertTrue(status['projects'][0]['valid'])
        w.studio_operation('set-status',{'studio_root':str(studio),'project_id':'P001','status':'active','dry_run':False})
        self.assertEqual(d.fields((moved/'PROJECT.md').read_text())['Created'],'2024-02-29')
        self.assertEqual(d.fields((moved/'PROJECT.md').read_text())['Status'],'active')

    def test_invalid_studio_rows_do_not_look_empty(self):
        studio=self.base/'office'; w.studio_init({'target':str(studio),'name':'Office','dry_run':False})
        project=studio/'Projects/Child'; w.project_init({**self.init,'target':str(project)})
        w.studio_operation('register',{'studio_root':str(studio),'project_root':str(project),'dry_run':False})
        (project/'PROJECT.md').unlink()
        result=w.resolve_context({'path':str(studio)})
        self.assertEqual(result['type'],'studio-picker'); self.assertFalse(result['choices'][0]['valid'])

    def test_current_empty_task_mode_switch_and_populated_refusal(self):
        studio=self.base/'office'; w.studio_init({'target':str(studio),'name':'Office','dry_run':False})
        project=studio/'Projects/Child'; w.project_init({**self.init,'target':str(project)})
        w.studio_operation('register',{'studio_root':str(studio),'project_root':str(project),'dry_run':False})
        w.studio_operation('task-mode',{'studio_root':str(studio),'mode':'portfolio','dry_run':False})
        self.assertFalse((project/'TASKS.csv').exists()); self.assertTrue((studio/'TASKS.csv').exists())
        w.studio_operation('task-mode',{'studio_root':str(studio),'mode':'project','dry_run':False})
        self.assertTrue((project/'TASKS.csv').exists()); self.assertFalse((studio/'TASKS.csv').exists())

    def test_read_version_conflict_prevents_lost_update(self):
        path=self.root/'TASKS.csv'; d.read_csv(path,d.TASK_FIELDS); original=path.read_bytes(); path.write_bytes(original+b'changed externally\n')
        with self.assertRaises(d.DomainError) as raised: d.commit(self.root,{'TASKS.csv':original})
        self.assertEqual(raised.exception.code,'conflict'); self.assertTrue(path.read_bytes().endswith(b'changed externally\n'))

    def test_nested_setup_and_collision_preserve_existing_files(self):
        before=(self.root/'PROJECT.md').read_bytes()
        with self.assertRaises(d.DomainError): w.project_init({**self.init,'target':str(self.root/'nested')})
        with self.assertRaises(d.DomainError): w.project_init(self.init)
        self.assertEqual(before,(self.root/'PROJECT.md').read_bytes())

    def test_metadata_update_preserves_bytes_and_history(self):
        row=self.put(); original=(self.root/row['path']).read_bytes()
        changed=d.update({**self.data,'id':row['id'],'expected_sha256':row['sha256'],'changes':{'status':'reviewed'},'dry_run':False})['document']
        self.assertEqual((self.root/row['path']).read_bytes(),original); self.assertEqual(changed['id'],row['id']); self.assertEqual(len(json.loads(changed['history'])),2)

    def test_explicit_recovery_restores_interrupted_write(self):
        transaction=self.root/'.as-document-transaction'; transaction.mkdir(); original=(self.root/'TASKS.csv').read_bytes(); (transaction/'0.backup').write_bytes(original)
        (transaction/'journal.json').write_text(json.dumps({'state':'prepared','files':[{'path':'TASKS.csv','backup':'0.backup','existed':True}]}))
        (self.root/'TASKS.csv').write_text('interrupted')
        with self.assertRaises(d.DomainError): d.commit(self.root,{'TASKS.csv':original})
        result=d.dispatch('documents.recover',{**self.data,'dry_run':False})
        self.assertTrue(result['recovered']); self.assertEqual((self.root/'TASKS.csv').read_bytes(),original)

    def test_exported_modules_use_their_own_packaged_support(self):
        exported=self.base/'exported package'; shutil.copytree(ROOT/'skills/receive/scripts',exported,ignore=shutil.ignore_patterns('__pycache__'))
        spec=importlib.util.spec_from_file_location('exported_workspace',exported/'workspaces.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertEqual(Path(module.d.__file__).resolve(),(exported/'documents.py').resolve())
        target=self.base/'Exported fresh project'; module.dispatch('project.init',{**self.init,'target':str(target)})
        source=self.base/'export-input.pdf'; source.write_bytes(b'%PDF-export-synthetic')
        result=module.d.dispatch('documents.register',{'project_root':str(target),'source_path':str(source),'coordinates':self.coords,'kind':'drawing','dry_run':False})
        self.assertEqual((target/result['document']['path']).read_bytes(),source.read_bytes())
        self.assertTrue(module.d.dispatch('documents.verify',{'project_root':str(target)})['valid'])

    def test_latest_does_not_resurrect_revision_outside_stage_filter(self):
        old=self.put(); source=self.base/'new-stage.pdf'; source.write_bytes(b'%PDF-new-stage')
        newer=d.register({**self.data,'source_path':str(source),'coordinates':{**self.coords,'stage':'2-build','date':'2026-09-14'},'kind':'drawing','metadata':{'supersedes':old['id']},'dry_run':False})['document']
        self.assertEqual(d.query({**self.data,'filters':{'stage':'1-design','kind':'drawing','latest':True}})['count'],0)
        self.assertEqual(d.query({**self.data,'filters':{'stage':'1-design','kind':'drawing'}})['documents'][0]['id'],old['id'])
        self.assertEqual(d.query({**self.data,'filters':{'stage':'2-build','latest':True}})['documents'][0]['id'],newer['id'])

    def test_receive_and_move_preserve_package_empty_directories(self):
        source=self.base/'package'; (source/'empty/nested').mkdir(parents=True); (source/'files').mkdir(); (source/'files/a.txt').write_text('package data')
        registered=d.register({**self.data,'source_path':str(source),'coordinates':self.coords,'kind':'package','dry_run':False})['document']
        target=self.root/registered['path']; original_dirs=sorted(p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_dir())
        self.assertEqual(sorted(p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_dir()),original_dirs)
        (target/'empty/nested').rmdir()
        self.assertIn('hash_mismatch',[f['code'] for f in d.verify(self.data)['findings']])
        (target/'empty/nested').mkdir()
        moved=d.move({**self.data,'id':registered['id'],'expected_sha256':registered['sha256'],'coordinates':{**self.coords,'phase':'beta'},'dry_run':False})['document']
        self.assertFalse(target.exists()); destination=self.root/moved['path']
        self.assertEqual(sorted(p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_dir()),original_dirs)
        self.assertEqual(d.digest(destination),registered['sha256'])
        self.assertTrue(d.verify(self.data)['valid'])

    def test_empty_package_receive_and_failed_move_restore_directory_tree(self):
        source=self.base/'empty-package'; (source/'empty/nested').mkdir(parents=True)
        row=d.register({**self.data,'source_path':str(source),'coordinates':self.coords,'kind':'package','dry_run':False})['document']
        target=self.root/row['path']; registry=(self.root/'DOCUMENTS.csv').read_bytes()
        os.environ['AS_DOCUMENT_TEST_FAIL_AFTER']='1'
        try:
            with self.assertRaises(OSError): d.move({**self.data,'id':row['id'],'expected_sha256':row['sha256'],'coordinates':{**self.coords,'phase':'beta'},'dry_run':False})
        finally: os.environ.pop('AS_DOCUMENT_TEST_FAIL_AFTER')
        self.assertTrue((target/'empty/nested').is_dir()); self.assertEqual((self.root/'DOCUMENTS.csv').read_bytes(),registry)
        self.assertTrue(d.verify(self.data)['valid'])

    def test_unrelated_package_drift_is_not_blessed_by_move(self):
        source=self.base/'package'; source.mkdir(); (source/'data.txt').write_text('original')
        row=d.register({**self.data,'source_path':str(source),'coordinates':self.coords,'kind':'package','dry_run':False})['document']
        brief=self.put('brief.md',b'Unrelated document\n'); (self.root/row['path']/'data.txt').write_text('external changed bytes')
        before=dict(next(r for r in d.rows_for(self.root) if r['id']==row['id']))
        d.move({**self.data,'id':brief['id'],'expected_sha256':brief['sha256'],'coordinates':{**self.coords,'phase':'beta'},'dry_run':False})
        after=next(r for r in d.rows_for(self.root) if r['id']==row['id']); self.assertEqual(before,after)
        self.assertTrue(any(f['code']=='hash_mismatch' and f['id']==row['id'] for f in d.verify(self.data)['findings']))

    def test_changed_markdown_link_target_is_not_blessed_by_move(self):
        brief=self.put('brief.md',b'Brief\n'); note=self.put('note.md',b'[brief](brief.md)\n')
        (self.root/note['path']).write_text('[brief](brief.md)\nExternally edited\n')
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with self.assertRaises(d.DomainError) as raised: d.move({**self.data,'id':brief['id'],'expected_sha256':brief['sha256'],'coordinates':{**self.coords,'phase':'beta'},'dry_run':False})
        self.assertEqual(raised.exception.code,'conflict')
        self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

if __name__=='__main__': unittest.main()
