#!/bin/sh
set -e
cd "$(dirname "$0")/.."
trap 'docker compose -p grades-tests -f compose.test.yml down' EXIT
# Образ создаётся обычной командой docker compose build web.
docker compose -p grades-tests -f compose.test.yml run --rm tests
