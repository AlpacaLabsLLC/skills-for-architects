import { readdir, readFile, writeFile, lstat, realpath } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateShape, validateRelationships } from './source-health.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const json = async file => JSON.parse(await readFile(file, 'utf8'));
const render = value => `${JSON.stringify(value, null, 2)}\n`;

// Only authored records own data; compatibility catalogs are deterministic views.
export async function generateCatalog(base = root) {
  base = await realpath(base);
  const records = [], families = [];
  async function walk(relative) {
    const current = path.join(base,relative);
    if ((await lstat(current)).isSymbolicLink() || !(await realpath(current)).startsWith(`${base}${path.sep}`)) throw new Error(`unsafe geographic root: ${relative}`);
    for (const entry of (await readdir(path.join(base, relative), { withFileTypes: true })).sort((a,b) => a.name.localeCompare(b.name))) {
      const target = path.posix.join(relative, entry.name);
      if (entry.isSymbolicLink()) throw new Error(`symlink record rejected: ${target}`);
      if (entry.isDirectory()) await walk(target);
      else if (entry.name.endsWith('.json') && entry.name !== 'catalog.json') {
        const value = await json(path.join(base, target));
        if (value.record_type) records.push({ value, path: target });
        else if (entry.name === 'families.json') {
          if (value.schema_version !== 1 || !Array.isArray(value.families) || Object.keys(value).some(k => !['schema_version','families'].includes(k))) throw new Error(`invalid family map: ${target}`);
          families.push(...value.families);
        }
      }
    }
  }
  await walk('corpus/jurisdictions');
  const sources = [], authorities = [], jurisdictions = [], relationships = [];
  const seen = new Set();
  for (const {value, path: filename} of records) {
    if (value.schema_version !== 1 || !['source','authority','jurisdiction'].includes(value.record_type)) throw new Error(`invalid geographic record: ${filename}`);
    if (!value.data?.id || seen.has(value.data.id)) throw new Error(`missing/duplicate geographic ID: ${filename}`);
    seen.add(value.data.id);
    if (Object.keys(value).some(k => !['schema_version','record_type','data','relationships'].includes(k))) throw new Error(`unknown record field: ${filename}`);
    ({source:sources, authority:authorities, jurisdiction:jurisdictions})[value.record_type].push(value.data);
    for (const relation of value.relationships ?? []) relationships.push(relation);
  }
  for (const group of [sources,authorities,jurisdictions]) group.sort((a,b) => a.id.localeCompare(b.id));
  const catalog = {schema_version:1,authorities,sources,relationships:relationships.sort((a,b) => JSON.stringify(a).localeCompare(JSON.stringify(b)))};
  const geography = {schema_version:1,jurisdictions};
  validateShape(catalog, await json(path.join(base,'schema/source-catalog.schema.json')));
  validateShape(geography, await json(path.join(base,'schema/jurisdiction-catalog.schema.json')));
  const integrations = await json(path.join(base,'tools/integrations/catalog.json'));
  const standards = [];
  for (const name of await readdir(path.join(base,'corpus/shared-references'))) {
    if (name.endsWith('.json')) standards.push(await json(path.join(base,'corpus/shared-references',name)));
  }
  validateRelationships({sources:catalog,jurisdictions:geography,integrations,standards});
  const familyIds = new Set();
  for (const family of families) {
    if (!/^family:[a-z0-9-]+$/.test(family.id ?? '') || familyIds.has(family.id) || typeof family.title !== 'string' || !family.title.trim() || !jurisdictions.some(j=>j.id===family.jurisdiction)) throw new Error('invalid or duplicate source family');
    if (Object.keys(family).some(k=>!['id','title','jurisdiction','edition_source_ids','limitations','evidence'].includes(k))) throw new Error('unknown source family field');
    if (!Array.isArray(family.edition_source_ids) || !family.edition_source_ids.length || new Set(family.edition_source_ids).size!==family.edition_source_ids.length) throw new Error('invalid family editions');
    if (!Array.isArray(family.limitations) || family.limitations.some(x=>typeof x!=='string') || !Array.isArray(family.evidence) || !family.evidence.length) throw new Error('missing family evidence/limitations');
    for (const e of family.evidence) {
      if (Object.keys(e).some(k=>!['url','checked_at','note'].includes(k)) || !/^https:\/\//.test(e.url ?? '') || !/^\d{4}-\d{2}-\d{2}$/.test(e.checked_at ?? '') || typeof e.note!=='string' || !e.note.trim()) throw new Error('invalid family evidence');
    }
    for (const id of family.edition_source_ids) {
      const source = sources.find(s=>s.id===id);
      if (!source || source.governance?.family_id!==family.id || source.jurisdiction!==family.jurisdiction) throw new Error(`invalid family edition reference: ${id}`);
    }
    familyIds.add(family.id);
  }
  for (const source of sources) if (source.governance?.family_id && !familyIds.has(source.governance.family_id)) throw new Error(`unresolved source family: ${source.id}`);
  for (const relation of relationships) {
    if (!/^(?:skills|corpus)\/[a-zA-Z0-9/_.-]+$/.test(relation.evidence) || relation.evidence.split('/').includes('..')) throw new Error('unsafe relationship evidence');
    const evidence = path.join(base,relation.evidence);
    if (!(await lstat(evidence)).isFile() || !(await realpath(evidence)).startsWith(`${base}${path.sep}`)) throw new Error('unsafe or missing relationship evidence');
  }
  for (const source of sources) {
    if (source.governance?.review.status === 'reviewed' && (!source.governance.review.reviewer || !source.governance.review.reviewed_at)) throw new Error(`unattributed review: ${source.id}`);
    const retrieval = source.retrieval;
    if (retrieval) {
      for (const origin of retrieval.allowed_origins) {
        const url = new URL(origin);
        if (url.protocol !== 'https:' || url.origin !== origin || url.username || url.password) throw new Error(`invalid approved origin: ${source.id}`);
      }
      if (!retrieval.allowed_origins.includes(new URL(source.url).origin)) throw new Error(`source origin unapproved: ${source.id}`);
      for (const [id, provision] of Object.entries(retrieval.provisions ?? {})) {
        if (!/^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}$/.test(id) || !provision || Object.keys(provision).some(k => !['url','contains_all','start_id','end_id'].includes(k))) throw new Error(`invalid provision: ${source.id}`);
        for (const key of ['start_id','end_id']) if (provision[key] !== undefined && (typeof provision[key] !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,255}$/.test(provision[key]))) throw new Error(`invalid heading selector: ${source.id}`);
        const url = new URL(provision.url);
        if (url.protocol !== 'https:' || url.username || url.password || !retrieval.allowed_origins.includes(url.origin)) throw new Error(`unapproved provision: ${source.id}`);
        if (!Array.isArray(provision.contains_all) || !provision.contains_all.length || provision.contains_all.some(s => typeof s !== 'string' || !s.trim())) throw new Error(`missing provision identity: ${source.id}`);
      }
    }
    for (const name of source.existing_skills) {
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name)) throw new Error(`unsafe skill name: ${name}`);
      if (!(await lstat(path.join(base,'skills',name,'SKILL.md'))).isFile()) throw new Error(`missing skill: ${name}`);
    }
  }
  // Supersession and amendment relations cannot introduce circular precedence.
  const graph = new Map();
  for (const r of relationships.filter(r => ['supersedes','amends'].includes(r.type))) {
    graph.set(r.from,[...(graph.get(r.from) ?? []),r.to]);
  }
  function visit(id, active = new Set()) {
    if (active.has(id)) throw new Error(`relation cycle: ${id}`);
    for (const next of graph.get(id) ?? []) visit(next,new Set([...active,id]));
  }
  for (const id of graph.keys()) visit(id);
  return {'corpus/sources/catalog.json':render(catalog),'corpus/jurisdictions/catalog.json':render(geography)};
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const mode = process.argv[2] ?? '--check';
  if (!['--check','--write'].includes(mode)) throw new Error('use --check or --write');
  const outputs = await generateCatalog();
  for (const [file, text] of Object.entries(outputs)) {
    if (mode === '--write') {
      const target = path.join(root,file);
      if ((await lstat(target)).isSymbolicLink() || !(await realpath(target)).startsWith(`${await realpath(root)}${path.sep}`)) throw new Error('unsafe generated catalog target');
      await writeFile(target,text);
    }
    else if (await readFile(path.join(root,file),'utf8') !== text) throw new Error(`generated catalog drift: ${file}`);
  }
  console.log(`geographic catalogs ${mode === '--check' ? 'verified' : 'generated'}`);
}
