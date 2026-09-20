#!/usr/bin/env python3
"""Current CSV record owners. No Markdown import or inferred commercial facts."""
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys

# Import shared code by exact packaged path AND bytes; persistent hosts must not
# reuse a sibling from another installed release through sys.modules['documents'].
import importlib.util
import hashlib
_module_path=Path(__file__).with_name('documents.py')
_module_key='_as_documents_'+hashlib.sha256(str(_module_path.resolve()).encode()+_module_path.read_bytes()).hexdigest()
if _module_key not in sys.modules:
    _spec=importlib.util.spec_from_file_location(_module_key,_module_path)
    _module=importlib.util.module_from_spec(_spec); sys.modules[_module_key]=_module; _spec.loader.exec_module(_module)
d=sys.modules[_module_key]

def number(value,positive=False):
    try: n=Decimal(str(value))
    except InvalidOperation: d.fail('invalid_number','explicit finite decimal required')
    if not n.is_finite() or (positive and n<=0): d.fail('invalid_number','explicit positive finite decimal required')
    return n

def register(data,kind):
    root,info,studio=d.context(data); owner=root
    name={'tasks':'TASKS.csv','time':'TIME.csv','invoice':'INVOICES.csv'}[kind]
    if kind=='tasks' and studio:
        settings=d.fields((studio/'STUDIO.md').read_text())
        if settings['Task register']=='portfolio': owner=studio
    rows=d.read_csv(d.inside(owner,name),d.REGISTERS[name])
    if kind=='tasks':
        valid_ids={info['Project ID']} if owner==root else {row['Project ID'] for row in d.table(d.read_text(owner/'STUDIO.md'),'projects')}
        if any(row['project_id'] not in valid_ids for row in rows): d.fail('invalid_register','task refers to an unregistered project')
    return root,owner,info,name,rows

def validate_rows(rows,kind,project_id=None):
    prefix={'tasks':'T','time':'E','invoice':'I'}[kind]; seen=set()
    for row in rows:
        if not re.fullmatch(prefix+r'\d{4,}',row['id']) or row['id'] in seen: d.fail('invalid_register','invalid or duplicate permanent ID')
        seen.add(row['id'])
        if kind=='tasks':
            if row['status'] not in ('open','in-progress','blocked','completed','cancelled'): d.fail('invalid_register','invalid task status')
            for k in ('created','updated'): d.date_value(row[k])
            for k in ('due','completed','cancelled'):
                if row[k]: d.date_value(row[k])
            if not row['project_id'] or not row['description'] or not row['source']: d.fail('invalid_register','task identity/provenance incomplete')
            if row['status']=='completed' and not row['completed'] or row['status']=='cancelled' and not row['cancelled']: d.fail('invalid_register','task closure date missing')
            try:
                if not isinstance(json.loads(row['history']),list): raise ValueError()
            except ValueError: d.fail('invalid_register','invalid task history')
        elif kind=='time':
            d.date_value(row['date']); number(row['hours'],True)
            if not row['description'] or not row['sources']: d.fail('invalid_register','time provenance incomplete')
            try:
                sources=json.loads(row['sources'])
                if not isinstance(sources,list) or not sources or any(not isinstance(v,str) or not v for v in sources): raise ValueError()
            except ValueError: d.fail('invalid_register','invalid time sources JSON')
        else:
            for key in ('base','expenses','total'): number(row[key])
            if number(row['base'])+number(row['expenses'])!=number(row['total']): d.fail('invalid_register','invoice total mismatch')
            if row['status'] not in ('draft','sent','paid','void'): d.fail('invalid_register','invalid invoice status')
            for key in ('period_start','period_end'): d.date_value(row[key])
            for key in ('sent','paid'):
                if row[key]: d.date_value(row[key])
            if not row['currency'] or not row['invoice_number']: d.fail('invalid_register','invoice identity/currency missing')
            try:
                if not isinstance(json.loads(row['history']),list): raise ValueError()
            except ValueError: d.fail('invalid_register','invalid invoice history JSON')

