import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, cp, readFile, writeFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateCatalog } from '../tools/integrations/geographic-catalog.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
test('authored geographic records deterministically reproduce compatibility catalogs',async()=>{
  const outputs=await generateCatalog(root);
  for(const [file,text] of Object.entries(outputs)) assert.equal(text,await readFile(path.join(root,file),'utf8'));
  const ids=JSON.parse(outputs['corpus/sources/catalog.json']).sources.map(x=>x.id);
  for(const id of ['source:nyc-construction-codes','source:nyc-zoning-resolution','source:nyc-pluto']) assert.ok(ids.includes(id));
});
test('duplicate IDs and jurisdiction cycles fail closed; schema supports a non-NYC child',async()=>{
  const tmp=await mkdtemp(path.join(os.tmpdir(),'as-geo-test-'));
  try {
    for(const dir of ['corpus','schema','tools','skills']) await cp(path.join(root,dir),path.join(tmp,dir),{recursive:true});
    const file=path.join(tmp,'corpus/jurisdictions/us/test.json');
    const record={schema_version:1,record_type:'jurisdiction',data:{id:'jurisdiction:us-test',name:'Fictional schema fixture',parent:'jurisdiction:us',coverage:'routing-only'}};
    await writeFile(file,JSON.stringify(record));
    assert.ok(JSON.parse((await generateCatalog(tmp))['corpus/jurisdictions/catalog.json']).jurisdictions.some(x=>x.id==='jurisdiction:us-test'));
    record.data.id='jurisdiction:us';await writeFile(file,JSON.stringify(record));
    await assert.rejects(generateCatalog(tmp),/duplicate/);
    record.data.id='jurisdiction:us-test';record.data.parent='jurisdiction:us-test';await writeFile(file,JSON.stringify(record));
    await assert.rejects(generateCatalog(tmp),/cycle/);
    record.data.parent='jurisdiction:us';await writeFile(file,JSON.stringify(record));
    const sourceFile=path.join(tmp,'corpus/jurisdictions/us/ny/nyc/codes/nyc-construction-codes.json');
    const source=JSON.parse(await readFile(sourceFile,'utf8'));
    const originalFamily=source.data.governance?.family_id;
    source.data.governance.family_id='family:missing-fixture';
    await writeFile(sourceFile,JSON.stringify(source));await assert.rejects(generateCatalog(tmp),/family/);
    source.data.governance.family_id=originalFamily;
    source.relationships=[{from:source.data.id,to:'authority:nyc-dob',type:'published-by',edition:null,effective_date:null,evidence:'corpus/../../outside'}];
    await writeFile(sourceFile,JSON.stringify(source));await assert.rejects(generateCatalog(tmp),/unsafe relationship evidence/);
    source.relationships[0].evidence='corpus/absent.md';await writeFile(sourceFile,JSON.stringify(source));await assert.rejects(generateCatalog(tmp),/ENOENT|missing/);
  } finally {await rm(tmp,{recursive:true,force:true});}
});
