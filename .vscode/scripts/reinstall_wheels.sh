#!/bin/bash
#
# Search dist folder recursively and installs containing *.whl files, if found
#

DEPTH="$(pwd | tr -c -d / | wc -c)"
MOD=.

while [[ $DEPTH -gt 0 ]]; do
    if [[ -d $MOD/dist ]]; then
        for file in $MOD/dist/*.whl; do
            if [[ -f $file ]]; then
                echo "Installing $file"
                pip3 install "$file" --force-reinstall --no-deps --break-system-packages
            fi
        done
        exit 0
    fi
    MOD=$MOD/..
    (( DEPTH-- )) || true
done

echo "No wheels found." >&2
exit 1