def source(value,root):
    d.safe_text(value)
    if re.fullmatch(r'conversation:\d{4}-\d{2}-\d{2}#instruction-\d+',value): d.date_value(value.split(':')[1].split('#')[0]); return value
    if re.fullmatch(r'D\d{6,}#[^\s]+',value):
        if value.split('#')[0] not in {r['id'] for r in d.rows_for(root)}: d.fail('invalid_source','source document ID is not registered')
        return value
    d.fail('invalid_source','source must be registered document ID#item or exact conversation instruction token')

def next_id(rows,kind):
    return {'tasks':'T','time':'E','invoice':'I'}[kind]+str(max([int(r['id'][1:]) for r in rows],default=0)+1).zfill(4)

def task(verb,data):
    root,owner,info,name,rows=register(data,'tasks'); validate_rows(rows,'tasks'); project_id=info['Project ID']
    selected=[r for r in rows if r['project_id']==project_id]
    if verb=='list': return {'tasks':selected,'project_id':project_id,'register':str(owner/name),'changed':False}
    when=d.date_value(data.get('date',d.today()))
    if verb=='add':
        values=data['task']; provenance=source(values['source'],root)
        duplicates=[r for r in selected if r['source']==provenance]
        if duplicates and not data.get('distinct_reason'): d.fail('duplicate_source','source already belongs to '+duplicates[0]['id']+'; link/update or supply user-confirmed distinct_reason')
        row={k:'' for k in d.TASK_FIELDS}; row.update(id=next_id(rows,'tasks'),project_id=project_id,description=d.safe_text(values['description']),owner=values.get('owner','Unassigned'),due=values.get('due',''),status='open',created=when,updated=when,source=provenance,related=values.get('related',''),history=d.json_text([{'event':'created','date':when,'distinct_reason':data.get('distinct_reason','')}]))
        rows.append(row)
    else:
        matches=[r for r in selected if r['id']==data['id']]
        if len(matches)!=1: d.fail('unknown_task','task ID not in selected project')
        row=matches[0]; before=dict(row)
        if verb=='update':
            changes=data['changes']
            if set(changes)-{'description','owner','due','related','status'}: d.fail('immutable_field','routine update cannot change identity, provenance or closure dates')
            if changes.get('status') in ('completed','cancelled'): d.fail('invalid_lifecycle','use explicit lifecycle operation')
            if row['status'] in ('completed','cancelled') and changes.get('status',row['status'])!=row['status']: d.fail('invalid_lifecycle','use explicit reopen operation')
            row.update(changes)
        elif verb in ('complete','cancel','reopen'):
            status={'complete':'completed','cancel':'cancelled','reopen':'open'}[verb]
            if row['status']==status: return {'task':row,'changed':False}
            if verb=='complete' and row['status']=='cancelled': d.fail('invalid_lifecycle','reopen cancelled task first')
            if verb in ('cancel','reopen'): d.safe_text(data['reason'])
            row['status']=status
            if verb!='reopen': row[status]=when
        else: d.fail('unknown_operation','unknown task operation')
        row['updated']=when; history=json.loads(row['history']); history.append({'event':verb,'date':when,'before':{k:v for k,v in before.items() if k!='history'},'reason':data.get('reason','')}); row['history']=d.json_text(history)
    validate_rows(rows,'tasks')
    if not d.dry_run(data): d.commit(owner,{name:d.csv_bytes(rows,d.TASK_FIELDS)})
    return {'task':row,'changed':not d.dry_run(data),'dry_run':d.dry_run(data)}

def time(verb,data):
    root,owner,info,name,rows=register(data,'time'); validate_rows(rows,'time')
    if verb=='list': return {'entries':rows,'changed':False}
    if verb!='append': d.fail('unknown_operation','time supports list and append only')
    values=data['entry']; date=d.date_value(values['date']); hours=str(number(values['hours'],True))
    sources=values['sources']
    if not isinstance(sources,list) or not sources: d.fail('invalid_source','at least one source required')
    for s in sources: source(s,root)
    correction=values.get('correction','')
    if correction and correction not in {r['id'] for r in rows}: d.fail('invalid_correction','original time ID does not exist')
    row={'id':next_id(rows,'time'),'date':date,'hours':hours,'description':d.safe_text(values['description']),'sources':d.json_text(sources),'correction':correction}
    # An exact repeated approved append is an idempotent result, not a new duration.
    for old in rows:
        if all(old[k]==v for k,v in row.items() if k!='id'): return {'entry':old,'changed':False}
    if not d.dry_run(data): d.commit(owner,{name:d.csv_bytes(rows+[row],d.TIME_FIELDS)})
    return {'entry':row,'changed':not d.dry_run(data),'dry_run':d.dry_run(data)}

