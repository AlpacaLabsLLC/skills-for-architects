#!/usr/bin/env python3
"""Append-only, project-owned URL clip history.  It never retrieves a URL or adopts a product."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit, unquote
import uuid
import copy


REQUEST = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}')
OUTCOMES = {'success', 'partial', 'blocked', 'login-required', 'not-product', 'file-reference', 'unavailable', 'failed'}
SECRET_KEYS = re.compile(r'(^|[_-])(token|auth|authorization|key|api[_-]?key|signature|sig|credential|password|cookie|session|expires?)($|[_-])|^x-amz-', re.I)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def timestamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def identity(value, label):
    try:
        if not isinstance(value, str) or str(uuid.UUID(value)) != value:
            raise ValueError
    except ValueError as error:
        raise ValueError(label + ' must be a canonical UUID') from error
    return value


def request_id(value):
    if not isinstance(value, str) or not REQUEST.fullmatch(value):
        raise ValueError('Request ID must be 1–80 safe ASCII characters')
    return value


def redact_url(value):
    """Keep non-secret variant identity while ensuring persisted URLs contain no credentials."""
    if not isinstance(value, str) or not value:
        raise ValueError('URL is required')
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise ValueError('Only absolute HTTP(S) URLs are accepted')
    redacted = []
    pairs = []
    for key, item in parse_qsl(parsed.query, keep_blank_values=True):
        if SECRET_KEYS.search(key):
            pairs.append((key, '[REDACTED]'))
            redacted.append('query:' + key)
        else:
            pairs.append((key, item))
    netloc = parsed.hostname
    if parsed.port:
        netloc += ':' + str(parsed.port)
    if parsed.username is not None or parsed.password is not None:
        redacted.append('userinfo')
    # Fragments often select variants. Retain them unless the obvious secret marker is present.
    fragment = unquote(parsed.fragment)
    if SECRET_KEYS.search(fragment) or re.search(r'(token|auth|key|signature|sig|credential|password|session)\s*=', fragment, re.I):
        fragment = '[REDACTED]'
        redacted.append('fragment')
    else:
        fragment = parsed.fragment
    path_parts = parsed.path.split('/')
    for index in range(len(path_parts) - 1):
        if SECRET_KEYS.search(unquote(path_parts[index])):
            path_parts[index + 1] = '[REDACTED]'
            redacted.append('path-secret')
    path = '/'.join(path_parts)
    return {'url': urlunsplit((parsed.scheme, netloc, path, urlencode(pairs, doseq=True), fragment)),
            'redacted_components': list(dict.fromkeys(redacted))}


def redact_url_value(value):
    """Return a persisted URL string; non-URL locators remain locators, not guessed URLs."""
    if not isinstance(value, str):
        return value
    parsed = urlsplit(value)
    return redact_url(value)['url'] if parsed.scheme in ('http', 'https') and parsed.hostname else value


def sanitize_configuration(value, depth=0):
    """Configuration is evidence, never a container for credentials or arbitrary host payloads."""
    if depth > 12:
        raise ValueError('Clip configuration is too deeply nested')
    if value is None or type(value) in (str, int, float, bool):
        if type(value) is float and value != value:
            raise ValueError('Clip configuration contains a non-finite number')
        return redact_url_value(value)
    if isinstance(value, list):
        return [sanitize_configuration(item, depth + 1) for item in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if not isinstance(key, str) or SECRET_KEYS.search(key):
                raise ValueError('Clip configuration cannot persist secret-named fields')
            result[key] = sanitize_configuration(item, depth + 1)
        return result
    raise ValueError('Clip configuration must contain JSON values only')


def sanitize_observation(value):
    """Allow only the producer envelope, after removing secrets from every persisted URL field."""
    def walk(item):
        if isinstance(item, str):
            return redact_url_value(item)
        if isinstance(item, list):
            return [walk(value) for value in item]
        if isinstance(item, dict):
            result = {}
            for key, child in item.items():
                if isinstance(key, str) and SECRET_KEYS.search(key):
                    raise ValueError('Observation cannot persist secret-named fields')
                result[key] = walk(child)
            return result
        return item
    document = walk(copy.deepcopy(value))
    if not isinstance(document, dict):
        raise ValueError('Observation must be an object')
    source = document.get('source')
    if isinstance(source, dict) and source.get('kind') == 'url':
        source['reference'] = redact_url_value(source.get('reference'))
    for field in document.get('fields', []):
        if not isinstance(field, dict):
            continue
        if field.get('kind') == 'image':
            field['value'] = redact_url_value(field.get('value'))
        field['locator'] = redact_url_value(field.get('locator'))
    return document


def root_for(project, one_off=False):
    supplied = Path(project).absolute()
    if one_off:
        if supplied.is_symlink() or not supplied.is_dir():
            raise ValueError('Explicit one-off clip destination must be an existing non-symlink directory')
        return supplied.resolve()
    for candidate in (supplied, *supplied.parents):
        if candidate.is_symlink():
            raise ValueError('Symlink project paths are not supported')
        if (candidate / 'PROJECT.md').is_file():
            return candidate.resolve()
    raise ValueError('no project root found; clip persistence requires PROJECT.md')


def safe(root, *parts):
    path = root.joinpath(*parts)
    if not path.is_relative_to(root) or '..' in path.parts:
        raise ValueError('Path escapes clip project')
    for entry in (path, *path.parents):
        if entry.is_symlink():
            raise ValueError('Symlink clip paths are not supported')
    return path


def sync_directory(path):
    if os.name != 'nt':
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def directories(root):
    base = safe(root, 'ffe', 'clips')
    captures = safe(root, 'ffe', 'clips', 'captures')
    ffe = safe(root, 'ffe')
    ffe.mkdir(exist_ok=True)
    base.mkdir(exist_ok=True)
    captures.mkdir(exist_ok=True)
    sync_directory(root)
    sync_directory(ffe)
    sync_directory(base)
    return base, captures


@contextmanager
def locked(root):
    base, _ = directories(root)
    lock = safe(root, 'ffe', 'clips', '.writer.lock')
    with lock.open('a+b') as handle:
        try:
            if os.name == 'nt':
                import msvcrt
                if handle.tell() == 0:
                    handle.write(b'0'); handle.flush()
                handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError('Another clip-history writer holds the lock; retry after it finishes') from error
        try:
            yield base
        finally:
            if os.name == 'nt':
                handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def event_lines(root):
    path = safe(root, 'ffe', 'clips', 'events.jsonl')
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw and not raw.endswith(b'\n'):
        raise ValueError('Malformed clip log: final event is incomplete')
    result = []
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError('Malformed clip log at line ' + str(number)) from error
        if canonical(event) != line:
            raise ValueError('Noncanonical clip event at line ' + str(number))
        validate_event(event)
        result.append(event)
    return result


def validate_event(event):
    validate_structure(event, 'clip-event.schema.json')
    common = {'schema_version', 'event_id', 'capture_id', 'request_id', 'at', 'action', 'state'}
    if not isinstance(event, dict) or type(event.get('schema_version')) is not int or event.get('schema_version') != 1 or event.get('action') != 'clip':
        raise ValueError('Invalid clip event envelope')
    identity(event.get('event_id'), 'event ID'); identity(event.get('capture_id'), 'capture ID'); request_id(event.get('request_id'))
    try:
        stamp = datetime.fromisoformat(event.get('at', '').replace('Z', '+00:00'))
    except (ValueError, TypeError):
        stamp = None
    if not isinstance(event.get('at'), str) or not event['at'].endswith('Z') or stamp is None or stamp.tzinfo is None:
        raise ValueError('Clip event timestamp must be UTC')
    if event.get('state') == 'started':
        if set(event) != common | {'request', 'prior_capture_id'}:
            raise ValueError('Invalid clip start event')
        validate_request(event['request'])
        if event['prior_capture_id'] is not None:
            identity(event['prior_capture_id'], 'prior capture ID')
    elif event.get('state') == 'terminal':
        if set(event) != common | {'outcome', 'capture_path', 'capture_sha256', 'product'}:
            raise ValueError('Invalid clip terminal event')
        if event['outcome'] not in OUTCOMES or not isinstance(event['capture_path'], str) or not re.fullmatch(r'captures/[0-9a-f-]{36}\.json', event['capture_path']) or not re.fullmatch(r'[a-f0-9]{64}', event['capture_sha256']):
            raise ValueError('Invalid clip terminal reference')
        if not isinstance(event['product'], dict) or set(event['product']) != {'manufacturer', 'model', 'manufacturer_sku', 'vendor_item_id', 'storefront_id'}:
            raise ValueError('Invalid clip terminal projection')
    else:
        raise ValueError('Unknown clip event state')


def validate_request(value):
    validate_structure(value, 'clip-event.schema.json', 'request')
    if not isinstance(value, dict) or set(value) != {'submitted_url', 'configuration', 'fingerprint'}:
        raise ValueError('Invalid clip request')
    if not isinstance(value['submitted_url'], dict) or set(value['submitted_url']) != {'url', 'redacted_components'} or not isinstance(value['submitted_url']['url'], str) or not isinstance(value['submitted_url']['redacted_components'], list) or any(type(item) is not str for item in value['submitted_url']['redacted_components']):
        raise ValueError('Invalid persisted URL')
    if not isinstance(value['configuration'], dict) or not re.fullmatch(r'[a-f0-9]{64}', value['fingerprint']) or value['fingerprint'] != digest(canonical({'submitted_url': value['submitted_url'], 'configuration': value['configuration']})):
        raise ValueError('Invalid clip request fingerprint')
    if redact_url(value['submitted_url']['url'])['url'] != value['submitted_url']['url'] or sanitize_configuration(value['configuration']) != value['configuration']:
        raise ValueError('Persisted request contains unredacted URL or configuration evidence')


def states(events):
    requests, captures, event_ids = {}, {}, set()
    for event in events:
        if event['event_id'] in event_ids:
            raise ValueError('Duplicate clip event identity')
        event_ids.add(event['event_id'])
        if event['state'] == 'started':
            if event['request_id'] in requests or event['capture_id'] in captures:
                raise ValueError('Duplicate clip start identity')
            requests[event['request_id']] = event
            if event['prior_capture_id'] is not None and event['prior_capture_id'] not in captures:
                raise ValueError('Prior capture reference is absent or forward')
            captures[event['capture_id']] = {'start': event, 'terminal': None}
        else:
            state = captures.get(event['capture_id'])
            if state is None or state['start']['request_id'] != event['request_id'] or state['terminal'] is not None:
                raise ValueError('Dangling or duplicate clip terminal event')
            state['terminal'] = event
    return requests, captures


def checked_terminal(root, state):
    terminal, start_event = state['terminal'], state['start']
    if terminal is None:
        return None
    document = read_capture(root, terminal)
    if document['request'] != start_event['request'] or document['outcome'] != terminal['outcome'] or document['product'] != terminal['product']:
        raise ValueError('Terminal event does not match immutable capture')
    return document


def append(base, event):
    path = base / 'events.jsonl'
    data = canonical(event) + b'\n'
    with path.open('ab') as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())
    sync_directory(base)


def start(project, request, request_id_value, prior_capture_id=None, one_off=False):
    root = root_for(project, one_off); request_id(request_id_value)
    if not isinstance(request, dict) or set(request) != {'url', 'configuration'} or not isinstance(request['configuration'], dict):
        raise ValueError('Clip request requires URL and object configuration')
    persisted = {'submitted_url': redact_url(request['url']), 'configuration': sanitize_configuration(request['configuration'])}
    persisted['fingerprint'] = digest(canonical(persisted))
    if prior_capture_id is not None:
        identity(prior_capture_id, 'prior capture ID')
    with locked(root) as base:
        requests, captures = states(event_lines(root))
        if prior_capture_id is not None and prior_capture_id not in captures:
            raise ValueError('Prior capture reference is absent')
        existing = requests.get(request_id_value)
        if existing:
            if existing['request']['fingerprint'] != persisted['fingerprint'] or existing['prior_capture_id'] != prior_capture_id:
                raise ValueError('Request ID reused with different clip inputs')
            checked_terminal(root, captures[existing['capture_id']])
            return {'capture_id': existing['capture_id'], 'request_id': request_id_value,
                    'state': 'replayed-terminal' if captures[existing['capture_id']]['terminal'] else 'started', 'persisted': True}
        capture_id = str(uuid.uuid4())
        event = {'schema_version': 1, 'event_id': str(uuid.uuid4()), 'capture_id': capture_id,
                 'request_id': request_id_value, 'at': timestamp(), 'action': 'clip', 'state': 'started',
                 'request': persisted, 'prior_capture_id': prior_capture_id}
        append(base, event)
        return {'capture_id': capture_id, 'request_id': request_id_value, 'state': 'started', 'persisted': True}


def observation_module():
    import importlib.util
    path = Path(__file__).resolve().parents[1] / 'transformers/product_observations.py'
    spec = importlib.util.spec_from_file_location('product_observations', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def validate_structure(value, filename, definition=None):
    """Use closed published schemas; resolve only the bundled observation dependency."""
    module = observation_module()
    schema = json.loads((Path(__file__).resolve().parents[2] / 'schema' / filename).read_text(encoding='utf-8'))
    def relocate(item):
        if isinstance(item, list):
            return [relocate(child) for child in item]
        if isinstance(item, dict):
            return {key: ('#/$defs/observation' + child[1:] if key == '$ref' and child.startswith('#') else relocate(child))
                    for key, child in item.items()}
        return item
    def dependencies(item):
        if isinstance(item, list):
            return [dependencies(child) for child in item]
        if isinstance(item, dict):
            if item.get('$ref') == 'product-observation.schema.json':
                return {'$ref': '#/$defs/observation'}
            return {key: dependencies(child) for key, child in item.items()}
        return item
    schema = dependencies(schema)
    if filename == 'clip-capture.schema.json':
        schema['$defs']['observation'] = relocate(json.loads(module.SCHEMA.read_text(encoding='utf-8')))
    rule = schema['$defs'][definition] if definition else schema
    module.check(value, rule, schema)


def artifact(capture_id, request_value, outcome, observation, resolved_url, canonical_url, as_version=None, as_digest=None, extractor_version=None):
    if outcome not in OUTCOMES:
        raise ValueError('Unknown capture outcome')
    urls = {'resolved_url': redact_url(resolved_url) if resolved_url else None,
            'canonical_url': redact_url(canonical_url) if canonical_url else None}
    product = {'manufacturer': None, 'model': None, 'manufacturer_sku': None, 'vendor_item_id': None, 'storefront_id': None}
    observation_sha256 = None
    if observation is not None:
        observation = sanitize_observation(observation)
        result = observation_module().validate(observation)
        observation_sha256 = result['sha256']
        product = dict(observation['product'])
    return {'schema_version': 1, 'capture_id': capture_id, 'request_id': request_value['request_id'],
            'created_at': timestamp(), 'outcome': outcome, 'request': request_value['request'],
            'urls': urls, 'observation': observation, 'observation_sha256': observation_sha256,
            'product': product, 'provenance': {'as_version': as_version, 'as_digest': as_digest, 'extractor_version': extractor_version},
            'adoption_performed': False, 'retrieval_performed_by_helper': False}


def publish_capture(root, document):
    captures = safe(root, 'ffe', 'clips', 'captures')
    target = safe(root, 'ffe', 'clips', 'captures', document['capture_id'] + '.json')
    data = canonical(document) + b'\n'
    if target.exists():
        if target.read_bytes() != data:
            raise ValueError('Capture identity collision')
        return target, digest(data)
    fd, temporary = tempfile.mkstemp(prefix='.capture-', dir=captures)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            if target.read_bytes() != data:
                raise ValueError('Capture identity collision')
        sync_directory(captures)
    finally:
        os.unlink(temporary)
    actual = target.read_bytes()
    if actual != data:
        raise ValueError('Capture artifact readback differs')
    return target, digest(actual)


def read_capture(root, terminal):
    path = safe(root, 'ffe', 'clips', terminal['capture_path'])
    data = path.read_bytes()
    if digest(data) != terminal['capture_sha256'] or not data.endswith(b'\n'):
        raise ValueError('Capture artifact checksum mismatch')
    document = json.loads(data)
    if canonical(document) + b'\n' != data or document.get('capture_id') + '.json' != path.name:
        raise ValueError('Malformed capture artifact')
    validate_capture(document, terminal['capture_id'], terminal['request_id'])
    return document


def validate_capture(document, capture_id, request_id_value):
    validate_structure(document, 'clip-capture.schema.json')
    required = {'schema_version', 'capture_id', 'request_id', 'created_at', 'outcome', 'request', 'urls', 'observation',
                'observation_sha256', 'product', 'provenance', 'adoption_performed', 'retrieval_performed_by_helper'}
    if not isinstance(document, dict) or set(document) != required or document.get('schema_version') != 1:
        raise ValueError('Invalid capture artifact envelope')
    if document['capture_id'] != capture_id or document['request_id'] != request_id_value or document['outcome'] not in OUTCOMES:
        raise ValueError('Capture artifact identity or outcome mismatch')
    validate_request(document['request'])
    if not isinstance(document['urls'], dict) or set(document['urls']) != {'resolved_url', 'canonical_url'}:
        raise ValueError('Invalid capture URL evidence')
    for item in document['urls'].values():
        if item is not None and (not isinstance(item, dict) or set(item) != {'url', 'redacted_components'}):
            raise ValueError('Invalid capture URL evidence')
        if item is not None and redact_url(item['url'])['url'] != item['url']:
            raise ValueError('Persisted capture URL is not redacted')
    if document['observation'] is None:
        if document['observation_sha256'] is not None:
            raise ValueError('Absent observation has a hash')
    else:
        if sanitize_observation(document['observation']) != document['observation']:
            raise ValueError('Persisted observation contains unredacted URL evidence')
        result = observation_module().validate(document['observation'])
        if result['sha256'] != document['observation_sha256']:
            raise ValueError('Capture observation hash mismatch')
    product_keys = {'manufacturer', 'model', 'manufacturer_sku', 'vendor_item_id', 'storefront_id'}
    if not isinstance(document['product'], dict) or set(document['product']) != product_keys or any(value is not None and not isinstance(value, str) for value in document['product'].values()):
        raise ValueError('Invalid capture product projection')
    if not isinstance(document['provenance'], dict) or set(document['provenance']) != {'as_version', 'as_digest', 'extractor_version'} or any(value is not None and not isinstance(value, str) for value in document['provenance'].values()):
        raise ValueError('Invalid capture provenance identity')
    if document['adoption_performed'] is not False or document['retrieval_performed_by_helper'] is not False:
        raise ValueError('Capture helper must not retrieve or adopt')


def finish(project, request_id_value, outcome, observation=None, resolved_url=None, canonical_url=None, as_version=None, as_digest=None, extractor_version=None, one_off=False):
    root = root_for(project, one_off); request_id(request_id_value)
    with locked(root) as base:
        requests, captures = states(event_lines(root))
        start_event = requests.get(request_id_value)
        if start_event is None:
            raise ValueError('Unknown clip request; append attempt-start first')
        state = captures[start_event['capture_id']]
        if state['terminal'] is not None:
            checked_terminal(root, state)
            return {'capture_id': start_event['capture_id'], 'request_id': request_id_value,
                    'state': 'replayed-terminal', 'persisted': True, 'outcome': state['terminal']['outcome']}
        document = artifact(start_event['capture_id'], start_event, outcome, observation, resolved_url, canonical_url, as_version, as_digest, extractor_version)
        validate_capture(document, start_event['capture_id'], request_id_value)
        target, checksum = publish_capture(root, document)
        if target.read_bytes() != canonical(document) + b'\n':
            raise ValueError('Capture artifact fresh readback differs')
        terminal = {'schema_version': 1, 'event_id': str(uuid.uuid4()), 'capture_id': start_event['capture_id'],
                    'request_id': request_id_value, 'at': timestamp(), 'action': 'clip', 'state': 'terminal',
                    'outcome': outcome, 'capture_path': str(target.relative_to(base)), 'capture_sha256': checksum,
                    'product': document['product']}
        append(base, terminal)
        return {'capture_id': start_event['capture_id'], 'request_id': request_id_value, 'state': 'terminal',
                'outcome': outcome, 'capture_sha256': checksum, 'persisted': True}


def recover(project, request_id_value, one_off=False):
    root = root_for(project, one_off); request_id(request_id_value)
    with locked(root) as base:
        requests, captures = states(event_lines(root))
        start_event = requests.get(request_id_value)
        if start_event is None:
            raise ValueError('Unknown clip request')
        state = captures[start_event['capture_id']]
        if state['terminal'] is not None:
            checked_terminal(root, state)
            return {'capture_id': start_event['capture_id'], 'state': 'replayed-terminal', 'outcome': state['terminal']['outcome']}
        target = safe(root, 'ffe', 'clips', 'captures', start_event['capture_id'] + '.json')
        if not target.exists():
            return {'capture_id': start_event['capture_id'], 'state': 'incomplete', 'persisted': True}
        raw = target.read_bytes()
        document = json.loads(raw)
        if document.get('capture_id') != start_event['capture_id'] or document.get('request_id') != request_id_value:
            raise ValueError('Orphan capture artifact does not match pending request')
        if canonical(document) + b'\n' != raw:
            raise ValueError('Malformed capture artifact')
        validate_capture(document, start_event['capture_id'], request_id_value)
        if document['request'] != start_event['request']:
            raise ValueError('Recovered capture request differs from attempt-start')
        sync_directory(target.parent)
        checksum = digest(raw)
        terminal = {'schema_version': 1, 'event_id': str(uuid.uuid4()), 'capture_id': start_event['capture_id'], 'request_id': request_id_value,
                    'at': timestamp(), 'action': 'clip', 'state': 'terminal', 'outcome': document['outcome'],
                    'capture_path': str(target.relative_to(base)), 'capture_sha256': checksum, 'product': document['product']}
        append(base, terminal)
        return {'capture_id': start_event['capture_id'], 'state': 'recovered-terminal', 'outcome': document['outcome']}


def history(project, url=None, outcome=None, product=None, date_from=None, date_to=None, one_off=False):
    root = root_for(project, one_off)
    if outcome is not None and outcome not in OUTCOMES:
        raise ValueError('Unknown capture outcome')
    needle = redact_url(url)['url'] if url else None
    def date(value):
        return datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None
    lower, upper = date(date_from), date(date_to)
    _, captures = states(event_lines(root))
    result = []
    for capture_id in sorted(captures):
        state = captures[capture_id]
        if state['terminal'] is None:
            if (lower and datetime.fromisoformat(state['start']['at'].replace('Z', '+00:00')) < lower) or (upper and datetime.fromisoformat(state['start']['at'].replace('Z', '+00:00')) > upper):
                continue
            result.append({'capture_id': capture_id, 'request_id': state['start']['request_id'], 'state': 'incomplete', 'submitted_url': state['start']['request']['submitted_url']['url']})
            continue
        document = checked_terminal(root, state)
        created = datetime.fromisoformat(document['created_at'].replace('Z', '+00:00'))
        if (lower and created < lower) or (upper and created > upper):
            continue
        if needle and needle not in (document['request']['submitted_url']['url'], (document['urls']['resolved_url'] or {}).get('url'), (document['urls']['canonical_url'] or {}).get('url')):
            continue
        if outcome and document['outcome'] != outcome:
            continue
        if product and product.casefold() not in ' '.join(str(v or '') for v in document['product'].values()).casefold():
            continue
        result.append({'capture_id': capture_id, 'request_id': document['request_id'], 'outcome': document['outcome'],
                       'product': document['product'], 'submitted_url': document['request']['submitted_url']['url'],
                       'capture_sha256': state['terminal']['capture_sha256']})
    return {'captures': result, 'network_performed': False, 'adoption_performed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('start', 'finish', 'recover', 'history'))
    parser.add_argument('--project'); parser.add_argument('--destination'); parser.add_argument('--request-id'); parser.add_argument('--url')
    parser.add_argument('--configuration-json', default='{}'); parser.add_argument('--prior-capture-id')
    parser.add_argument('--outcome', choices=sorted(OUTCOMES)); parser.add_argument('--observation-json', type=Path)
    parser.add_argument('--resolved-url'); parser.add_argument('--canonical-url'); parser.add_argument('--product'); parser.add_argument('--date-from'); parser.add_argument('--date-to')
    parser.add_argument('--as-version'); parser.add_argument('--as-digest'); parser.add_argument('--extractor-version')
    args = parser.parse_args()
    try:
        if bool(args.project) == bool(args.destination): raise ValueError('Provide exactly one project or explicit one-off destination')
        target, one_off = (args.destination, True) if args.destination else (args.project, False)
        if args.command == 'start':
            result = start(target, {'url': args.url, 'configuration': json.loads(args.configuration_json)}, args.request_id, args.prior_capture_id, one_off)
        elif args.command == 'finish':
            observation = json.loads(args.observation_json.read_text(encoding='utf-8')) if args.observation_json else None
            result = finish(target, args.request_id, args.outcome, observation, args.resolved_url, args.canonical_url, args.as_version, args.as_digest, args.extractor_version, one_off)
        elif args.command == 'recover': result = recover(target, args.request_id, one_off)
        else: result = history(target, args.url, args.outcome, args.product, args.date_from, args.date_to, one_off)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as error:
        parser.exit(2, 'clip log refused: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
