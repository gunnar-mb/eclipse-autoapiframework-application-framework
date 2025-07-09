#!/bin/bash
#
# Search Makefiles recursively in a directory named VAF and run make(1) there, if one is found
#

DEPTH="$(pwd | tr -c -d / | wc -c)"
MOD=.
NPD="--no-print-directory"

if [[ "$*" == *"-w"* || "$*" == *"--print-directory"* ]]; then
    NPD=
fi

while [[ $DEPTH -gt 0 ]]; do
    if [[ -f $MOD/VAF/Makefile ]]; then
        if [[ $MOD == "." ]]; then
            make -C VAF "$@"
        else
            echo "make -C $MOD/VAF $*"
            make $NPD -C $MOD/VAF "$@"
        fi
        exit $?
    fi
    MOD=$MOD/..
    (( DEPTH-- )) || true
done

echo "No Makefile found in a directory named VAF." >&2
exit 1