def invoice(verb,data):
    root,owner,info,name,rows=register(data,'invoice'); validate_rows(rows,'invoice')
    if verb=='allocate': return {'id':next_id(rows,'invoice'),'changed':False}
    if verb=='status':
        totals={}
        for row in rows:
            if row['status']=='void': continue
            totals[row['currency']]=str(number(totals.get(row['currency'],'0'))+number(row['total']))
        return {'invoices':rows,'totals_by_currency':totals,'changed':False,'billing_inferred':False}
    if verb=='init': return {'register':name,'changed':False,'already_created_by_project_setup':True}
    if verb=='append':
        values=data['invoice']; row={k:'' for k in d.INVOICE_FIELDS}; row.update({k:str(v) for k,v in values.items()})
        if set(values)-set(d.INVOICE_FIELDS) or 'id' in values or 'history' in values: d.fail('invalid_input','unknown or immutable invoice field')
        row.update(id=next_id(rows,'invoice'),status=values.get('status','draft'),history=d.json_text([{'event':'created','date':d.today()}]))
        for key in ('invoice_number','currency'): d.safe_text(row[key])
        for key in ('period_start','period_end'): d.date_value(row[key])
        if row['period_end']<row['period_start']: d.fail('invalid_period','invoice period is reversed')
        for key in ('sent','paid'):
            if row[key]: d.date_value(row[key])
        if row['status']=='paid' and not row['paid']: d.fail('invalid_lifecycle','paid status requires explicit payment date')
        if row['status']=='sent' and not row['sent']: d.fail('invalid_lifecycle','sent status requires explicit sent date')
        if row['correction'] and row['correction'] not in {r['id'] for r in rows}: d.fail('invalid_correction','unknown correction target')
        if row['document_id'] and row['document_id'] not in {r['id'] for r in d.rows_for(root)}: d.fail('invalid_source','invoice document is not registered')
        for old in rows:
            if old['invoice_number']==row['invoice_number']:
                if all(old[k]==v for k,v in row.items() if k not in ('id','history')): return {'invoice':old,'changed':False}
                d.fail('duplicate_invoice','invoice number already exists; correction needs a distinct identity')
        rows.append(row)
    elif verb=='set-lifecycle':
        matches=[r for r in rows if r['id']==data['id']]
        if len(matches)!=1: d.fail('unknown_invoice','invoice ID absent')
        row=matches[0]; event=data['event']; when=d.date_value(data['date'])
        if event not in ('sent','paid','void'): d.fail('invalid_lifecycle','unsupported invoice lifecycle')
        if row['status']=='void' and event!='void': d.fail('invalid_lifecycle','void invoice cannot change lifecycle')
        if row['status']==event and (event=='void' or row[event]==when): return {'invoice':row,'changed':False}
        if event=='sent' and row['status']=='paid': d.fail('invalid_lifecycle','cannot move paid invoice back to sent')
        before=row['status']; row['status']=event
        if event!='void': row[event]=when
        history=json.loads(row['history']); history.append({'event':event,'date':when,'before':before}); row['history']=d.json_text(history)
    else: d.fail('unknown_operation','unknown invoice operation')
    validate_rows(rows,'invoice')
    if not d.dry_run(data): d.commit(owner,{name:d.csv_bytes(rows,d.INVOICE_FIELDS)})
    return {'invoice':row,'changed':not d.dry_run(data),'dry_run':d.dry_run(data)}

def dispatch(operation,data):
    kind,verb=operation.split('.',1)
    if kind=='tasks': return task(verb,data)
    if kind=='time': return time(verb,data)
    if kind=='invoice': return invoice(verb,data)
    d.fail('unknown_operation','unknown record operation')
