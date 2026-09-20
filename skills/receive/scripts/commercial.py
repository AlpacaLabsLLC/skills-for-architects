#!/usr/bin/env python3
"""Commercial context and issued proposal protection on registered documents."""
import hashlib
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

def document(data,kind=None):
    root,info,studio=d.context(data)
    rows=[r for r in d.rows_for(root) if r['id']==data['id']]
    if len(rows)!=1: d.fail('unknown_document','document ID is not registered')
    row=rows[0]
    if kind and row['kind']!=kind: d.fail('wrong_document_kind','expected '+kind)
    if d.digest(d.inside(root,row['path']))!=row['sha256']: d.fail('conflict','document bytes differ from registered hash')
    return root,row

def terms_hash(path):
    text=path.read_text()
    blocks=re.findall(r'<!-- issued-terms:start -->\n?(.*?)\n?<!-- issued-terms:end -->',text,re.S)
    if len(blocks)!=1 or not blocks[0].strip(): d.fail('invalid_proposal','exactly one nonempty issued-terms block required')
    return hashlib.sha256(blocks[0].encode()).hexdigest()

def seal(row):
    sealed=[e for e in json.loads(row['history']) if e.get('terms_sha256')]
    return sealed[-1] if sealed else None

def proposal(verb,data):
    if verb=='create':
        source=Path(data['source_path']); terms_hash(source)
        return d.register({**data,'kind':'proposal','metadata':{**data.get('metadata',{}),'status':'draft'}})
    if verb in ('list','verify'):
        result=d.query({**data,'filters':{'kind':'proposal'}})
        if verb=='list': return result
        findings=[]
        for row in result['documents']:
            try:
                root,checked=document({**data,'id':row['id']},'proposal'); current=terms_hash(d.inside(root,row['path'])); issued=seal(checked)
                if issued and current!=issued['terms_sha256']: d.fail('sealed_terms_changed','issued proposal terms changed')
            except (ValueError,OSError) as e: findings.append({'id':row['id'],'code':getattr(e,'code','io_error'),'message':str(e)})
        return {'findings':findings,'valid':not findings,'changed':False}
    root,row=document(data,'proposal'); sha=terms_hash(d.inside(root,row['path'])); issued=seal(row)
    if issued and issued['terms_sha256']!=sha: d.fail('sealed_terms_changed','issued proposal terms changed')
    if verb=='status': return {'document':row,'terms_sha256':sha,'issued':bool(issued),'changed':False}
    if verb=='send':
        # This records separately evidenced sending. It never sends a message.
        evidence=d.safe_text(data['evidence']); when=d.date_value(data['date'])
        if issued:
            if issued['terms_sha256']==sha and row['status']=='sent': return {'document':row,'changed':False,'sent_by_tool':False}
            d.fail('invalid_lifecycle','proposal already issued; do not manufacture another send')
        if row['status']!='draft': d.fail('invalid_lifecycle','only a draft can first be issued')
        return {**d.update({**data,'expected_sha256':row['sha256'],'changes':{'status':'sent'},'event':{'event':'issued','date':when,'evidence':evidence,'terms_sha256':sha}}),'sent_by_tool':False}
    if verb=='set-status':
        status=data['status']
        if status not in ('accepted','declined','superseded'): d.fail('invalid_lifecycle','supported outcomes: accepted, declined, superseded')
        evidence=d.safe_text(data['evidence']); when=d.date_value(data['date'])
        if row['status']==status: return {'document':row,'changed':False}
        event={'event':status,'date':when,'evidence':evidence}
        if status=='accepted' and not issued: event['terms_sha256']=sha
        return d.update({**data,'expected_sha256':row['sha256'],'changes':{'status':status},'event':event})
    d.fail('unknown_operation','unknown proposal operation')

def agreement_section(text):
    marker='<!-- agreement:start -->'; end='<!-- agreement:end -->'
    if marker in text or end in text:
        match=re.search(re.escape(marker)+r'(.*?)'+re.escape(end),text,re.S)
        if not match or text.count(marker)!=1 or text.count(end)!=1: d.fail('invalid_agreement','malformed agreement section')
        return match.group(0)
    return None

def agreement(verb,data):
    root,_,_=d.context(data); text=d.read_text(root/'PROJECT.md'); existing=agreement_section(text)
    if verb=='verify':
        findings=[]
        if existing:
            for docid in re.findall(r'\bD\d{6,}\b',existing):
                try: document({**data,'id':docid})
                except (ValueError,OSError) as e: findings.append({'id':docid,'message':str(e)})
        return {'present':bool(existing),'valid':not findings,'findings':findings,'changed':False}
    if verb in ('init','promote'):
        if existing: d.fail('collision','agreement context already exists; preserve and update sourced facts explicitly')
        _,row=document(data,'proposal' if verb=='promote' else None)
        if verb=='promote' and (row['status']!='accepted' or not seal(row)): d.fail('invalid_lifecycle','promotion needs accepted issued proposal evidence')
        if verb=='init' and row['kind'] not in ('agreement','contract'): d.fail('wrong_document_kind','agreement init needs an agreement or contract document')
        facts=data.get('facts',[])
        if not isinstance(facts,list): d.fail('invalid_input','facts must be sourced field objects')
        rows=[]
        for fact in facts:
            if set(fact)!={'field','value','source','date'}: d.fail('invalid_input','agreement facts need field, value, source, date')
            for k in ('field','value','source'): d.safe_text(fact[k])
            d.date_value(fact['date']); rows.append('| '+fact['field']+' | '+fact['value']+' | '+fact['source']+' | '+fact['date']+' |')
        section='<!-- agreement:start -->\n## Agreement\n\nGoverning document: '+row['id']+'. Registered SHA-256: '+row['sha256']+'.\n'
        if seal(row): section+='Issued terms SHA-256: '+seal(row)['terms_sha256']+'.\n'
        section+='\n| Field | Value | Source | Date |\n|---|---|---|---|\n'+'\n'.join(rows)+'\n\n### In scope\n\n'+data.get('in_scope','')+'\n\n### Not in scope\n\n'+data.get('not_in_scope','')+'\n\n### Requires SOW\n\n'+data.get('requires_sow','')+'\n\n### Amendments\n\n<!-- agreement:end -->'
        updated=text.rstrip()+'\n\n'+section+'\n'
    elif verb=='record-amendment':
        if not existing: d.fail('missing_agreement','agreement context is absent')
        _,row=document(data)
        if row['kind'] not in ('agreement','contract'): d.fail('wrong_document_kind','amendment must be registered as agreement or contract')
        summary=d.safe_text(data['summary']); when=d.date_value(data['date'])
        line='- '+when+' — '+row['id']+' — '+summary+'\n'
        if line in existing: return {'changed':False,'id':row['id']}
        updated=text.replace(existing,existing.replace('<!-- agreement:end -->',line+'<!-- agreement:end -->'))
    else: d.fail('unknown_operation','unknown agreement operation')
    if not d.dry_run(data): d.commit(root,{'PROJECT.md':updated.encode()})
    return {'document_id':row['id'],'target':'PROJECT.md#agreement','changed':not d.dry_run(data),'dry_run':d.dry_run(data)}

def dispatch(operation,data):
    kind,verb=operation.split('.',1)
    if kind=='proposal': return proposal(verb,data)
    if kind=='agreement': return agreement(verb,data)
    d.fail('unknown_operation','unknown commercial operation')
