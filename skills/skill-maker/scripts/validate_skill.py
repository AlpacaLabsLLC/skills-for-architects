#!/usr/bin/env python3
"""Portable skill scaffold validation; no shell or search executable dependency."""
from pathlib import Path
import re
import yaml


def dispatch(operation, request):
    if operation != 'skill_scaffold.validate':
        raise ValueError('Unknown scaffold operation')
    target = Path(request['directory'])
    if not target.is_dir() or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', target.name):
        raise ValueError('Existing lowercase kebab-case skill directory required')
    if not (target / 'README.md').is_file():
        raise ValueError('Missing README.md')
    text = (target / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not match:
        raise ValueError('SKILL.md requires initial YAML frontmatter')
    frontmatter = yaml.safe_load(match.group(1))
    if not isinstance(frontmatter, dict) or frontmatter.get('name') != target.name or not isinstance(frontmatter.get('description'), str) or not frontmatter['description'].strip():
        raise ValueError('Matching name and nonempty description required')
    if '~/' in text:
        raise ValueError('SKILL.md must not contain home shortcut paths')
    return {'valid': True, 'directory': str(target), 'name': target.name}
