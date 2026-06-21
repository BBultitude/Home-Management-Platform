#!/bin/sh
set -e

# Docker secrets mount as 0400 root:root, unreadable by non-root appuser.
# Widen to o+r here (as root) before dropping privileges.
if [ -d /run/secrets ]; then
    chmod o+r /run/secrets/* 2>/dev/null || true
fi

exec gosu appuser "$@"
