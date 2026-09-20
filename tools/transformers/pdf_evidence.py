#!/usr/bin/env python3
"""Read PDF bytes into document-bound page/text/annotation evidence; no OCR or URL fetch."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

_NO_PAGE_MAP = object()


def locator(value):
    keys = ('document_sha256', 'physical_page', 'annotation_index')
    if not all(key in value for key in keys):
        raise ValueError('Full document/page/annotation locator required')
    digest, page, index = (value[key] for key in keys)
    if not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest):
        raise ValueError('SHA-256 required, not filename or suffix')
    if type(page) is not int or page < 1 or type(index) is not int or index < 0:
        raise ValueError('Physical page is one-based; annotation index is zero-based')
    return digest, page, index


def bind_link(annotations, key):
    """Resolve one explicit evidence locator; does not infer which product owns it."""
    if not isinstance(annotations, list) or not isinstance(key, dict) or any(not isinstance(row, dict) for row in annotations):
        raise ValueError('Annotation array and locator object required')
    target = locator(key)
    matches = [row for row in annotations if locator(row) == target]
    if len(matches) != 1:
        raise ValueError('Annotation locator missing or ambiguous; never fall back to page/name')
    row = matches[0]
    uri, box = row.get('uri'), row.get('bbox')
    if not isinstance(uri, str) or any(c.isspace() for c in uri):
        raise ValueError('Full HTTP(S) product URL required')
    url = urlsplit(uri)
    if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
        raise ValueError('Full HTTP(S) product URL without credentials required')
    if not isinstance(box, list) or len(box) != 4:
        raise ValueError('Annotation bounding box required')
    try:
        valid = all(type(n) in (int, float) and math.isfinite(n) for n in box) and box[0] < box[2] and box[1] < box[3]
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError('Finite nonempty annotation bounding box required')
    return dict(matches[0])


def validate_page_map(value, document_sha256, page_count):
    """Validate supplied host review against actual PDF identity, never infer numbering or OCR."""
    if not isinstance(value, dict) or set(value) != {'schema_version', 'document_sha256', 'page_count', 'entries'}:
        raise ValueError('Page map requires schema_version, document_sha256, page_count and entries only')
    if type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ValueError('Page map schema_version must be 1')
    if not isinstance(value['document_sha256'], str) or not re.fullmatch('[a-f0-9]{64}', value['document_sha256']) or value['document_sha256'] != document_sha256:
        raise ValueError('Page map document hash does not match exact PDF bytes')
    if type(value['page_count']) is not int or value['page_count'] != page_count or page_count < 1:
        raise ValueError('Page map page_count must match the actual PDF')
    if not isinstance(value['entries'], list) or len(value['entries']) != page_count:
        raise ValueError('Page map must account for every physical page explicitly')
    physical, printed = set(), set()
    for index, entry in enumerate(value['entries']):
        if not isinstance(entry, dict) or set(entry) != {'physical_page', 'printed_page', 'status', 'evidence'}:
            raise ValueError(f'Page map entries[{index}] requires physical_page, printed_page, status and evidence only')
        page, label = entry['physical_page'], entry['printed_page']
        if type(page) is not int or not 1 <= page <= page_count or page in physical:
            raise ValueError('Page map physical pages must be unique one-based actual indices')
        physical.add(page)
        if label is not None and (not isinstance(label, str) or not label.strip() or len(label) > 128):
            raise ValueError('Printed page must be an explicit nonblank label up to 128 characters or null')
        if label is not None:
            if label in printed:
                raise ValueError('Printed page labels are ambiguous; preserve unresolved entries instead of inferring an offset')
            printed.add(label)
        if entry['status'] not in ('visual-reviewed', 'ocr-unverified', 'unresolved'):
            raise ValueError('Page map requires explicit visual-reviewed, ocr-unverified or unresolved status')
        if entry['status'] == 'visual-reviewed' and label is None:
            raise ValueError('Visual-reviewed page requires an explicit printed label')
        if not isinstance(entry['evidence'], str) or not entry['evidence'].strip() or len(entry['evidence']) > 2048:
            raise ValueError('Page map requires a bounded nonblank host review/source evidence reference')
    return copy.deepcopy(value)


def extract_pdf(payload, page_map=_NO_PAGE_MAP):
    import pymupdf as fitz  # Host dependency; no installation or network side effects.
    digest = hashlib.sha256(payload).hexdigest()
    pages, annotations = [], []
    try:
        doc = fitz.open(stream=payload, filetype='pdf')
    except (fitz.FileDataError, fitz.EmptyFileError) as error:
        raise ValueError('PDF could not be opened: malformed or empty source') from error
    with doc:
        if doc.needs_pass:
            raise ValueError('Password-protected PDF; authorized decryption required')
        for physical, page in enumerate(doc, 1):
            text = page.get_text()
            pages.append(dict(physical_page=physical, printed_page=None,
                              text=text, words=[list(word) for word in page.get_text('words')],
                              text_layer_empty=not bool(text.strip())))
            for index, link in enumerate(page.get_links()):
                if 'uri' in link:
                    annotations.append(dict(document_sha256=digest, physical_page=physical,
                                            annotation_index=index, bbox=list(link['from']), uri=link['uri']))
    result = dict(document_sha256=digest, pages=pages, annotations=annotations,
                  ocr_performed=False, product_associations_inferred=False)
    if page_map is not _NO_PAGE_MAP:
        reviewed_map = validate_page_map(page_map, digest, len(pages))
        by_physical = {entry['physical_page']: entry for entry in reviewed_map['entries']}
        for page in pages:
            entry = by_physical[page['physical_page']]
            if entry['status'] == 'visual-reviewed':
                page['printed_page'] = entry['printed_page']
        result.update(page_map=reviewed_map, page_map_source_verified=False)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['extract', 'bind'])
    parser.add_argument('input', type=Path)
    parser.add_argument('--page-map', type=Path, help='Optional version-1 host-reviewed page map, extract only')
    args = parser.parse_args()
    try:
        if args.command == 'extract':
            def unique_keys(pairs):
                value = {}
                for key, item in pairs:
                    if key in value:
                        raise ValueError('Duplicate JSON key in page map: ' + key)
                    value[key] = item
                return value
            supplied_map = json.loads(args.page_map.read_text(encoding='utf-8'), object_pairs_hook=unique_keys) if args.page_map else _NO_PAGE_MAP
            result = extract_pdf(args.input.read_bytes(), supplied_map)
        else:
            if args.page_map:
                raise ValueError('--page-map is only available with extract')
            request = json.loads(args.input.read_text(encoding='utf-8'))
            result = bind_link(request['annotations'], request['locator'])
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError, ImportError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
