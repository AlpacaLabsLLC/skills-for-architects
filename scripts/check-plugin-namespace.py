#!/usr/bin/env python3
"""Compatibility entry point; canonical implementation is a shared tool."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools/validators/check-plugin-namespace.py"), run_name="__main__")
