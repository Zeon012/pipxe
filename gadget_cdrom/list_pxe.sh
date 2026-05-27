#!/bin/bash -eu

if [ ! -d /pxe ]; then
    exit 1
fi

EXT=${1:-ipxe}

find /pxe -type f -iname "*.$EXT" -not -path '*/.*' -print0