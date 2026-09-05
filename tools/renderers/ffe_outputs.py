#!/usr/bin/env python3
"""Prepare allowlisted FF&E render data and verify host-produced PDF packages.

This is a local, synchronous contract helper, not a renderer or remote filesystem API.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('invalid number: ' + value)))


def write_json(path, value):
    path.write_bytes(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode() + b'\n')


def safe_file(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'missing file or symlink: ' + str(path))
    return path


def tag_ok(tag):
    return isinstance(tag, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}', tag) and not tag.endswith('.') and tag.upper().split('.')[0] not in {'CON','PRN','AUX','NUL', *(f'COM{i}' for i in range(1,10)), *(f'LPT{i}' for i in range(1,10))}


def positive(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def prepare(args):
    snapshot = read_json(args.input)
    contract = read_json(args.contract)
    template = safe_file(args.template)
    require(type(contract.get('schema_version')) is int and contract['schema_version'] == 1, 'unsupported contract version')
    require(set(contract) <= {'schema_version', 'mode', 'audience', 'allowed_fields', 'template_accepted', 'layout_requirements', 'missing_image_policy', 'combined_pdf', 'outputs'}, 'unknown output contract keys')
    require(contract.get('mode') in ('adopted', 'one-off'), 'explicit adopted or one-off mode required')
    require(contract.get('audience') in ('client', 'internal'), 'explicit audience required')
    require(contract.get('template_accepted') is True, 'template must be inspected and accepted for this job')
    require(isinstance(contract.get('layout_requirements'), list) and contract['layout_requirements'] and all(isinstance(v, str) and v.strip() for v in contract['layout_requirements']), 'layout requirements required')
    fields = contract.get('allowed_fields')
    require(isinstance(fields, list) and fields and all(isinstance(v, str) and v for v in fields) and len(set(fields)) == len(fields), 'explicit unique allowed_fields required')
    require(contract.get('missing_image_policy') in ('block', 'labeled-placeholder'), 'missing image policy required')
    require(isinstance(contract.get('combined_pdf'), bool), 'combined_pdf must be explicit')
    groups = contract.get('outputs')
    require(isinstance(groups, list) and groups, 'explicit ordered output grouping required')
    items = snapshot.get('items')
    require(isinstance(items, list) and items, 'items required')
    by_id = {}
    for item in items:
        require(isinstance(item, dict) and isinstance(item.get('item_id'), str) and item['item_id'], 'item_id required')
        require(item['item_id'] not in by_id, 'duplicate item_id')
        require(positive(item.get('revision')), 'positive item revision required')
        require(isinstance(item.get('fields'), dict), 'item fields required')
        by_id[item['item_id']] = item
    if contract['mode'] == 'adopted':
        require(isinstance(snapshot.get('schedule_id'), str) and snapshot['schedule_id'] and positive(snapshot.get('revision')) and isinstance(snapshot.get('hash'), str) and re.fullmatch('[a-f0-9]{64}', snapshot['hash']), 'adopted snapshot requires schedule_id, revision and hash')
    require(isinstance(snapshot.get('source'), (dict, str)) and snapshot['source'], 'source identity required')
    seen_tags, covered, payload, pinned, denied = set(), [], [], [], []
    image_root = Path(args.input).resolve().parent
    assets = {}
    for group in groups:
        require(isinstance(group, dict) and set(group) <= {'tag', 'item_ids', 'expected_pages', 'images'}, 'invalid output group')
        tag = group.get('tag')
        require(tag_ok(tag), 'unsafe output tag; resolve explicitly, never silently rename')
        require(tag.casefold() not in seen_tags and tag.casefold() != 'combined', 'duplicate/reserved output tag')
        seen_tags.add(tag.casefold())
        ids = group.get('item_ids')
        require(isinstance(ids, list) and ids and all(isinstance(v, str) and v in by_id for v in ids) and len(set(ids)) == len(ids), 'invalid group item_ids')
        require(positive(group.get('expected_pages')), 'positive expected_pages required per output')
        require(isinstance(group.get('images', {}), dict) and set(group.get('images', {})) <= set(ids), 'image mapping must reference grouped items')
        rows = []
        for item_id in ids:
            item = by_id[item_id]
            covered.append(item_id)
            projected = {key: item['fields'][key] for key in fields if key in item['fields']}
            for key, value in projected.items():
                require(value is None or isinstance(value, (str, int, float, bool)), 'render fields must be scalar, flatten explicitly: ' + key)
            denied.extend(str(v) for k, v in item['fields'].items() if k not in fields and isinstance(v, (str, int, float)) and str(v).strip())
            row = {'item_id': item_id, 'revision': item['revision'], 'fields': projected}
            image = group.get('images', {}).get(item_id)
            if image:
                require(isinstance(image, dict) and set(image) == {'path', 'source', 'status'}, 'invalid image contract')
                require(image.get('status') in ('exact', 'representative') and isinstance(image.get('source'), str) and image['source'], 'image status/source required')
                require(isinstance(image.get('path'), str) and not Path(image['path']).is_absolute(), 'image must be a relative bundle path')
                candidate = image_root / image['path']
                require(candidate.resolve().is_relative_to(image_root), 'image path escapes source bundle')
                asset = safe_file(candidate)
                image_bytes = asset.read_bytes()
                require(image_bytes.startswith((b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff', b'GIF87a', b'GIF89a')) or (image_bytes.startswith(b'RIFF') and image_bytes[8:12] == b'WEBP'), 'image is not supported raster bytes')
                image_hash = digest(asset.read_bytes())
                # Stable content name; retain source outside delivery. Host validates image bytes.
                name = image_hash + asset.suffix.lower()
                assets[name] = asset
                row['image'] = {'path': 'assets/' + name, 'sha256': image_hash, 'status': image['status'], 'source': image['source']}
                if image['status'] == 'representative':
                    row['image']['label'] = 'Representative product image'
            else:
                require(contract['missing_image_policy'] == 'labeled-placeholder', 'missing image blocks output: ' + tag)
                row['image'] = {'status': 'missing', 'label': 'Product image unavailable'}
            rows.append(row)
        payload.append({'tag': tag, 'items': rows})
        pinned.append({'fingerprint': digest(canonical({'rows': rows, 'source': snapshot['source'], 'schedule_id': snapshot.get('schedule_id'), 'evidence': [by_id[i].get('provenance', {}) for i in ids], 'group': group, 'template': digest(template.read_bytes()), 'audience': contract['audience'], 'fields': fields, 'layout': contract['layout_requirements']})), 'tag': tag, 'items': [{'item_id': i, 'revision': by_id[i]['revision']} for i in ids], 'expected_pages': group['expected_pages']})
    require(set(covered) == set(by_id), 'grouping must cover the explicit snapshot item scope exactly')
    require(len(covered) == len(set(covered)), 'item occurs in multiple groups; resolve finish/product grouping explicitly')
    fingerprint = digest(canonical({'snapshot': snapshot, 'contract': contract, 'template_sha256': digest(template.read_bytes()), 'assets': sorted(assets)}))
    target = Path(args.output)
    require(not target.exists() and not target.is_symlink(), 'output exists; preserve prior revision, use a new job revision')
    manifest = {'schema_version': 1, 'fingerprint': fingerprint, 'mode': contract['mode'], 'audience': contract['audience'], 'source_sha256': digest(canonical(snapshot)), 'schedule': {k: snapshot[k] for k in ('schedule_id', 'revision', 'hash') if k in snapshot}, 'template_sha256': digest(template.read_bytes()), 'contract': contract, 'outputs': pinned, 'denied_values': denied, 'status': 'prepared'}
    target.mkdir(parents=True)
    for directory in ('internal', 'render', 'delivery'):
        (target / directory).mkdir()
    (target / 'render/assets').mkdir()
    for name, asset in assets.items():
        shutil.copyfile(asset, target / 'render/assets' / name)
    # Accepted template is not automatically copied into a client package.
    write_json(target / 'render/data.json', {'schema_version': 1, 'audience': contract['audience'], 'outputs': payload})
    manifest['render_sha256'] = digest((target / 'render/data.json').read_bytes())
    write_json(target / 'internal/manifest.json', manifest)
    print(json.dumps({'status': 'prepared', 'fingerprint': fingerprint, 'manifest': str(target / 'internal/manifest.json'), 'workflowCompleted': False}))


def run_pdf(tool, path):
    require(shutil.which(tool), 'missing host verification capability: ' + tool)
    command = [tool, str(path)] if tool == 'pdfinfo' else [tool, '-layout', str(path), '-']
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    require(result.returncode == 0, 'PDF parse failed: ' + path.name)
    return result.stdout


def check(args):
    root = Path(args.job).resolve()
    manifest = read_json(root / 'internal/manifest.json')
    require(manifest.get('schema_version') == 1, 'unsupported manifest version')
    require(digest(canonical(read_json(args.input))) == manifest['source_sha256'], 'source changed; prepare a new revision')
    require(read_json(args.contract) == manifest['contract'], 'contract changed; prepare a new revision')
    require(digest(safe_file(args.template).read_bytes()) == manifest['template_sha256'], 'template changed; prepare a new revision')
    for group in read_json(root / 'render/data.json')['outputs']:
        for item in group['items']:
            asset = item['image']
            if 'path' in asset:
                require(digest(safe_file(root / 'render' / asset['path']).read_bytes()) == asset['sha256'], 'image changed; prepare a new revision')
    inspection = read_json(args.inspection)
    require(inspection.get('fingerprint') == manifest['fingerprint'], 'stale inspection fingerprint')
    require(digest(safe_file(root / 'render/data.json').read_bytes()) == manifest['render_sha256'], 'render data changed; create a new preparation')
    contract = manifest['contract']
    expected = [o['tag'] + '.pdf' for o in manifest['outputs']]
    if contract['combined_pdf']:
        expected.append('combined.pdf')
    delivery = root / 'delivery'
    actual = sorted(p.name for p in delivery.iterdir())
    failures, verified = [], []
    if sorted(expected) != actual:
        failures.append('delivery file set differs from exact expected PDF set')
    entries = inspection.get('artifacts', {})
    for name in expected:
        try:
            path = safe_file(delivery / name)
            data = path.read_bytes()
            require(data.startswith(b'%PDF-') and b'%%EOF' in data[-2048:], 'not a complete PDF: ' + name)
            info = run_pdf('pdfinfo', path)
            text = run_pdf('pdftotext', path)
            pages = re.search(r'^Pages:\s+(\d+)\s*$', info, re.M)
            expected_pages = sum(o['expected_pages'] for o in manifest['outputs']) if name == 'combined.pdf' else next(o['expected_pages'] for o in manifest['outputs'] if o['tag'] + '.pdf' == name)
            require(pages and int(pages[1]) == expected_pages, 'page count differs: ' + name)
            evidence = entries.get(name, {})
            require(evidence.get('sha256') == digest(data), 'missing/stale artifact inspection hash: ' + name)
            for flag in ('rendered_pages_inspected', 'layout_matches', 'images_checked', 'links_checked', 'audience_checked'):
                require(evidence.get(flag) is True, 'inspection missing ' + flag + ': ' + name)
            require(isinstance(evidence.get('evidence'), str) and evidence['evidence'].strip(), 'inspection evidence reference required: ' + name)
            require(evidence.get('template_sha256') == manifest['template_sha256'], 'template inspection mismatch')
            # Text and metadata are only an additional guard; host checks links, attachments,
            # hidden layers and images, which plain-text extraction cannot prove safe.
            haystack = ' '.join((text + '\n' + info).split())
            projected = read_json(root / 'render/data.json')
            selected_groups = projected['outputs'] if name == 'combined.pdf' else [group for group in projected['outputs'] if group['tag'] + '.pdf' == name]
            for group in selected_groups:
                for row in group['items']:
                    label = row['image'].get('label')
                    require(not label or label in ' '.join(text.split()), 'required image disclosure missing: ' + name)
            visible_values = {' '.join(str(v).split()) for group in projected['outputs'] for row in group['items'] for v in row['fields'].values()}
            for value in manifest['denied_values']:
                normalized = ' '.join(value.split())
                if normalized not in visible_values and len(normalized) >= 4:
                    require(normalized not in haystack, 'non-allowlisted field value detected: ' + name)
            tags = [o['tag'] for o in manifest['outputs']] if name == 'combined.pdf' else [name[:-4]]
            matches = [re.search(r'(?<![A-Za-z0-9._-])' + re.escape(tag) + r'(?![A-Za-z0-9._-])', text) for tag in tags]
            positions = [match.start() if match else -1 for match in matches]
            require(all(p >= 0 for p in positions), 'expected tag not found in PDF text: ' + name)
            if name == 'combined.pdf':
                require(positions == sorted(positions), 'combined tag order differs')
            verified.append({'file': name, 'sha256': digest(data), 'pages': int(pages[1])})
        except (ValueError, OSError, subprocess.TimeoutExpired) as error:
            failures.append(str(error))
    receipt = {'schema_version': 1, 'fingerprint': manifest['fingerprint'], 'schedule': manifest['schedule'], 'outputs': manifest['outputs'], 'template_sha256': manifest['template_sha256'], 'audience': manifest['audience'], 'verified_artifacts': verified, 'failures': failures, 'status': 'complete' if not failures else 'incomplete', 'workflowCompleted': not failures, 'verification': 'PDF parsing plus host-supplied hash-bound visual/link/audience evidence; not independent visual verification'}
    # Do not erase earlier receipts or use an output receipt to mutate item records.
    receipt_path = Path(args.receipt)
    require(not receipt_path.exists() and not receipt_path.is_symlink(), 'receipt exists; preserve previous evidence')
    write_json(receipt_path, receipt)
    print(json.dumps(receipt))
    return 0 if not failures else 2


def resume(args):
    old_root, new_root = Path(args.previous), Path(args.job)
    old = read_json(old_root / 'internal/manifest.json')
    new = read_json(new_root / 'internal/manifest.json')
    receipt = read_json(args.receipt)
    require(receipt['fingerprint'] == old['fingerprint'], 'previous receipt does not match job')
    validated = {entry['file']: entry for entry in receipt['verified_artifacts']}
    old_outputs = {entry['tag']: entry for entry in old['outputs']}
    reusable, invalidated = [], []
    for entry in new['outputs']:
        name = entry['tag'] + '.pdf'
        prior = old_outputs.get(entry['tag'], {})
        verified = validated.get(name)
        if prior.get('fingerprint') == entry['fingerprint'] and verified:
            try:
                require(digest(safe_file(old_root / 'delivery' / name).read_bytes()) == verified['sha256'], 'changed file')
                reusable.append({'file': name, 'sha256': verified['sha256']})
                continue
            except (ValueError, OSError):
                pass
        invalidated.append(name)
    print(json.dumps({'status': 'resume-plan', 'workflowCompleted': False, 'reusable': reusable, 'invalidated': invalidated, 'combined': 'rebuild and reverify', 'instruction': 'Copy reusable files into new job only; inspect and check new package. No files or records mutated.'}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    for name in ('input', 'contract', 'template', 'output'):
        prep.add_argument('--' + name, required=True)
    verify = sub.add_parser('check')
    for name in ('job', 'inspection', 'receipt', 'input', 'contract', 'template'):
        verify.add_argument('--' + name, required=True)
    reuse = sub.add_parser('resume')
    for name in ('previous', 'job', 'receipt'):
        reuse.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        return {'prepare': prepare, 'check': check, 'resume': resume}[args.command](args)
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(json.dumps({'status': 'blocked', 'workflowCompleted': False, 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
