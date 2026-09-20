#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - "${AS_FFE_INTAKE_TEST_ROOT:-.}" <<'PY'
import copy
import importlib.util
from pathlib import Path
import tempfile
import sys
import subprocess
import json

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
plugin=Path(sys.argv[1]).resolve()
records=module('record_contract',plugin/'tools/workspace/ffe_records.py')
intake=module('intake_contract',plugin/'tools/transformers/ffe_intake.py')
def files(root):
    return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
def refuses(root,callback):
    before=files(root)
    try: callback()
    except (ValueError,OSError,TypeError): pass
    else: raise AssertionError('invalid intake accepted')
    assert files(root)==before,'failed intake mutated project files'
with tempfile.TemporaryDirectory(prefix='as-ffe-intake-') as temporary:
    root=Path(temporary).resolve();project=root/'project';project.mkdir()
    (project/'PROJECT.md').write_text('# Synthetic intake project\n')
    (project/'source.pdf').write_bytes(b'Synthetic input evidence; not a real PDF.')
    record=records.write_revision(project,dict(name='Appliances',actor='Test',reason='Explicit adoption',items=[dict(tag='AP-01',fields={'model':'Synthetic'})]))
    original_records=files(project/'ffe')
    base=dict(schema_version=1,mode='adopted',job_id='accepted',sources=[dict(id='source',kind='file',reference='source.pdf',sha256=None,status='available')],selected_tags=['AP-01'],template=None,record_basis={k:record[k] for k in ('schedule_id','revision','hash')},supersedes=None,actor='Tester',reason='Accepted source')
    result=intake.manifest(project,base)
    assert result['adoption_performed'] is False
    for name,data in original_records.items(): assert (project/'ffe'/name).read_bytes()==data
    assert records.read_schedule(project,record['schedule_id'])==record
    refuses(project,lambda:intake.manifest(project,base))
    for mutate in [lambda d:d['record_basis'].update(hash='0'*64),
                   lambda d:d['record_basis'].update(revision=True),
                   lambda d:d.update(selected_tags=['AP-02']),
                   lambda d:d.update(mode='one-off'),
                   lambda d:d['sources'][0].update(sha256='0'*64),
                   lambda d:d['sources'][0].update(reference='../source.pdf'),
                   lambda d:d.update(supersedes='missing-job')]:
        candidate=copy.deepcopy(base);candidate['job_id']='refused';mutate(candidate)
        refuses(project,lambda:intake.manifest(project,candidate))
    symlink=root/'linked-project';symlink.symlink_to(project,target_is_directory=True)
    refuses(project,lambda:intake.manifest(symlink,dict(base,job_id='linked')))
    (project/'linked-source.pdf').symlink_to(project/'source.pdf')
    candidate=copy.deepcopy(base);candidate['job_id']='linked-source';candidate['sources'][0]['reference']='linked-source.pdf'
    refuses(project,lambda:intake.manifest(project,candidate))
    other=root/'other';other.mkdir();(other/'PROJECT.md').write_text('# Other\n');(other/'source.pdf').write_bytes(b'Synthetic')
    refuses(other,lambda:intake.manifest(other,base))
    correction=copy.deepcopy(base);correction.update(job_id='correction',supersedes='accepted',reason='Explicit scope correction')
    assert intake.manifest(project,correction)['path']=='ffe/jobs/correction/input-manifest.json'
    prior=project/'ffe/jobs/accepted/input-manifest.json'
    saved=prior.read_bytes()
    for corrupt in [b'not JSON', saved.replace(b'Accepted source',b'Tampered source')]:
        prior.write_bytes(corrupt)
        broken=copy.deepcopy(correction);broken['job_id']='corrupt-lineage'
        refuses(project,lambda:intake.manifest(project,broken))
    prior.write_bytes(saved)
    oneoff=copy.deepcopy(base);oneoff.update(mode='one-off',record_basis=None,job_id='one-off')
    assert intake.manifest(project,oneoff)['adoption_performed'] is False
    standalone=root/'samples';standalone.mkdir();(standalone/'source.pdf').write_bytes(b'Sample source')
    sample=copy.deepcopy(oneoff);sample['job_id']='sample'
    refuses(standalone,lambda:intake.manifest(standalone,sample))
    assert intake.manifest(standalone,sample,standalone=True)['adoption_performed'] is False
    assert not (standalone/'PROJECT.md').exists()
    assert not (standalone/'STUDIO.md').exists()
    refuses(standalone,lambda:intake.manifest(standalone,sample,standalone=True))
    refuses(standalone,lambda:intake.manifest(standalone,base,standalone=True))
    cli_sample=copy.deepcopy(sample);cli_sample['job_id']='cli-sample'
    cli_input=root/'intake.json';cli_input.write_text(json.dumps(cli_sample))
    command=[sys.executable,str(plugin/'tools/transformers/ffe_intake.py'),'--workspace',str(standalone),'--input',str(cli_input)]
    receipt=subprocess.run(command,check=True,capture_output=True,text=True)
    assert json.loads(receipt.stdout)['mode']=='one-off'
    cli_input.write_text(json.dumps(base))
    assert subprocess.run(command,capture_output=True).returncode==2
    assert subprocess.run(command+['--project',str(project)],capture_output=True).returncode==2
    for change in [dict(reference='../source.pdf'),dict(sha256='0'*64)]:
        invalid=copy.deepcopy(sample);invalid['job_id']='invalid';invalid['sources'][0].update(change)
        refuses(standalone,lambda:intake.manifest(standalone,invalid,standalone=True))
print('PASS adopted intake dynamic import, canonical hash/tag binding, foreign/symlink refusal, immutable corrections, one-off isolation')
PY
