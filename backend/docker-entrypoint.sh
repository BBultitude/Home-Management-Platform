#!/bin/sh
set -e

# Docker secrets bind-mount as 0400 root:root. Copying to /tmp/secrets/
# (rather than chmod) is reliable even on VFS read-only mounts.
if [ -d /run/secrets ]; then
    mkdir -p /tmp/secrets
    for f in /run/secrets/*; do
        [ -f "$f" ] || continue
        cp "$f" "/tmp/secrets/$(basename "$f")"
        chown appuser:appgroup "/tmp/secrets/$(basename "$f")"
        chmod 400 "/tmp/secrets/$(basename "$f")"
    done
fi

exec gosu appuser "$@"
