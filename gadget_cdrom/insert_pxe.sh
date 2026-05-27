#!/bin/bash -eu

IDIR="${BASH_SOURCE%/*}"
if [[ ! -d "$IDIR" ]]; then IDIR="$PWD"; fi

profile="$1"
MODE=${2:-pxe}

if [ "$MODE" != "pxe" ] ; then
    exit 1
fi

if ! realpath "$profile" | egrep "^/pxe/"; then
    exit 1
fi

exec "$IDIR/pxe.sh" start "$profile"