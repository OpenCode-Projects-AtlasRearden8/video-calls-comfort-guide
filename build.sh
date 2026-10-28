#!/usr/bin/env bash
# Build the Video Calls, Calm static site from docs/ into site/.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 build.py "$@"
