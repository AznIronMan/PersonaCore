#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/export_public_baseline.sh OUTPUT_DIR

Create a fresh public-safe PersonaConsole working tree in OUTPUT_DIR.
The script copies only allowlisted public distribution paths, then runs
path and content checks. It does not copy git history and does not push.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$1"

if [[ -e "$output_dir" ]]; then
  if [[ ! -d "$output_dir" ]]; then
    echo "error: output path exists and is not a directory: $output_dir" >&2
    exit 1
  fi
  if find "$output_dir" -mindepth 1 -maxdepth 1 | read -r _; then
    echo "error: output directory must be empty: $output_dir" >&2
    exit 1
  fi
fi

mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"

allowed_paths=(
  ".gitignore"
  "README.md"
  "pyproject.toml"
  "docs"
  "examples"
  "scripts"
  "src"
  "tests"
)

for path in "${allowed_paths[@]}"; do
  source_path="$repo_root/$path"
  [[ -e "$source_path" ]] || continue
  if [[ -d "$source_path" ]]; then
    mkdir -p "$output_dir/$path"
    rsync -a \
      --exclude '__pycache__/' \
      --exclude '.pytest_cache/' \
      --exclude '.syncthing*' \
      --exclude '.stfolder/' \
      --exclude '.stignore' \
      --exclude '*.egg-info/' \
      --exclude 'build/' \
      --exclude 'dist/' \
      --exclude '*.pyc' \
      --exclude '*.pyo' \
      --exclude '.DS_Store' \
      "$source_path/" "$output_dir/$path/"
  else
    mkdir -p "$output_dir/$(dirname "$path")"
    cp "$source_path" "$output_dir/$path"
  fi
done

blocked_path_matches="$(
  find "$output_dir" \
    \( -name '.git' \
    -o -name '.private' \
    -o -name '.tasks' \
    -o -name '.env' \
    -o -name '.env.*' \
    -o -name 'AGENTS.md' \
    -o -name '.syncthing*' \
    -o -name '.stfolder' \
    -o -name '.stignore' \
    -o -name '*.db' \
    -o -name '*.sqlite' \
    -o -name '*.sqlite3' \) \
    -print
)"
if [[ -n "$blocked_path_matches" ]]; then
  echo "error: blocked local/private paths were copied:" >&2
  echo "$blocked_path_matches" >&2
  exit 1
fi

scan_pattern='(/Users/|/home/[A-Za-z0-9._-]+/|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|DATABASE_URL=.*://|PASSWORD=|TOKEN=|SECRET=|PRIVATE_KEY=)'
if command -v rg >/dev/null 2>&1; then
  if rg -n --hidden --glob '!**/scripts/export_public_baseline.sh' "$scan_pattern" "$output_dir"; then
    echo "error: generic private path or secret pattern matched in export" >&2
    exit 1
  fi
else
  echo "warning: rg is not installed; skipped content scan" >&2
fi

release_version="$(
  python3 - "$output_dir/pyproject.toml" <<'PY'
import sys
import tomllib

with open(sys.argv[1], "rb") as handle:
    data = tomllib.load(handle)

print(data["project"]["version"])
PY
)"

cat <<EOF
Exported public baseline to:
  $output_dir

Next steps:
  cd "$output_dir"
  git init
  git add .
  git commit -m "Start sanitized PersonaConsole public baseline"
  git tag v$release_version
  git remote add origin https://github.com/AznIronMan/PersonaConsole.git

Push only after reviewing the exported tree.
EOF
