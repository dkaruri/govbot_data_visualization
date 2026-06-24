#!/usr/bin/env bash
set -euo pipefail

repos_dir="${1:?Usage: build-bill-counts.sh REPOS_DIR OUTPUT_JSON}"
output_json="${2:?Usage: build-bill-counts.sh REPOS_DIR OUTPUT_JSON}"
source_url="${GOVBOT_SOURCE_URL:-https://github.com/chihacknight/govbot/tree/main/docs}"

mkdir -p "$(dirname "$output_json")"

tmp_file="$(mktemp)"
trap 'rm -f "$tmp_file"' EXIT

{
  printf '{\n'
  printf '  "generated_at": "%s",\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  printf '  "source": "%s",\n' "$source_url"
  printf '  "rows": [\n'

  first=1
  find "$repos_dir" -mindepth 1 -maxdepth 1 -type d -name '*-legislation' -printf '%f\n' | sort | while IFS= read -r repo; do
    count="$(
      find "$repos_dir/$repo" \
        -path '*/.git' -prune -o \
        -path '*/bills/*/metadata.json' -type f -print \
        | wc -l
    )"
    state="${repo%-legislation}"
    state="$(printf '%s' "$state" | tr '[:lower:]' '[:upper:]')"

    if [[ "$first" -eq 0 ]]; then
      printf ',\n'
    fi
    first=0
    printf '    {"repo":"%s","state":"%s","count":%s}' "$repo" "$state" "$count"
  done

  printf '\n  ]\n'
  printf '}\n'
} > "$tmp_file"

mv "$tmp_file" "$output_json"
