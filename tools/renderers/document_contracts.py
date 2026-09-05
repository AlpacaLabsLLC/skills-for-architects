#!/usr/bin/env python3
"""Resolve portable shared document assets and physical layout contracts. No rendering."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    def pairs(values):
        result = {}
        for key, value in values:
            require(key not in result, 'duplicate asset key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=lambda value: (_ for _ in ()).throw(ValueError('invalid number: ' + value)))


def number(value, label):
    require(type(value) in (int, float) and math.isfinite(value) and value > 0, 'invalid ' + label)
    return value


def validate_resolved(result):
    require(result.get('schema_version') == 1 and result.get('kind') in ('product-cut-sheet', 'spec-book'), 'invalid design contract')
    unsigned = {key: value for key, value in result.items() if key != 'fingerprint'}
    require(result.get('fingerprint') == sha(canonical(unsigned)), 'resolved design fingerprint mismatch')
    require(result.get('assets') and result.get('identities'), 'resolved assets missing')
    for asset in result['assets']:
        require(sha(asset['text'].encode()) == asset['sha256'], 'resolved asset hash mismatch')
    for key in ('width_pt', 'height_pt', 'content_width_pt', 'content_height_pt'):
        number(result['page'][key], key)
    return result


def resolve(args):
    bundled = Path(__file__).resolve().parents[2] / 'studio'
    roots = []
    if args.project_assets:
        project = Path(args.project_assets)
        require(project.is_dir(), 'selected project asset root missing')
        roots.append(('project', project))
    if args.studio:
        studio = Path(args.studio)
        require((studio / 'STUDIO.md').is_file(), 'configured studio root must contain STUDIO.md')
        roots.append(('studio', studio))
    roots.append(('bundled', bundled))
    assets, identities = [], []

    def select(relative):
        for layer, root in roots:
            candidate = root / relative
            if candidate.exists() or candidate.is_symlink():
                require(candidate.is_file() and not candidate.is_symlink() and candidate.resolve().is_relative_to(root.resolve()), 'invalid shared asset path: ' + relative)
                return layer, root, candidate
        raise ValueError('missing shared asset: ' + relative)

    def manifest(relative, expected_id):
        layer, root, path = select(relative)
        content = load(path)
        require(content.get('schema_version') == 1 and content.get('id') == expected_id and isinstance(content.get('version'), str) and content['version'], 'invalid shared asset identity: ' + relative)
        manifest_asset = {'layer': layer, 'path': relative, 'sha256': sha(path.read_bytes()), 'text': path.read_bytes().decode('utf-8')}
        assets.append(manifest_asset)
        identities.append({'id': content['id'], 'version': content['version'], 'layer': layer, 'manifest_sha256': manifest_asset['sha256']})
        require(isinstance(content.get('assets'), dict) and content['assets'], 'manifest assets required')
        for name, checksum in content['assets'].items():
            asset = path.parent / name
            require(not Path(name).is_absolute() and asset.resolve().is_relative_to(path.parent.resolve()) and asset.is_file() and not asset.is_symlink(), 'missing or unsafe declared asset: ' + name)
            require(sha(asset.read_bytes()) == checksum, 'declared asset hash mismatch: ' + name)
            assets.append({'layer': layer, 'path': str(asset.relative_to(root)), 'sha256': checksum, 'text': asset.read_bytes().decode('utf-8')})
        return content

    system = manifest('standards/documents/design-system.json', 'as.document-design-system')
    canonical_presets = load(bundled / 'standards/documents/design-system.json')['presets']
    require(system.get('presets') == canonical_presets, 'named physical presets cannot be redefined by an override; use custom')
    template = manifest('templates/documents/' + args.kind + '/manifest.json', 'as.' + args.kind + '-template')
    templates = [template]
    if args.kind == 'spec-book':
        require(template.get('dependencies') == ['product-cut-sheet'], 'book must reference shared cut-sheet template')
        templates.append(manifest('templates/documents/product-cut-sheet/manifest.json', 'as.product-cut-sheet-template'))
    for value in templates:
        require(value.get('design_system') == {'id':system['id'],'version':system['version']}, 'template/design-system version mismatch')
        require(args.page in value.get('supported_presets', []) and args.orientation in value.get('orientations', []), 'unsupported template page or orientation')
    if args.project_assets:
        require(any(asset['layer'] == 'project' for asset in assets), 'selected project asset root contains no effective override')
    if args.page == 'custom':
        require(args.custom_units in ('in', 'mm'), 'custom dimensions require in or mm units')
        width, height, units = number(args.custom_width, 'custom width'), number(args.custom_height, 'custom height'), args.custom_units
    else:
        require(args.custom_width is None and args.custom_height is None and args.custom_units is None, 'custom dimensions cannot override a named preset')
        require(args.page in system['presets'], 'unknown physical preset')
        preset = system['presets'][args.page]
        width, height, units = number(preset['width'], 'preset width'), number(preset['height'], 'preset height'), preset['units']
    require(units in ('in','mm'), 'unsupported physical units')
    factor = 72 if units == 'in' else 72 / 25.4
    short, long = sorted([width * factor, height * factor])
    limits = system['custom_limits_pt']
    require(short >= limits['min_short'] and long <= limits['max_long'], 'unsupported physical size limits')
    width_pt, height_pt = (short, long) if args.orientation == 'portrait' else (long, short)
    tier = next((key for key in ('compact','standard','board') if short <= system['layouts'][key]['max_short_pt']), None)
    require(tier, 'unsupported size-aware layout')
    layout = dict(system['layouts'][tier])
    margin = number(layout['margin_pt'], 'margin')
    for key in ('body_pt','title_pt','minimum_type_pt','gutter_pt'):
        number(layout[key], key)
    columns = layout[args.orientation + '_columns']
    require(type(columns) is int and columns > 0, 'invalid column count')
    require(layout['body_pt'] >= layout['minimum_type_pt'] >= 9, 'unreadable typography')
    content_width, content_height = width_pt - 2*margin, height_pt - 2*margin
    require(content_width > 0 and content_height > 0 and (content_width - (columns-1)*layout['gutter_pt'])/columns >= 90, 'insufficient content grid')
    result = {'schema_version':1,'kind':args.kind,'identities':identities,'assets':assets,'override_layers':list(dict.fromkeys(asset['layer'] for asset in assets)), 'page':{'preset':args.page,'orientation':args.orientation,'width_pt':round(width_pt,6),'height_pt':round(height_pt,6),'physical_units':units,'measurement_units':args.measurement_units,'margin_pt':margin,'content_width_pt':round(content_width,6),'content_height_pt':round(content_height,6),'rotation':0,'user_unit':1},'layout':{'id':tier,'version':system['layout_version'],'columns':columns,**layout}}
    result['fingerprint']=sha(canonical(result))
    validate_resolved(result)
    target=Path(args.output)
    require(not target.exists() and not target.is_symlink(), 'resolved output exists; preserve previous resolution')
    with target.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'resolved','fingerprint':result['fingerprint'],'page':result['page'],'layout':result['layout'],'identities':identities,'workflowCompleted':False}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    command=sub.add_parser('resolve')
    command.add_argument('--kind',choices=['product-cut-sheet','spec-book'],required=True)
    command.add_argument('--page',required=True)
    command.add_argument('--orientation',choices=['portrait','landscape'],required=True)
    command.add_argument('--measurement-units',choices=['metric','imperial'],required=True)
    command.add_argument('--custom-width',type=float)
    command.add_argument('--custom-height',type=float)
    command.add_argument('--custom-units',choices=['in','mm'])
    command.add_argument('--studio')
    command.add_argument('--project-assets')
    command.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        resolve(args)
    except (ValueError,OSError,KeyError,TypeError,AttributeError) as error:
        print(json.dumps({'status':'blocked','error':str(error),'workflowCompleted':False}),file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':
    sys.exit(main())
