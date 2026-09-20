#!/usr/bin/env python3
"""Guarded local product CSV transactions; locks cover cooperating writers only."""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile
import uuid

_spec = importlib.util.spec_from_file_location('product_csv', Path(__file__).resolve().parents[2] / 'skills/product-library/scripts/csv-library.py')
csv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csv)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode('utf-8')


def safe(root, *parts):
    path = root.joinpath(*parts)
    if not path.is_relative_to(root) or '..' in path.parts:
        raise ValueError('Path escapes library project')
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError('Symlink library paths are not supported')
    return path


def root_for(project):
    supplied = Path(project).absolute()
    # Reject aliases within the governed project, but allow OS ancestors such as macOS /var.
    for candidate in (supplied, *supplied.parents):
        if candidate.is_symlink():
            raise ValueError('Symlink project paths are not supported')
        if (candidate / 'PROJECT.md').is_file():
            break
    root = csv.project_root(supplied)
    safe(root, 'PROJECT.md')
    return root


def request_name(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', value):
        raise ValueError('Request ID must be 1–80 safe ASCII characters')
    return value


def current(root):
    target = safe(root, 'product-library.csv')
    return target.read_bytes() if target.exists() else None


def state_hash(data):
    return 'missing' if data is None else sha(data)


def sync_directory(path):
    if os.name != 'nt':
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def write_new(path, data):
    with path.open('xb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def create_directories(root, *parts):
    parent = root
    for part in parts:
        child = safe(root, *parent.relative_to(root).parts, part)
        child.mkdir(exist_ok=True)
        # A cooperating process may have just created this entry before acquiring
        # the writer lock. Persist its parent even when the child already exists.
        sync_directory(parent)
        parent = child
    return parent


@contextmanager
def locked(root):
    root = root_for(root)
    base = create_directories(root, 'ffe', 'library')
    lock_path = safe(root, 'ffe', 'library', '.writer.lock')
    # Keep the lock inode: unlinking it would let a later writer lock a different file.
    with lock_path.open('a+b') as handle:
        try:
            if os.name == 'nt':
                import msvcrt
                if handle.tell() == 0:
                    handle.write(b'0'); handle.flush()
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError('Another product-library writer holds the lock; retry after it finishes') from error
        try:
            yield
        finally:
            if os.name == 'nt':
                handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def proposal(before, operation, row=None, source=None, match_column=None, match_value=None, replace_existing=False):
    header = csv.PRODUCT_HEADER
    if replace_existing and operation != 'import':
        raise ValueError('replace-existing applies only to import')
    rows = csv.parse_bytes(before, header, 'existing library') if before else [list(header)]
    if operation == 'init':
        if before:
            raise ValueError('refusing to overwrite non-empty product library')
        result = [list(header)]
    elif operation == 'import':
        if source is None:
            raise ValueError('import requires source bytes')
        result = csv.parse_bytes(source, header, 'import source')
        if len(rows) > 1 and not replace_existing:
            raise ValueError('refusing to overwrite populated library without replace-existing')
    elif operation in ('append', 'update'):
        if before is None:
            raise ValueError('library does not exist; run init first')
        # An empty existing file is malformed for row mutations, never an implicit init.
        if not before:
            rows = csv.parse_bytes(before, header, 'existing library')
        if operation == 'append':
            values = row if isinstance(row, list) else [row]
            if not values:
                raise ValueError('append requires at least one row')
            for value in values:
                normalized = csv.validate_row(value, header)
                rows.append([normalized[name] for name in header])
        else:
            if match_column not in header or match_value is None:
                raise ValueError('update requires a valid match column and value')
            changes = csv.validate_row(row, header, partial=True)
            matches = [r for r in rows[1:] if r[header.index(match_column)] == match_value]
            if len(matches) != 1:
                raise ValueError('update must match exactly one row')
            for name, value in changes.items():
                matches[0][header.index(name)] = value
        result = rows
    else:
        raise ValueError('Unsupported product operation')
    return csv.encode_rows(result, header)


def payload(operation, row, source, match_column, match_value, replace_existing, expected):
    return dict(operation=operation, row=row, source_sha256=sha(source) if source is not None else None,
                match_column=match_column, match_value=match_value, replace_existing=replace_existing,
                expected_sha256=expected)


def preview(project, operation, **kwargs):
    root = root_for(project)
    before = current(root)
    after = proposal(before, operation, **kwargs)
    return {'operation': operation, 'target': 'product-library.csv', 'before_sha256': state_hash(before),
            'after_sha256': sha(after), 'rows': csv.parse_bytes(after, csv.PRODUCT_HEADER, 'preview')[1:],
            'header': list(csv.PRODUCT_HEADER), 'persisted': False}


def read_operation(root, directory):
    safe(root, *directory.relative_to(root).parts)
    request = json.loads(safe(root, *(directory / 'request.json').relative_to(root).parts).read_bytes())
    required = {'schema_version', 'request_id', 'request_sha256', 'request', 'before_sha256', 'after_sha256'}
    if set(request) != required or request['schema_version'] != 1 or request['request_id'] != directory.name or request['request_sha256'] != sha(encode(request['request'])):
        raise ValueError('Malformed transaction request')
    before = None if request['before_sha256'] == 'missing' else safe(root, *(directory / 'before.csv').relative_to(root).parts).read_bytes()
    after = safe(root, *(directory / 'after.csv').relative_to(root).parts).read_bytes()
    if state_hash(before) != request['before_sha256'] or sha(after) != request['after_sha256']:
        raise ValueError('Transaction artifact checksum mismatch')
    csv.parse_bytes(after, csv.PRODUCT_HEADER, 'transaction output')
    receipt_path = safe(root, *(directory / 'receipt.json').relative_to(root).parts)
    receipt = json.loads(receipt_path.read_bytes()) if receipt_path.exists() else None
    expected_receipt = make_receipt(request)
    if receipt is not None and receipt != expected_receipt:
        raise ValueError('Malformed transaction receipt')
    return request, before, after, receipt


def make_receipt(request):
    return {'schema_version': 1, 'request_id': request['request_id'], 'request_sha256': request['request_sha256'],
            'before_sha256': request['before_sha256'], 'after_sha256': request['after_sha256'],
            'target': 'product-library.csv', 'status': 'committed', 'readback_verified': True}


def publish_receipt(directory, receipt):
    fd, name = tempfile.mkstemp(prefix='.receipt-', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(encode(receipt)); handle.flush(); os.fsync(handle.fileno())
        os.link(name, directory / 'receipt.json')
        sync_directory(directory)
    finally:
        os.unlink(name)


def finish(root, directory, recovered=False):
    request, before, after, receipt = read_operation(root, directory)
    actual = current(root)
    if receipt is not None:
        return dict(receipt, replayed=True, recovered=False, current_sha256=state_hash(actual), current_matches_result=actual == after)
    if actual != before and actual != after:
        raise ValueError('Pending transaction conflicts with current library; preserve and reconcile')
    if actual != after:
        csv.atomic_write(safe(root, 'product-library.csv'), after, csv.MISSING if before is None else before)
        sync_directory(root)
    if current(root) != after:
        raise ValueError('Product library readback differs; transaction remains pending')
    receipt = make_receipt(request)
    publish_receipt(directory, receipt)
    return dict(receipt, replayed=False, recovered=recovered, current_sha256=sha(after), current_matches_result=True)


def execute(project, operation, request_id, expected_sha256, row=None, source=None, match_column=None, match_value=None, replace_existing=False):
    root = root_for(project)
    request_name(request_id)
    if expected_sha256 != 'missing' and (not isinstance(expected_sha256, str) or not re.fullmatch('[a-f0-9]{64}', expected_sha256)):
        raise ValueError('Expected SHA256 must be the preview hash or missing')
    proposed = payload(operation, row, source, match_column, match_value, replace_existing, expected_sha256)
    fingerprint = sha(encode(proposed))
    with locked(root):
        operations = create_directories(root, 'ffe', 'library', 'operations')
        directory = safe(root, 'ffe', 'library', 'operations', request_id)
        # Validate prior operations before allowing a new mutation; incomplete ones block other requests.
        for entry in sorted(operations.iterdir()):
            if entry.name.startswith('.staging-'):
                continue  # unpublished preparation never changes the CSV; retain crash evidence
            request, _, _, receipt = read_operation(root, entry)
            if entry == directory:
                if request['request_sha256'] != fingerprint:
                    raise ValueError('Request ID reused with different inputs or preview state')
                return finish(root, entry, recovered=receipt is None)
            if receipt is None:
                raise ValueError('Another pending transaction requires recovery: ' + entry.name)
        before = current(root)
        if state_hash(before) != expected_sha256:
            raise ValueError('Stale preview hash; reread and reconcile before writing')
        after = proposal(before, operation, row, source, match_column, match_value, replace_existing)
        request = dict(schema_version=1, request_id=request_id, request_sha256=fingerprint, request=proposed,
                       before_sha256=state_hash(before), after_sha256=sha(after))
        staging = Path(tempfile.mkdtemp(prefix='.staging-', dir=operations))
        if before is not None:
            write_new(staging / 'before.csv', before)
        write_new(staging / 'after.csv', after)
        write_new(staging / 'request.json', encode(request))
        sync_directory(staging)
        os.rename(staging, directory)
        sync_directory(operations)
        return finish(root, directory)


def recover(project, request_id):
    root = root_for(project)
    request_name(request_id)
    with locked(root):
        return finish(root, safe(root, 'ffe', 'library', 'operations', request_id), recovered=True)


def run(args):
    if args.command == 'recover':
        if not args.request_id:
            raise ValueError('recover requires request-id')
        print(json.dumps(recover(args.project, args.request_id)))
        return 0
    kwargs = dict(row=csv.load_json(args.row_json) if args.row_json else None,
                  source=args.source.read_bytes() if args.source else None,
                  match_column=args.match_column, match_value=args.match_value, replace_existing=args.replace_existing)
    if args.command == 'preview':
        if not args.operation:
            raise ValueError('preview requires operation')
        print(json.dumps(preview(args.project, args.operation, **kwargs)))
        return 0
    if bool(args.request_id) != bool(args.expected_sha256):
        raise ValueError('request-id and expected-sha256 are required together')
    legacy = args.request_id is None
    request_id = args.request_id or str(uuid.uuid4())
    expected = args.expected_sha256 if not legacy else state_hash(current(root_for(args.project)))
    result = execute(args.project, args.command, request_id, expected, **kwargs)
    result['legacy_generated_request'] = legacy
    print(json.dumps(result))
    return 0
