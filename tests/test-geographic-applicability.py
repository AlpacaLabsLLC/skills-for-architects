"""Supplied-context routing checks only; no external source or legal verification."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('geography', ROOT / 'tools/validators/geographic_applicability.py')
geo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(geo)


def location(jurisdiction='jurisdiction:us-ny-nyc', origin='request', status='resolved'):
    return {'jurisdiction': jurisdiction, 'target': 'selected-site', 'origin': origin,
            'status': status, 'evidence': 'Synthetic supplied location; not geocoded'}


class GeographicApplicability(unittest.TestCase):
    def setUp(self):
        self.catalog = geo.load(ROOT)

    def request(self, component='skill:nyc-acris', **fields):
        return {'schema_version': 1, 'component': component, 'locations': [location()], **fields}

    def assess(self, request):
        result = geo.assess(self.catalog, request, ROOT)
        self.assertFalse(result['execution_verified'])
        self.assertFalse(result['evidence_authenticated'])
        self.assertEqual(result['legal_applicability'], 'unverified')
        return result

    def test_every_registered_skill_and_tool_is_explicit(self):
        inventory = json.loads((ROOT / 'corpus/components.json').read_text())
        expected = {c['id'] for c in inventory['components'] if c['category'] in ('skills', 'tools')}
        self.assertEqual(set(self.catalog['components']), expected)
        self.assertEqual(geo.validate(self.catalog, ROOT)['components'], len(expected))

    def test_catalog_is_closed_and_rejects_missing_unknown_or_unsafe_declarations(self):
        for mutate in [lambda d: d.update(grants_execution=True),
                       lambda d: d['components'].pop('skill:nyc-acris'),
                       lambda d: d['components'].update({'skill:invented': 'portable'}),
                       lambda d: d['components'].update({'skill:nyc-acris': 'worldwide'}),
                       lambda d: d['references'][0].update(path='../outside')]:
            document = copy.deepcopy(self.catalog)
            mutate(document)
            with self.assertRaises(ValueError):
                geo.validate(document, ROOT)

    def test_one_off_nyc_requires_no_project_or_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            before = list(Path(directory).iterdir())
            result = subprocess.run([sys.executable, str(ROOT / 'tools/validators/geographic_applicability.py'),
                                     '--root', str(ROOT), '--assess'], input=json.dumps(self.request()),
                                    cwd=directory, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'procedure-supported')
            self.assertEqual(list(Path(directory).iterdir()), before)

    def test_explicit_non_nyc_never_uses_nyc_procedure_even_with_identifier(self):
        for jurisdiction in ['jurisdiction:us-ma-boston', 'jurisdiction:uy-montevideo']:
            result = self.assess(self.request(locations=[location(jurisdiction)], identifier='1000770001'))
            self.assertEqual(result['status'], 'unsupported')

    def test_missing_ambiguous_and_studio_only_locations_require_context(self):
        for locations in [[], [location(status='ambiguous')], [location(origin='studio-default')],
                          [location('jurisdiction:us-ny')]]:
            self.assertEqual(self.assess(self.request(locations=locations))['status'], 'context-required')

    def test_conflicting_project_and_request_targets_require_resolution(self):
        locations = [location(), location('jurisdiction:us-ma-boston', origin='project')]
        self.assertEqual(self.assess(self.request(locations=locations))['status'], 'context-required')
        second = location(origin='project')
        second['target'] = 'different-site'
        self.assertEqual(self.assess(self.request(locations=[location(), second]))['status'], 'context-required')

    def test_studio_default_cannot_override_one_off_site(self):
        locations = [location(origin='studio-default'), location('jurisdiction:uy-montevideo')]
        self.assertEqual(self.assess(self.request(locations=locations))['status'], 'unsupported')

    def test_portable_methods_and_general_research_do_not_inherit_nyc_cluster_scope(self):
        self.assertEqual(self.assess(self.request('skill:workplace-programmer', locations=[]))['status'], 'procedure-supported')
        for component in ['environmental-analysis', 'mobility-analysis', 'demographics-analysis', 'site-history']:
            result = self.assess(self.request('skill:' + component, locations=[location('jurisdiction:uy-montevideo')]))
            self.assertEqual(result['status'], 'procedure-supported')
            self.assertEqual(result['source_verification'], 'required')

    def test_regulatory_route_requires_material_date_use_and_work_scope(self):
        complete = self.request('skill:zoning-analysis-nyc', as_of='2026-09-07', use='office', work_scope='new building')
        for field in ['as_of', 'use', 'work_scope']:
            request = dict(complete)
            request.pop(field)
            self.assertEqual(self.assess(request)['status'], 'context-required')
        self.assertEqual(self.assess(complete)['status'], 'procedure-supported')
        self.assertEqual(self.assess(complete)['source_verification'], 'required')

    def test_non_us_occupancy_requires_supplied_local_table(self):
        request = self.request('skill:occupancy-calculator', locations=[location('jurisdiction:uy-montevideo')],
                               as_of='2026-09-07', use='office', work_scope='occupant load')
        self.assertEqual(self.assess(request)['status'], 'context-required')
        request['local_rule_reference'] = 'Supplied local table, exact section retained by host'
        self.assertEqual(self.assess(request)['status'], 'procedure-supported')
        self.assertEqual(self.assess(request)['source_verification'], 'required')

    def test_material_fields_are_conditional_for_general_research(self):
        request = self.request('skill:environmental-analysis', material_fields=['as_of'])
        self.assertEqual(self.assess(request)['status'], 'context-required')
        request['as_of'] = '2024-03-01'
        self.assertEqual(self.assess(request)['status'], 'procedure-supported')

    def test_explicit_material_context_also_applies_to_portable_methods(self):
        request = self.request('skill:workplace-programmer', locations=[], material_fields=['use'])
        self.assertEqual(self.assess(request)['status'], 'context-required')
        request['use'] = 'office'
        self.assertEqual(self.assess(request)['status'], 'procedure-supported')

    def test_cli_rejections_do_not_echo_supplied_evidence(self):
        for raw in ['not-json PRIVATE-SITE', json.dumps(self.request(locations=[])),
                    json.dumps(self.request(locations=[location('jurisdiction:uy-montevideo')])),
                    'PRIVATE-SITE' * 7000]:
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/validators/geographic_applicability.py'),
                                     '--root', str(ROOT), '--assess'], input=raw,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('PRIVATE-SITE', result.stdout + result.stderr)

    def test_renderer_keeps_explicit_unknown_report_date(self):
        request = self.request('skill:zoning-envelope', locations=[location(origin='input-report')],
                               input_report={'locator': 'supplied.md', 'as_of': None,
                                             'limitations': ['Date and legal applicability unknown']})
        result = self.assess(request)
        self.assertEqual(result['status'], 'procedure-supported')
        self.assertEqual(result['input_report'], request['input_report'])

    def test_renderer_preserves_report_context_without_revalidating_law(self):
        request = self.request('skill:zoning-envelope', locations=[location(origin='input-report')])
        self.assertEqual(self.assess(request)['status'], 'context-required')
        request['input_report'] = {'locator': 'supplied-envelope.md', 'as_of': '2024-01-01',
                                   'limitations': ['Source applicability unverified', 'Existing report approximation']}
        result = self.assess(request)
        self.assertEqual(result['status'], 'procedure-supported')
        self.assertEqual(result['input_report'], request['input_report'])

    def test_unknown_date_location_or_execution_claims_do_not_sneak_through(self):
        for patch in [{'as_of': '2023-02-29'}, {'as_of': 'now'}, {'legal_applicability': 'verified'},
                      {'locations': [{'jurisdiction': 'New York'}]}, {'component': 'skill:invented'}]:
            with self.assertRaises(ValueError):
                self.assess(self.request(**patch))

    def test_source_health_and_us_explanations_never_claim_applicability(self):
        for component in ['tool:source-health', 'skill:architecture-knowledge']:
            result = self.assess(self.request(component, locations=[]))
            self.assertEqual(result['status'], 'procedure-supported')
            self.assertIn('limitation', result)

    def test_selected_docs_link_shared_gate_and_keep_flat_names(self):
        for name in ['zoning-analysis-nyc', 'occupancy-calculator', 'environmental-analysis',
                     'mobility-analysis', 'demographics-analysis', 'site-history', 'zoning-envelope']:
            self.assertIn('../../docs/geographic-applicability.md', (ROOT / 'skills' / name / 'SKILL.md').read_text())
        shared = (ROOT / 'skills/nyc-property-report/pluto-resolution.md').read_text()
        self.assertIn('../../docs/geographic-applicability.md', shared)


if __name__ == '__main__':
    unittest.main()
