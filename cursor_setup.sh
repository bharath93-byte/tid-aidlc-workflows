#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: ./cursor_setup.sh [options]

Default (no --aws-aidlc):
  Copy contents of tid-aidlc/ into the target .cursor folder.

Options:
  --aws-aidlc  Install AWS AI-DLC rules instead of tid-aidlc
  -g           Install into the global ~/.cursor folder
               (default: ./.cursor in the current directory)
  -h, --help   Show this help

Examples:
  ./cursor_setup.sh                  # tid-aidlc -> ./.cursor
  ./cursor_setup.sh -g               # tid-aidlc -> ~/.cursor
  ./cursor_setup.sh --aws-aidlc      # AWS AI-DLC -> ./.cursor
  ./cursor_setup.sh --aws-aidlc -g   # AWS AI-DLC -> ~/.cursor
EOF
}

install_aws_aidlc=false
global_install=false

for arg in "$@"; do
  case "$arg" in
    --aws-aidlc)
      install_aws_aidlc=true
      ;;
    -g)
      global_install=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "$global_install" == true ]]; then
  cursor_dir="${HOME}/.cursor"
else
  cursor_dir="$(pwd)/.cursor"
fi

ensure_cursor_dir() {
  if [[ ! -d "$cursor_dir" ]]; then
    mkdir -p "$cursor_dir"
    echo "Created $cursor_dir"
  fi
}

install_tid_aidlc() {
  local source_dir="${SCRIPT_DIR}/tid-aidlc"

  if [[ ! -d "$source_dir" ]]; then
    echo "Error: tid-aidlc directory not found at $source_dir" >&2
    exit 1
  fi

  ensure_cursor_dir
  cp -R "${source_dir}/." "$cursor_dir/"
  echo "tid-aidlc contents copied to $cursor_dir"
}

install_aws_aidlc_rules() {
  local rules_src="${SCRIPT_DIR}/aidlc-rules/aws-aidlc-rules/core-workflow.md"
  local details_src="${SCRIPT_DIR}/aidlc-rules/aws-aidlc-rule-details"

  if [[ ! -f "$rules_src" ]]; then
    echo "Error: AWS AI-DLC core workflow not found at $rules_src" >&2
    exit 1
  fi

  if [[ ! -d "$details_src" ]]; then
    echo "Error: AWS AI-DLC rule details not found at $details_src" >&2
    exit 1
  fi

  ensure_cursor_dir
  mkdir -p "${cursor_dir}/rules"
  cat "$rules_src" >> "${cursor_dir}/rules/ai-dlc-workflow.mdc"

  mkdir -p "${cursor_dir}/.aidlc-rule-details"
  cp -R "${details_src}/." "${cursor_dir}/.aidlc-rule-details/"

  echo "AWS AI-DLC rules installed to $cursor_dir"
}

if [[ "$install_aws_aidlc" == true ]]; then
  install_aws_aidlc_rules
else
  install_tid_aidlc
fi
