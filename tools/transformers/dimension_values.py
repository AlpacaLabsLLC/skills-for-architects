#!/usr/bin/env python3
"""Normalize explicitly mapped dimensional values; never infer units or axis order."""
import argparse
import copy
from decimal import Decimal
import json
import math
from pathlib import Path

MM = {'mm': Decimal('1'), 'cm': Decimal('10'), 'm': Decimal('1000'),
      'in': Decimal('25.4'), 'ft': Decimal('304.8')}


def normalize(source, target_unit=None):
    if not isinstance(source, dict) or not isinstance(source.get('raw'), str) or not source['raw'].strip():
        raise ValueError('Raw dimension evidence required')
    axes = source.get('axes', {})
    if not isinstance(axes, dict):
        raise ValueError('Explicit axis mapping required')
    for value in axes.values():
        try:
            valid = type(value) in (int, float) and math.isfinite(value) and value > 0
        except OverflowError:
            valid = False
        if not valid:
            raise ValueError('Dimension values must be finite positive numbers, not guesses or booleans')
    result = dict(source=copy.deepcopy(source), axes={}, unit=None, status='unresolved')
    meaning = source.get('meaning')
    if not axes or set(axes) - {'W', 'D', 'H'} or not isinstance(source.get('unit'), str) or source['unit'] not in MM or meaning not in ('overall', 'cutout', 'clearance', 'shipping', 'assembly', 'rough-in'):
        result['reason'] = 'Explicit W/D/H mapping, supported source unit and dimensional meaning required'
        return result
    unit = target_unit or source['unit']
    if unit not in MM:
        raise ValueError('Unsupported target unit')
    factor = MM[source['unit']] / MM[unit]
    result.update(axes={axis: float(Decimal(str(value))*factor) for axis, value in axes.items()},
                  unit=unit, status='normalized', missing_axes=sorted({'W', 'D', 'H'} - axes.keys()))
    if any(not math.isfinite(value) or value <= 0 for value in result['axes'].values()):
        raise ValueError('Conversion exceeds supported finite numeric range')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--unit', choices=sorted(MM))
    args = parser.parse_args()
    try:
        print(json.dumps(normalize(json.loads(args.input.read_text(encoding='utf-8')), args.unit), allow_nan=False))
    except (ValueError, TypeError, OSError) as error:
        parser.exit(2, str(error) + '\n')
