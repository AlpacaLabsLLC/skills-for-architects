#!/usr/bin/env python3
"""Compare OOXML bytes and explicitly allowed cell edits without resaving workbooks."""
import copy
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def members(path):
    path = Path(path)
    if path.suffix.lower() not in ('.xlsx', '.xlsm') or path.is_symlink():
        raise ValueError('Native OOXML .xlsx/.xlsm file required; provider/binary formats are untested')
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or any(name.startswith('/') or '..' in Path(name).parts for name in names):
            raise ValueError('Unsafe or duplicate OOXML members')
        if sum(info.file_size for info in archive.infolist()) > 256 * 1024 * 1024:
            raise ValueError('Workbook exceeds 256 MiB inspection bound')
        if '[Content_Types].xml' not in names or 'xl/workbook.xml' not in names:
            raise ValueError('Not an inspectable OOXML workbook')
        return {name: archive.read(name) for name in names if not name.endswith('/')}


def canonical_xml(element, preserve=False):
    # Only structural indentation is ignorable. Cell/rich-text leaf bytes retain spaces.
    space = element.get('{http://www.w3.org/XML/1998/namespace}space')
    preserve = space == 'preserve' if space is not None else preserve
    text = element.text or ''
    if len(element) and not preserve and not text.strip():
        text = ''
    children = []
    for child in element:
        tail = child.tail or ''
        if not preserve and not tail.strip():
            tail = ''
        children.append((canonical_xml(child, preserve), tail))
    return (element.tag, tuple(sorted(element.attrib.items())), text, tuple(children))


def compare(before, after, allowed_edits):
    old, new = members(before), members(after)
    allowed = {}
    for edit in allowed_edits:
        if not isinstance(edit, dict) or set(edit) != {'part', 'cell', 'aspects'}:
            raise ValueError('Each allowed edit requires part, cell and aspects')
        part, cell, aspects = edit['part'], edit['cell'], edit['aspects']
        if not isinstance(part, str) or not part.startswith('xl/worksheets/') or not part.endswith('.xml') or part not in old or part not in new:
            raise ValueError('Allowed edit must name an existing worksheet part')
        if not isinstance(cell, str) or not isinstance(aspects, list) or not aspects or set(aspects) - {'value', 'formula', 'style', 'cached_value'}:
            raise ValueError('Explicit cell aspects required')
        if (part, cell) in allowed:
            raise ValueError('Duplicate allowed edit')
        allowed[(part, cell)] = set(aspects)
    changes, violations = [], []
    for part in sorted(old.keys() | new.keys()):
        if old.get(part) == new.get(part):
            continue
        changes.append(part)
        if part not in old or part not in new:
            violations.append({'part': part, 'reason': 'member-added-or-removed'})
            continue
        edits = {cell: aspects for (name, cell), aspects in allowed.items() if name == part}
        if not edits:
            violations.append({'part': part, 'reason': 'undeclared-member-change'})
            continue
        trees = [ET.fromstring(old[part]), ET.fromstring(new[part])]
        for tree in trees:
            for cell in tree.findall('.//s:c', NS):
                aspects = edits.get(cell.get('r'), set())
                if not aspects:
                    continue
                formula = cell.find('s:f', NS)
                if 'style' in aspects:
                    cell.attrib.pop('s', None)
                if 'value' in aspects and formula is None:
                    cell.attrib.pop('t', None)
                for child in list(cell):
                    local = child.tag.rsplit('}', 1)[-1]
                    if (local == 'f' and 'formula' in aspects or
                        local in ('v', 'is') and ('cached_value' in aspects if formula is not None else 'value' in aspects)):
                        cell.remove(child)
        if canonical_xml(trees[0]) != canonical_xml(trees[1]):
            violations.append({'part': part, 'reason': 'change-outside-allowed-cell-aspects'})
    return {'status': 'preserved' if not violations else 'changed-outside-scope',
            'before_sha256': hashlib.sha256(Path(before).read_bytes()).hexdigest(),
            'after_sha256': hashlib.sha256(Path(after).read_bytes()).hexdigest(),
            'changed_parts': changes, 'violations': violations, 'preserved': not violations,
            'inspection': 'OOXML member bytes and declared cell XML; no calculation, visual or provider verification',
            'limitations': ['Only stored caches are inspectable; formula recalculation is not performed.',
                            'Binary embedded objects are compared as bytes, not interpreted.'],
            'workflow_completed': False}


def dispatch(operation, request):
    if operation != 'workbook_preservation.compare':
        raise ValueError('Unknown workbook preservation operation')
    return compare(request['before'], request['after'], request['allowed_edits'])
