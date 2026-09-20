#!/usr/bin/env python3
"""Preview and apply one explicitly approved Arch Studio instruction block, without host discovery.

The host must verify its instruction mechanism, selected scope/target and the user's
approval of the exact diff. A matching digest binds that approval input to these
bytes; this helper cannot authenticate a human or guarantee future skill selection.
Python 3.10+, standard library only. Never run apply for a declined/cancelled offer.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat
import secrets

START = '<!-- architecture-studio:default-preference:start -->'
END = '<!-- architecture-studio:default-preference:end -->'
FAMILY = '<!-- architecture-studio:default-preference:'
PREFERENCE = ('For architecture and Arch Studio-managed project work, use the connected Arch Studio MCP '
              'through Norma, its coordinator. When the user asks for Norma, discover that coordinator. '
              'Use host-native execution as appropriate; preserve project-context and permission requirements. '
              'If Arch Studio is unavailable, disclose it and offer a fallback without blocking unrelated work.')
MAX_BYTES = 1024 * 1024
MAX_PLAN_BYTES = 4 * MAX_BYTES


class PreferenceError(ValueError):
    pass


def digest(data: bytes) -> str:
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def plan_digest(plan: dict) -> str:
    return digest(json.dumps({k: v for k, v in plan.items() if k != 'plan_sha256'},
                             sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode())


def target_path(target: str | Path) -> Path:
    raw = str(target)
    if any(ord(c) < 32 for c in raw):
        raise PreferenceError('target contains a control character')
    path = Path(raw)
    if not path.is_absolute() or '..' in path.parts:
        raise PreferenceError('target must be an explicit absolute instruction-file path without parent traversal')
    for parent in reversed(path.parents):
        try:
            info = parent.lstat()
        except OSError as error:
            raise PreferenceError('instruction parent is unavailable; no folders were created') from error
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise PreferenceError('instruction ancestors must be existing real directories, not symlinks')
    return path


def snapshot(path: Path, parent_fd: int | None = None) -> tuple[bytes, dict]:
    if not hasattr(os, 'O_NOFOLLOW'):
        raise PreferenceError('this helper requires POSIX no-follow file access; use a verified native host editor')
    try:
        fd = os.open(path.name if parent_fd is not None else path,
                     os.O_RDONLY | os.O_NOFOLLOW | getattr(os, 'O_NONBLOCK', 0), dir_fd=parent_fd)
    except FileNotFoundError:
        # Broken symlinks must not masquerade as absent instruction files.
        if parent_fd is None and path.is_symlink():
            raise PreferenceError('instruction target must not be a symlink')
        return b'', {'exists': False, 'mode': None, 'device': None, 'inode': None}
    except OSError as error:
        raise PreferenceError('instruction target is unavailable or is a symlink') from error
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
            raise PreferenceError('instruction target must be a regular, single-link file owned by this user')
        if info.st_size > MAX_BYTES:
            raise PreferenceError('instruction target exceeds the 1 MiB bound')
        data = b''
        while len(data) <= MAX_BYTES:
            chunk = os.read(fd, min(65536, MAX_BYTES + 1 - len(data)))
            if not chunk:
                break
            data += chunk
        if len(data) > MAX_BYTES:
            raise PreferenceError('instruction target exceeds the 1 MiB bound')
        return data, {'exists': True, 'mode': stat.S_IMODE(info.st_mode), 'device': info.st_dev, 'inode': info.st_ino}
    finally:
        os.close(fd)


def transform(data: bytes, action: str) -> bytes:
    if action not in ('enable', 'remove'):
        raise PreferenceError('action must be enable or remove')
    try:
        text = data.decode('utf-8')
    except UnicodeError as error:
        raise PreferenceError('instruction target must be UTF-8 text') from error
    start_count, end_count = text.count(START), text.count(END)
    if (start_count, end_count, text.count(FAMILY)) not in ((0, 0, 0), (1, 1, 2)):
        raise PreferenceError('duplicate, partial or malformed Arch Studio preference markers; preserve the file for review')
    span = None
    if start_count:
        # A leading UTF-8 BOM belongs to the original file, outside the block.
        marker_text = text[1:] if text.startswith('\ufeff') else text
        prefix = 1 if text.startswith('\ufeff') else 0
        starts = list(re.finditer(r'(?m)^' + re.escape(START) + r'\r?$', marker_text))
        ends = list(re.finditer(r'(?m)^' + re.escape(END) + r'\r?$', marker_text))
        if len(starts) != 1 or len(ends) != 1 or starts[0].end() >= ends[0].start():
            raise PreferenceError('Arch Studio preference markers must be complete, ordered, separate lines')
        finish = ends[0].end()
        if marker_text[finish:finish + 1] == '\n':
            finish += 1
        span = (starts[0].start() + prefix, finish + prefix)
    newline = '\r\n' if '\r\n' in text else '\n'
    block = START + newline + PREFERENCE + newline + END + newline
    if span:
        replacement = '' if action == 'remove' else block
        text = text[:span[0]] + replacement + text[span[1]:]
    elif action == 'enable':
        # Prepending an owned block preserves every original byte, including the
        # final newline state. Removal consumes only the owned block's newline.
        text = ('\ufeff' + block + text[1:]) if text.startswith('\ufeff') else block + text
    return text.encode('utf-8')


def preview(target: str | Path, scope: str, action: str) -> dict:
    if scope not in ('project', 'user'):
        raise PreferenceError('scope must be the host-confirmed project or user scope')
    path = target_path(target)
    before, identity = snapshot(path)
    after = transform(before, action)
    if len(after) > MAX_BYTES:
        raise PreferenceError('proposed instruction file exceeds the 1 MiB bound; no edit was made')
    delta = ''.join(line if line.endswith('\n') else line + '\n\\ No newline at end of file\n'
                    for line in difflib.unified_diff(before.decode('utf-8').splitlines(keepends=True),
                                                    after.decode('utf-8').splitlines(keepends=True),
                                                    fromfile=str(path), tofile=str(path), n=0))
    parent = path.parent.stat()
    plan = {'schema_version': 1, 'target': str(path), 'scope': scope, 'action': action,
            'parent_identity': {'device': parent.st_dev, 'inode': parent.st_ino},
            'source_identity': identity, 'before_sha256': digest(before), 'after_sha256': digest(after),
            'operation': 'noop' if before == after else 'update' if identity['exists'] else 'create',
            'diff': delta}
    plan['plan_sha256'] = plan_digest(plan)
    if len(json.dumps(plan, indent=2, ensure_ascii=True).encode()) + 1 > MAX_PLAN_BYTES:
        raise PreferenceError('proposed review plan exceeds the 4 MiB bound; no edit was made')
    return plan


def apply(plan: dict, approval_digest: str) -> dict:
    if not isinstance(plan, dict) or set(plan) != {'schema_version', 'target', 'scope', 'action', 'parent_identity', 'source_identity', 'before_sha256', 'after_sha256', 'operation', 'diff', 'plan_sha256'}:
        raise PreferenceError('invalid preference plan')
    if not isinstance(approval_digest, str) or not isinstance(plan['plan_sha256'], str) or not hmac.compare_digest(plan_digest(plan), plan['plan_sha256']) or not hmac.compare_digest(plan['plan_sha256'], approval_digest):
        raise PreferenceError('approval digest does not match the exact reviewed plan')
    current = preview(plan['target'], plan['scope'], plan['action'])
    if current != plan or current['plan_sha256'] != plan['plan_sha256']:
        raise PreferenceError('stale or edited plan; read the current file and obtain approval of a new exact diff')
    path = target_path(plan['target'])
    before, identity = snapshot(path)
    after = transform(before, plan['action'])
    if digest(before) != plan['before_sha256'] or identity != plan['source_identity']:
        raise PreferenceError('instruction target changed during verification')
    if before != after:
        if identity['exists'] and not identity['mode'] & stat.S_IWUSR:
            raise PreferenceError('instruction file is read-only; no permissions were changed')
        temporary = None
        parent_fd = None
        try:
            parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            parent = os.fstat(parent_fd)
            if {'device': parent.st_dev, 'inode': parent.st_ino} != plan['parent_identity']:
                raise PreferenceError('instruction parent changed since preview')
            temporary = '.as-preference-' + secrets.token_hex(16)
            fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent_fd)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(after)
                stream.flush()
                os.fchmod(stream.fileno(), identity['mode'] if identity['exists'] else 0o600)
                os.fsync(stream.fileno())
            target_path(path)  # Recheck ancestors immediately before publication.
            named_parent = path.parent.lstat()
            if not stat.S_ISDIR(named_parent.st_mode) or {'device': named_parent.st_dev, 'inode': named_parent.st_ino} != plan['parent_identity']:
                raise PreferenceError('instruction parent namespace changed before publication')
            latest, latest_identity = snapshot(path, parent_fd)
            if latest != before or latest_identity != identity:
                raise PreferenceError('instruction target changed before publication')
            if identity['exists']:
                os.replace(temporary, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            else:
                # Exclusive create: an intervening file is never overwritten.
                os.link(temporary, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd, follow_symlinks=False)
                os.unlink(temporary, dir_fd=parent_fd)
            temporary = None
        except OSError as error:
            raise PreferenceError('instruction update failed; inspect the target before retrying') from error
        finally:
            if temporary is not None:
                try:
                    os.unlink(temporary, dir_fd=parent_fd)
                except FileNotFoundError:
                    pass
            if parent_fd is not None:
                os.close(parent_fd)
    actual, _ = snapshot(path)
    if actual != after:
        raise PreferenceError('instruction readback differs; do not claim preference completion')
    return {'status': 'unchanged' if before == after else 'preference-bytes-updated',
            'target': str(path), 'scope': plan['scope'], 'action': plan['action'],
            'plan_sha256': plan['plan_sha256'], 'sha256': digest(actual),
            'host_approval': 'provided-digest-matched; host must verify human approval',
            'norma_registration': 'not-performed', 'future_selection': 'not-verified'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    make = commands.add_parser('preview')
    make.add_argument('--target', required=True)
    make.add_argument('--scope', choices=('project', 'user'), required=True)
    make.add_argument('--action', choices=('enable', 'remove'), required=True)
    use = commands.add_parser('apply')
    use.add_argument('--plan', required=True, help='exact JSON preview saved by the host in authorized scratch space')
    use.add_argument('--approval-digest', required=True, help='digest independently retained when the user approved the exact diff')
    args = parser.parse_args()
    try:
        if args.command == 'preview':
            result = preview(args.target, args.scope, args.action)
        else:
            with Path(args.plan).open('rb') as stream:
                raw = stream.read(MAX_PLAN_BYTES + 1)
            if len(raw) > MAX_PLAN_BYTES:
                raise PreferenceError('plan exceeds the 4 MiB bound')
            result = apply(json.loads(raw), args.approval_digest)
        print(json.dumps(result, indent=2, ensure_ascii=True))
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, 'preference error: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
