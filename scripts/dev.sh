#! /usr/bin/env sh

# Exit in case of error
set -e

# Copy schemas from back
cp backend/app/app/schemas/scheme_game_current_api.py frontend/app/app/schemas/
cp backend/app/app/schemas/scheme_game_static.py frontend/app/app/schemas/
cp backend/app/app/constructs.py frontend/app/app/

docker compose \
-f docker-compose.yml \
config > docker-stack.yml

docker compose -f docker-stack.yml build
docker compose -f docker-stack.yml down --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker compose -f docker-stack.yml up -d
