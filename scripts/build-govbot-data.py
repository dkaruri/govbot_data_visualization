#!/usr/bin/env python3
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone


def parse_date(value):
    if not isinstance(value, str) or not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        try:
            return datetime.fromisoformat(text[:10])
        except ValueError:
            return None


def metadata_paths(repo_path):
    for dirpath, dirnames, filenames in os.walk(repo_path):
        if ".git" in dirnames:
            dirnames.remove(".git")
        normalized = dirpath.replace(os.sep, "/")
        if "metadata.json" in filenames and "/bills/" in normalized:
            yield os.path.join(dirpath, "metadata.json")


def first_bill_date(metadata):
    dates = []
    for collection in ("actions", "versions", "documents"):
        for item in metadata.get(collection, []) or []:
            if isinstance(item, dict):
                parsed = parse_date(item.get("date"))
                if parsed is not None:
                    dates.append(parsed.replace(tzinfo=None))
    return min(dates) if dates else None


def main():
    if len(sys.argv) != 3:
        print("Usage: build-govbot-data.py REPOS_DIR OUTPUT_JSON", file=sys.stderr)
        return 2

    repos_dir = sys.argv[1]
    output_json = sys.argv[2]
    source_url = os.environ.get("GOVBOT_SOURCE_URL", "https://chihacknight.github.io/govbot/")

    rows = []
    monthly = Counter()

    for repo in sorted(os.listdir(repos_dir)):
        repo_path = os.path.join(repos_dir, repo)
        if not repo.endswith("-legislation") or not os.path.isdir(repo_path):
            continue

        count = 0
        for path in metadata_paths(repo_path):
            count += 1
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    metadata = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue

            first_date = first_bill_date(metadata)
            if first_date is not None:
                monthly[first_date.strftime("%Y-%m")] += 1

        rows.append({
            "repo": repo,
            "state": repo.removesuffix("-legislation").upper(),
            "count": count,
        })

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source_url,
        "rows": rows,
        "monthly_totals": [
            {"month": month, "count": monthly[month]}
            for month in sorted(monthly)
        ],
    }

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
