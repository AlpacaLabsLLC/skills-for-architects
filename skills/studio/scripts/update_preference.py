#!/usr/bin/env python3
"""Current local version-check preference; explicit destination, no environment routing."""
from pathlib import Path


def dispatch(operation, request):
    command = operation.split('.')[-1]
    if command not in ('status', 'enable', 'disable'):
        raise ValueError('Unknown update preference operation')
    directory = Path(request['state_directory']).expanduser().resolve()
    enabled = directory / '.architecture-studio-update-check-enabled'
    cache = directory / '.architecture-studio-version-check'
    if enabled.is_symlink() or cache.is_symlink():
        raise ValueError('Preference symlink targets are not supported')
    if command == 'enable':
        directory.mkdir(parents=True, exist_ok=True)
        with enabled.open('a'):
            pass
        enabled.chmod(0o600)
        cache.unlink(missing_ok=True)
    elif command == 'disable':
        enabled.unlink(missing_ok=True)
    return {'enabled': enabled.is_file(), 'state_directory': str(directory)}
