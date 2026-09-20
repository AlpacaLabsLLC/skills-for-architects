#!/bin/bash
# Stages this case's fixtures into the run's working directory.
# context.add_dirs only grants reads at the case's own path, which the agent
# cannot resolve from an empty workspace; the runner runs this script in the
# workspace instead. Requires `--scaffold` on the eval command.
set -euo pipefail
mkdir -p fixtures
cp "$(dirname "$0")/fixtures/"* fixtures/
