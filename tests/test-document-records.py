import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/receive/scripts'))
import documents as d
import workspaces as w
d=w.d
import records as r
import commercial as c

class Records(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.base=Path(self.tmp.name).resolve(); self.root=self.base/'project'
        w.project_init({'target':str(self.root),'name':'Example','project_id':'P1','kind':'initiative','type':'internal','status':'on-hold','client_code':'INT','client':'Internal','vocabularies':{'phases':['main'],'scopes':['operations'],'originators':['firm']},'dry_run':False})
        self.data={'project_root':str(self.root),'dry_run':False}; self.source='conversation:2026-09-13#instruction-1'
        self.coords={'phase':'main','stage':'0-plan','scope':'operations','originator':'firm','date':'2026-09-13'}
    def tearDown(self): self.tmp.cleanup()
    def test_task_history_source_duplicates_and_reopen(self):
        first=r.dispatch('tasks.add',{**self.data,'task':{'description':'Review candidate','source':self.source}})['task']
        with self.assertRaises(d.DomainError): r.dispatch('tasks.add',{**self.data,'task':{'description':'Again','source':self.source}})
        finished=r.dispatch('tasks.complete',{**self.data,'id':first['id'],'date':'2026-09-13'})['task']
        reopened=r.dispatch('tasks.reopen',{**self.data,'id':first['id'],'date':'2026-09-14','reason':'New evidence'})['task']
        self.assertEqual(reopened['completed'],finished['completed']); self.assertEqual(reopened['source'],first['source']); self.assertEqual(len(json.loads(reopened['history'])),3)
        with self.assertRaises(d.DomainError): r.dispatch('tasks.update',{**self.data,'id':first['id'],'changes':{'created':'2020-01-01'}})
    def test_time_repeats_and_corrections_are_append_only(self):
        entry={'date':'2026-09-13','hours':'1.25','description':'Reviewed candidate','sources':[self.source]}
        first=r.dispatch('time.append',{**self.data,'entry':entry})['entry']
        self.assertFalse(r.dispatch('time.append',{**self.data,'entry':entry})['changed'])
        correction=r.dispatch('time.append',{**self.data,'entry':{**entry,'hours':'1.5','correction':first['id']}})['entry']
        rows=r.dispatch('time.list',self.data)['entries']; self.assertEqual(rows[0],first); self.assertEqual(rows[1]['correction'],first['id'])
        with self.assertRaises(d.DomainError): r.dispatch('time.append',{**self.data,'entry':{**entry,'hours':'NaN'}})
    def test_invoice_arithmetic_and_explicit_lifecycle(self):
        values={'invoice_number':'2026-01','period_start':'2026-09-01','period_end':'2026-09-30','currency':'USD','base':'10.10','expenses':'0.20','total':'10.30'}
        first=r.dispatch('invoice.append',{**self.data,'invoice':values})['invoice']
        self.assertFalse(r.dispatch('invoice.append',{**self.data,'invoice':values})['changed'])
        paid=r.dispatch('invoice.set-lifecycle',{**self.data,'id':first['id'],'event':'paid','date':'2026-09-13'})['invoice']
        self.assertEqual(paid['paid'],'2026-09-13'); self.assertEqual(r.dispatch('invoice.status',self.data)['totals_by_currency'],{'USD':'10.30'})
        before=(self.root/'INVOICES.csv').read_bytes()
        with self.assertRaises(d.DomainError): r.dispatch('invoice.append',{**self.data,'invoice':{**values,'invoice_number':'2026-02','total':'10.31'}})
        self.assertEqual(before,(self.root/'INVOICES.csv').read_bytes())
    def test_direct_acceptance_seals_terms_and_agreement_cites_id(self):
        source=self.base/'proposal.md'; source.write_text('# Offer\n\n<!-- issued-terms:start -->\nScope: a synthetic example.\n<!-- issued-terms:end -->\n')
        row=c.dispatch('proposal.create',{**self.data,'source_path':str(source),'coordinates':self.coords})['document']
        accepted=c.dispatch('proposal.set-status',{**self.data,'id':row['id'],'status':'accepted','date':'2026-09-13','evidence':self.source})['document']
        self.assertTrue(c.seal(accepted))
        c.dispatch('agreement.promote',{**self.data,'id':row['id'],'facts':[{'field':'Fee','value':'Explicit USD 10','source':row['id'],'date':'2026-09-13'}],'in_scope':'- Example scope ('+row['id']+').' })
        text=(self.root/'PROJECT.md').read_text(); self.assertIn('## Agreement',text); self.assertIn(row['id'],text)
        self.assertTrue(c.dispatch('agreement.verify',self.data)['valid'])
        p=self.root/row['path']; p.write_text(p.read_text().replace('a synthetic example','changed terms'))
        self.assertFalse(c.dispatch('proposal.verify',self.data)['valid'])
    def test_malformed_register_preserved(self):
        p=self.root/'TASKS.csv'; p.write_text('id,wrong\nT0001,value\n'); before=p.read_bytes()
        with self.assertRaises(d.DomainError): r.dispatch('tasks.add',{**self.data,'task':{'description':'Action','source':self.source}})
        self.assertEqual(before,p.read_bytes())

    def test_task_update_cancel_and_document_sources(self):
        source=self.base/'minutes.md'; source.write_text('# Minutes\n\n## T1\nAn explicit proposed action.\n')
        doc=d.register({**self.data,'source_path':str(source),'coordinates':self.coords,'kind':'meeting'})['document']
        first=r.dispatch('tasks.add',{**self.data,'task':{'description':'Review','source':doc['id']+'#T1'}})['task']
        changed=r.dispatch('tasks.update',{**self.data,'id':first['id'],'changes':{'owner':'Review lead','due':'2026-09-15'}})['task']
        self.assertEqual(changed['source'],first['source']); self.assertEqual(changed['owner'],'Review lead')
        cancelled=r.dispatch('tasks.cancel',{**self.data,'id':first['id'],'reason':'Explicitly superseded','date':'2026-09-14'})['task']
        self.assertEqual(cancelled['cancelled'],'2026-09-14'); self.assertEqual(r.dispatch('tasks.list',self.data)['tasks'][0]['id'],first['id'])

    def test_proposal_send_and_direct_agreement_amendment(self):
        source=self.base/'proposal.md'; source.write_text('# Proposal\n<!-- issued-terms:start -->\nSynthetic terms\n<!-- issued-terms:end -->\n')
        row=c.dispatch('proposal.create',{**self.data,'source_path':str(source),'coordinates':self.coords})['document']
        issued=c.dispatch('proposal.send',{**self.data,'id':row['id'],'date':'2026-09-13','evidence':'synthetic delivery receipt'})
        self.assertFalse(issued['sent_by_tool']); self.assertTrue(c.dispatch('proposal.status',{**self.data,'id':row['id']})['issued'])
        self.assertEqual(c.dispatch('proposal.list',self.data)['count'],1)
        self.assertFalse(c.dispatch('proposal.send',{**self.data,'id':row['id'],'date':'2026-09-13','evidence':'synthetic delivery receipt'})['changed'])
        contract=self.base/'contract.md'; contract.write_text('# Direct engagement\nExplicit synthetic governing terms.\n')
        governing=d.register({**self.data,'source_path':str(contract),'coordinates':self.coords,'kind':'contract'})['document']
        c.dispatch('agreement.init',{**self.data,'id':governing['id']})
        amendment=self.base/'amendment.md'; amendment.write_text('# Amendment\nExplicit synthetic change.\n')
        amended=d.register({**self.data,'source_path':str(amendment),'coordinates':self.coords,'kind':'agreement'})['document']
        args={**self.data,'id':amended['id'],'summary':'Synthetic agreed change','date':'2026-09-14'}
        c.dispatch('agreement.record-amendment',args); self.assertFalse(c.dispatch('agreement.record-amendment',args)['changed'])
        self.assertTrue(c.dispatch('agreement.verify',self.data)['valid'])

    def test_invoice_read_operations_and_register_mode_preservation(self):
        path=self.root/'INVOICES.csv'; path.chmod(0o600)
        before=path.read_bytes(); self.assertFalse(r.dispatch('invoice.init',self.data)['changed']); self.assertEqual(r.dispatch('invoice.allocate',self.data)['id'],'I0001'); self.assertEqual(before,path.read_bytes())
        r.dispatch('invoice.append',{**self.data,'invoice':{'invoice_number':'1','period_start':'2026-09-01','period_end':'2026-09-30','currency':'USD','base':'1','expenses':'0','total':'1'}})
        self.assertEqual(path.stat().st_mode & 0o777,0o600)

    def test_moves_never_rewrite_accepted_proposal_or_its_sealed_links(self):
        w.vocab({**self.data,'axis':'phase','action':'add','value':'other'})
        brief=self.base/'brief.md'; brief.write_text('# Brief\n')
        brief_row=d.register({**self.data,'source_path':str(brief),'coordinates':self.coords,'kind':'brief'})['document']
        source=self.base/'proposal.md'; source.write_text('# Offer\n<!-- issued-terms:start -->\n[Brief](brief.md) is part of scope.\n<!-- issued-terms:end -->\n')
        proposal=c.dispatch('proposal.create',{**self.data,'source_path':str(source),'coordinates':self.coords})['document']
        c.dispatch('proposal.set-status',{**self.data,'id':proposal['id'],'status':'accepted','date':'2026-09-13','evidence':self.source})
        c.dispatch('agreement.promote',{**self.data,'id':proposal['id']})
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for row in (brief_row,proposal):
            for preview in (True,False):
                with self.assertRaises(d.DomainError) as raised:
                    d.move({**self.data,'id':row['id'],'expected_sha256':row['sha256'],'coordinates':{**self.coords,'phase':'other'},'dry_run':preview})
                self.assertEqual(raised.exception.code,'sealed_reference_conflict')
                self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertTrue(c.dispatch('proposal.verify',self.data)['valid']); self.assertTrue(d.verify(self.data)['valid'])
        # Moving both records together keeps the relative sealed link unchanged.
        w.vocab({**self.data,'axis':'phase','action':'rename','old':'main','value':'renamed'})
        self.assertTrue(c.dispatch('proposal.verify',self.data)['valid']); self.assertTrue(d.verify(self.data)['valid'])
        after=next(row for row in d.rows_for(self.root) if row['id']==proposal['id'])
        self.assertEqual(after['sha256'],proposal['sha256']); self.assertEqual((self.root/after['path']).read_bytes(),before[Path(proposal['path'])])

if __name__=='__main__': unittest.main()
