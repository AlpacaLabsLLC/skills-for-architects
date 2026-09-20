#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node --input-type=module <<'JS'
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {validateShape} from './tools/integrations/source-health.mjs';
const read=p=>JSON.parse(readFileSync(p,'utf8'));
const catalog=read('corpus/sources/catalog.json');
const schema=read('schema/source-catalog.schema.json');
validateShape(catalog,schema);
assert.equal(new Set(catalog.sources.map(s=>s.id)).size,catalog.sources.length);
const jurisdictions=read('corpus/jurisdictions/catalog.json').jurisdictions;
const nyc=jurisdictions.find(j=>j.id==='jurisdiction:us-ny-nyc');
assert.equal(nyc.parent,'jurisdiction:us-ny');
assert.equal(jurisdictions.find(j=>j.id===nyc.parent).parent,'jurisdiction:us');
assert(catalog.sources.some(s=>s.jurisdiction===null));
assert(catalog.sources.some(s=>s.topics.includes('professional-practice')));
assert(catalog.sources.filter(s=>s.jurisdiction==='jurisdiction:us-ny-nyc'&&s.topics.includes('code')).length>0);
assert(!catalog.sources.some(s=>s.jurisdiction==='jurisdiction:us-ca-la'));
for (const fields of [{summary:'a copied rule'},{factors:[12,34]},{findings:['research claim']},{edition:2026}]) {
  const altered=structuredClone(catalog);Object.assign(altered.sources[0],fields);
  assert.throws(()=>validateShape(altered,schema));
}
for(const path of ['skills/occupancy-calculator/data/occupancy-load-factors.json','skills/workplace-programmer/data/findings.json','corpus/practice-methods/us-professional-practice/sources.md','corpus/shared-references/astm-e84.json']) assert(!existsSync(path));
console.log('PASS: single metadata authority, geographic separation, no external-content fields or old derivative datasets');
JS
