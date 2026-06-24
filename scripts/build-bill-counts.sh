#!/usr/bin/env bash
set -euo pipefail

repos_dir="${1:?Usage: build-bill-counts.sh REPOS_DIR OUTPUT_JSON}"
output_json="${2:?Usage: build-bill-counts.sh REPOS_DIR OUTPUT_JSON}"

python3 "$(dirname "$0")/build-govbot-data.py" "$repos_dir" "$output_json"
