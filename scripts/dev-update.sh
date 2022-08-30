#! /usr/bin/env sh

# Exit in case of error
set -e

sh ./scripts/dev.sh
docker-compose -f docker-stack.yml exec backend poetry lock --no-update
