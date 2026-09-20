"""Execute every JSON-to-CLI binding on isolated synthetic inputs; no host acceptance."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/runner'))


def load(path):
    specification = importlib.util.spec_from_file_location('fixture_' + path.stem.replace('-', '_'), path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class Bindings(unittest.TestCase):
    def test_all_registered_cli_operations_execute_valid_requests(self):
        with tempfile.TemporaryDirectory(prefix='Arch Studio operation fixtures é ') as temporary:
            work = Path(temporary).resolve(); package = work / 'package'
            shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__', '.DS_Store', 'node_modules'))
            adapter = load(package / 'tools/runner/adapters.py')
            registry = json.loads((package / 'tools/runner/operations.json').read_text())['operations']
            definitions = {row['id']: row for row in registry if row['module'] == 'tools/runner/adapters.py'}
            seen = set()
            def call(operation_id, **request):
                with self.subTest(operation=operation_id):
                    from run import validate
                    validate(request, definitions[operation_id]['input_schema'])
                    result = adapter.dispatch(operation_id, request)
                    seen.add(operation_id)
                    return result
            def save(name, data):
                target = work / name; target.write_text(json.dumps(data)); return str(target)
            project = work / 'project'; project.mkdir(); (project / 'PROJECT.md').write_text('# Synthetic project\n')
            call('dimension_values.normalize', data={'raw':'1 inch','axes':{'W':1},'unit':'in','meaning':'overall'}, unit='mm')
            call('delivery_coverage.assess', data={'expected':['A'], 'entries':[{'item':'A','status':'unresolved','reason':'synthetic'}]})
            call('drawing_quantities.summarize', data=[{'instance_id':'a','document_sha256':'a'*64,'physical_page':1,'bbox':[0,0,10,10],'classification':'instance','reviewed':True,'tag':'A','scope':'Room'}])
            call('schedule_reconcile.compare', data={'left':[],'right':[]})
            lighting = load(ROOT / 'tests/test-lighting-report.py')
            call('lighting_report.build', data=lighting.request([lighting.inventory()]))
            observations = load(ROOT / 'tests/test-product-observations.py')
            call('product_observations.validate', data=observations.observation())
            call('product_observations.validate-batch', data=[observations.observation()])
            call('product_observations.adapt', data={'schema_version':1,'observations':[observations.observation()],'items':[observations.item()],'bindings':[observations.binding()]})
            call('ffe_audit.assess', data={'schema_version':1,'mode':'snapshot','started_at':'2026-09-01T00:00:00Z','items':[observations.item()],'observations':[]})

            preference = call('assistant_preference.preview', target=str(work / 'AGENTS.md'), scope='project', action='enable')
            call('assistant_preference.apply', plan=save('preference.json',preference), approval_digest=preference['plan_sha256'])

            # Every product operation uses the same guarded CSV owner, including array batches.
            common = {'kind':'product','project':str(project)}
            call('product_library.preview', **common, operation='init')
            call('product_library.init', **common, request_id='init', expected_sha256='missing')
            import hashlib
            current = lambda: hashlib.sha256((project / 'product-library.csv').read_bytes()).hexdigest()
            call('product_library.append', **common, row_json=[{'SKU':'A','Tags':'preserve'},{'SKU':'B'}],request_id='append',expected_sha256=current())
            call('product_library.update', **common, row_json={'Lead Time':'7 days'},match_column='SKU',match_value='A',request_id='update',expected_sha256=current())
            call('product_library.status', **common); call('product_library.validate', **common)
            call('product_library.recover', **common, request_id='update')
            imported = work / 'import.csv'; imported.write_bytes((project / 'product-library.csv').read_bytes())
            call('product_library.import', **common, source=str(imported), replace_existing=True,request_id='import',expected_sha256=current())

            call('clip_log.start', project=str(project),request_id='capture',url='https://example.com/synthetic',configuration={'finish':'Blue'})
            call('clip_log.finish', project=str(project),request_id='capture',outcome='blocked')
            call('clip_log.recover', project=str(project),request_id='capture')
            call('clip_log.history', project=str(project),outcome='blocked')

            data={'name':'Synthetic','actor':'Fixture','reason':'Explicit scope','source':{'file':'synthetic.csv'},'items':[{'tag':'A','fields':{'quantity':1}}]}
            adopted=call('ffe_records.adopt',project=str(project),input=save('adopt.json',data)); sid=adopted['schedule_id']
            call('ffe_records.read',project=str(project),schedule=sid,revision=1)
            proposal={'name':'Synthetic','actor':'Fixture','reason':'Explicit update','items':adopted['items']}
            proposal['items'][0]['fields']['quantity']=2
            revised=call('ffe_records.revise',project=str(project),schedule=sid,expected_revision=1,input=save('revise.json',proposal))
            call('ffe_records.reconcile',project=str(project),schedule=sid,base_revision=2,input=save('reconcile.json',{'items':revised['items']}))
            snapshot=call('ffe_records.snapshot',project=str(project),schedule=sid,revision=2,phase='manual')
            call('ffe_records.recover',project=str(project),schedule=sid,snapshot=snapshot['snapshot_id'],destination='recovered.csv',kind='csv')
            call('ffe_records.export',project=str(project),schedule=sid,revision=2,destination='export.csv')

            # Reuse the existing synthetic PDF builder and host-claim fixture builder.
            pdfs=load(ROOT / 'tests/ffe/test_outputs.py')
            template=work/'template.pdf';pdfs.pdf(template,['Synthetic accepted template'])
            design=work/'design.json'
            call('document_contracts.resolve',kind='product-cut-sheet',page='letter',orientation='portrait',measurement_units='metric',output=str(design))
            call('pdf_evidence.extract',input=str(template))
            loc={'document_sha256':'a'*64,'physical_page':1,'annotation_index':0}
            call('pdf_evidence.bind',input=save('link.json',{'annotations':[{**loc,'uri':'https://example.com/synthetic','bbox':[0,0,10,10]}],'locator':loc}))
            intake={'schema_version':1,'mode':'one-off','job_id':'fixture','sources':[{'id':'source','kind':'file','reference':'template.pdf','sha256':None,'status':'available'}],'selected_tags':['A'],'template':None,'record_basis':None,'supersedes':None,'actor':'Fixture','reason':'Synthetic source'}
            call('ffe_intake.prepare',workspace=str(work),input=save('intake.json',intake))
            snapshot={'source':'Synthetic fixture','items':[{'item_id':'one','revision':1,'fields':{'Product':'Synthetic'}}]}
            contract={'schema_version':2,'mode':'one-off','audience':'client','allowed_fields':['Product'],'template_accepted':True,'layout_requirements':['Synthetic Letter page'],'missing_image_policy':'labeled-placeholder','combined_pdf':False,'outputs':[{'tag':'A','item_ids':['one'],'expected_pages':1}]}
            inputs={'input':save('snapshot.json',snapshot),'contract':save('contract.json',contract),'template':str(template),'design':str(design)}
            job=work/'job';call('ffe_outputs.prepare',**inputs,output=str(job))
            artifact=job/'delivery/A.pdf';pdfs.pdf(artifact,['A Synthetic Product image unavailable'])
            manifest=json.loads((job/'internal/manifest.json').read_text())
            inspection={'fingerprint':manifest['fingerprint'],'source_fact_status':'unresolved','unresolved_specifications':['manufacturer confirmation'], 'artifacts':{'A.pdf':{'sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'design_fingerprint':manifest['design']['fingerprint'],'evidence':'Synthetic host claim',**{key:True for key in ('rendered_pages_inspected','layout_matches','images_checked','links_checked','audience_checked','page_geometry_checked','overflow_checked','image_resolution_checked')}}}}
            receipt=job/'internal/receipt.json'
            checked=call('ffe_outputs.check',**inputs,job=str(job),inspection=save('inspection.json',inspection),receipt=str(receipt))
            self.assertEqual(checked['unresolved_specifications'],['manufacturer confirmation']);self.assertFalse(checked['workflowCompleted'])
            call('ffe_outputs.prepare',**inputs,output=str(work/'job-two'))
            call('ffe_outputs.resume',previous=str(job),job=str(work/'job-two'),receipt=str(receipt))
            from PIL import Image
            images=work/'images';images.mkdir();Image.new('RGB',(10,10)).save(images/'source.jpg')
            call('resize_images.resize',folder=str(images),modes=['web'])

            for operation in ('capabilities.write','capabilities.validate','capabilities.check','categories.write-guide','categories.validate','categories.check-guide','namespace.validate','geographic_applicability.validate','host_contracts.validate'):
                call(operation)
            call('geographic_applicability.assess',assessment={'schema_version':1,'component':'skill:nyc-acris','locations':[{'jurisdiction':'jurisdiction:us-ny-nyc','target':'selected-site','origin':'request','status':'resolved','evidence':'Synthetic supplied location'}]})
            host=load(package/'tools/validators/host_contracts.py');catalog=host.load(package)
            component=next(key for key,row in catalog['components'].items() if any(m['mode']=='answer' for m in row['modes']))
            call('host_contracts.assess',component=component,mode='answer',evidence={})
            # The fixture borrows an available Node executable. Production installs use the checksum-pinned binary.
            node=shutil.which('node')
            self.assertIsNotNone(node,'Node required for source adapter engineering checks')
            fixture_install=work/'fixture-node';(fixture_install/'node/bin').mkdir(parents=True)
            (fixture_install/'node/bin/node').symlink_to(node)
            lock=package/'tools/runner/runtime-lock.json';lock_data=json.loads(lock.read_text());lock_data['node']=subprocess.check_output([node,'--version'],text=True).strip().removeprefix('v');lock.write_text(json.dumps(lock_data))
            from unittest.mock import patch
            with patch.dict(os.environ,{'AS_LOCAL_INSTALLATION':str(fixture_install)}):
                call('source_health.validate')
                source_catalog=json.loads((package/'corpus/sources/catalog.json').read_text())
                pointer=next(s['id'] for s in source_catalog['sources'] if s['identity'] is None)
                call('source_health.check',sources=[pointer])
            self.assertEqual(seen,set(definitions),'Every retained JSON-to-CLI binding must execute a valid fixture')


if __name__=='__main__':unittest.main()
