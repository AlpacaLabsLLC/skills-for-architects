#!/bin/sh
# Run a hook script with a Python that works inside the Rhino AI panel.
# The panel passes Rhino's PYTHONHOME and a minimal PATH to hooks, so use absolute
# interpreter paths and -I (isolated: ignores PYTHON* variables).
# Prefer Rhino 9's bundled Python; fall back to the system one only when Apple's
# Command Line Tools are installed (otherwise /usr/bin/python3 opens an install prompt).
# No interpreter: exit 0, so a hook can never trap the user. macOS only; Windows separate.
for PY in "$HOME"/.rhinocode/py*-rh9/python3.[0-9]*; do
  [ -x "$PY" ] && exec "$PY" -I "$@"
done
if [ -x /usr/bin/python3 ] && /usr/bin/xcode-select -p >/dev/null 2>&1; then
  exec /usr/bin/python3 -I "$@"
fi
exit 0
