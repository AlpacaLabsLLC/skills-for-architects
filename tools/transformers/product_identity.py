"""Shared FF&E identity/filename policy; import from the exact delivered package.

No filesystem mutations or identity normalization. The package-relative schema is required.
"""
import json
from pathlib import Path
import re

SCHEMA = json.loads((Path(__file__).resolve().parents[2] / 'schema/product-identity.schema.json').read_text(encoding='utf-8'))
TAG_PATTERN = re.compile(SCHEMA['$defs']['tag']['pattern'])
FILENAME_PATTERN = re.compile(SCHEMA['$defs']['filename']['pattern'])
RESERVED_STEMS = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}


def validate_tag(tag, field):
    if not isinstance(tag, str) or not TAG_PATTERN.fullmatch(tag):
        raise ValueError(f'{field}: expected exact product ID, 1–80 ASCII letters/digits/dot/underscore/hyphen, starting with a letter or digit')
    return tag


def validate_filename(filename, field):
    valid = isinstance(filename, str) and FILENAME_PATTERN.fullmatch(filename)
    if valid:
        stem = filename[:-4]
        valid = not stem.endswith('.') and stem.upper().split('.')[0] not in RESERVED_STEMS and filename.casefold() != 'combined.pdf'
    if not valid:
        raise ValueError(f'{field}: expected safe 1–80 character stem plus .pdf; no path separators, trailing-dot stem, reserved device name or combined.pdf; use an explicit version-2 filename mapping without changing tag')
    return filename


def output_names(groups, version, *, prepared=False):
    if type(version) is not int or version not in (1, 2):
        raise ValueError('schema_version: expected output version 1 or 2')
    if not isinstance(groups, list) or not groups:
        raise ValueError('outputs: expected nonempty array')
    tags, filenames, result = set(), set(), []
    for index, group in enumerate(groups):
        label = f'outputs[{index}]'
        if not isinstance(group, dict):
            raise ValueError(f'{label}: expected object')
        tag = validate_tag(group.get('tag'), label + '.tag')
        if tag in tags:
            raise ValueError(f'{label}.tag: duplicate exact product identity')
        tags.add(tag)
        if version == 1 and 'filename' in group:
            raise ValueError(f'{label}.filename: explicit mapping requires schema_version 2')
        if version == 2 and prepared and 'filename' not in group:
            raise ValueError(f'{label}.filename: required in prepared version-2 manifest')
        filename = validate_filename(group.get('filename', tag + '.pdf'), label + '.filename')
        if filename.casefold() in filenames:
            raise ValueError(f'{label}.filename: case-insensitive collision; explicitly map distinct identities to distinct filenames')
        filenames.add(filename.casefold())
        result.append(filename)
    return result


def tag_match(tag, content):
    validate_tag(tag, 'tag')
    # Period stays a token character: TAG.pdf is filename text, not a bare product identity.
    return re.search(r'(?<![A-Za-z0-9._-])' + re.escape(tag) + r'(?![A-Za-z0-9._-])', content)
