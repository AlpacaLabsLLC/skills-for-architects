import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = p => readFileSync(resolve(root, p), 'utf8');
const fixtures = JSON.parse(read('tests/fixtures/nyc-code-routes.json'));
const catalog = JSON.parse(read('corpus/sources/catalog.json'));
const cluster = JSON.parse(read('clusters/code-regulatory.json'));
const sourceIds = new Set(catalog.sources.map(s => s.id));
const routes = new Map();
const coverage = new Set();
for (const route of fixtures.routes) {
  assert(!routes.has(route.skill), `Duplicate route: ${route.skill}`);
  routes.set(route.skill, route);
  coverage.add(route.coverage);
  const skill = route.skill.replace(/^skill:/, '');
  assert(existsSync(resolve(root, `skills/${skill}/README.md`)), `Missing README: ${skill}`);
  const card = read(`skills/${skill}/SKILL.md`);
  assert(card.includes(`name: ${skill}\n`), `Name mismatch: ${skill}`);
  assert(route.trigger && route.non_trigger && route.required_input && route.output && route.access_failure && route.missing_context, `Incomplete intent contract: ${skill}`);
  assert(cluster.members.includes(route.skill), `Cluster omits ${skill}`);
  assert(route.source_ids.length, `No source dependency: ${skill}`);
  for (const id of route.source_ids) {
    assert(sourceIds.has(id), `Unregistered source ${id} in ${skill}`);
    assert(card.includes('`' + id + '`'), `Card and fixture source drift: ${skill}/${id}`);
  }
}
assert.equal(routes.size, 45, 'Approved atomic intent denominator changed without updating test scope');
assert.deepEqual([...coverage].sort(), Array.from({length:13}, (_,i) => `N${String(i+1).padStart(2,'0')}`));
for (const test of fixtures.cases) {
  assert(test.request && (test.expected_skill || test.expected), 'Missing case outcome');
  if (test.expected_skill) assert(existsSync(resolve(root, `skills/${test.expected_skill}/SKILL.md`)), `Unresolved expected skill: ${test.expected_skill}`);
  for (const id of test.sources || []) assert(sourceIds.has(id), `Unregistered fixture source: ${id}`);
  assert(!(test.must_not || []).includes(test.expected_skill), `Contradictory routing case: ${test.request}`);
}
assert.equal(cluster.coverage.workflow_validated, false, 'Host acceptance must not be inferred from contract tests');
console.log(`NYC routing contract: ${routes.size} atomic routes, ${fixtures.cases.length} frozen cases, N01–N13 covered. This is not a model/host behavior test.`);
