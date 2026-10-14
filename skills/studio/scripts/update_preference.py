#!/usr/bin/env python3
"""Current local version-check preference; explicit destination, no environment routing."""
from pathlib import Path


def dispatch(operation, request):
    command = operation.split('.')[-1]
    if command not in ('status', 'enable', 'disable'):
        raise ValueError('Unknown update preference operation')
    directory = Path(request['state_directory']).expanduser().resolve()
    disabled = directory / '.architecture-studio-update-check-disabled'
    cache = directory / '.architecture-studio-version-check'
    if disabled.is_symlink() or cache.is_symlink():
        raise ValueError('Preference symlink targets are not supported')
    if command == 'enable':
        disabled.unlink(missing_ok=True)
        cache.unlink(missing_ok=True)
    elif command == 'disable':
        directory.mkdir(parents=True, exist_ok=True)
        with disabled.open('a'):
            pass
        disabled.chmod(0o600)
    return {'enabled': not disabled.is_file(), 'state_directory': str(directory)}
