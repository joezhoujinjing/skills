#!/bin/bash
# NotebookLM Direct API - Bash wrapper functions
# Source this file to use: source tools/notebooklm.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" && pwd)"

# Use system Python3 (scripts handle vendor path internally)
NB_PYTHON="python3"

# List all notebooks
nb_list() {
    $NB_PYTHON "$SCRIPT_DIR/list_notebooks.py" "$@"
}

# Create a notebook
nb_create() {
    if [ -z "$1" ]; then
        echo "Usage: nb_create <title>" >&2
        return 1
    fi
    $NB_PYTHON "$SCRIPT_DIR/create_notebook.py" --title "$1" "${@:2}"
}

# Add a URL source
nb_add_url() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: nb_add_url <notebook_id> <url> [--wait]" >&2
        return 1
    fi
    $NB_PYTHON "$SCRIPT_DIR/add_source.py" "$1" --url "$2" "${@:3}"
}

# Add a text source
nb_add_text() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: nb_add_text <notebook_id> <text> [--title <title>] [--wait]" >&2
        return 1
    fi
    $NB_PYTHON "$SCRIPT_DIR/add_source.py" "$1" --text "$2" "${@:3}"
}

# Add a file source
nb_add_file() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: nb_add_file <notebook_id> <file_path> [--wait]" >&2
        return 1
    fi
    $NB_PYTHON "$SCRIPT_DIR/add_source.py" "$1" --file "$2" "${@:3}"
}

# List sources in a notebook
nb_list_sources() {
    if [ -z "$1" ]; then
        echo "Usage: nb_list_sources <notebook_id>" >&2
        return 1
    fi
    $NB_PYTHON "$SCRIPT_DIR/list_sources.py" "$1" "${@:2}"
}

# Query a notebook
nb_query() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: nb_query <notebook_id> <question>" >&2
        return 1
    fi
    $NB_PYTHON "$SCRIPT_DIR/query.py" "$1" --question "$2" "${@:3}"
}

# Export functions
export -f nb_list
export -f nb_create
export -f nb_add_url
export -f nb_add_text
export -f nb_add_file
export -f nb_list_sources
export -f nb_query

# Print available functions
nb_help() {
    cat <<'EOF'
NotebookLM Direct API - Bash Functions

Available functions:
  nb_list                          - List all notebooks
  nb_create <title>                - Create a new notebook
  nb_add_url <id> <url>            - Add URL source to notebook
  nb_add_text <id> <text>          - Add text source to notebook
  nb_add_file <id> <file>          - Add file source to notebook
  nb_list_sources <id>             - List sources in notebook
  nb_query <id> <question>         - Query notebook

Options:
  --json                           - Output as JSON
  --wait                           - Wait for source processing (add_source)

Examples:
  nb_list
  nb_create "My Research"
  nb_add_url abc123 "https://example.com" --wait
  nb_query abc123 "What are the main points?"

EOF
}
