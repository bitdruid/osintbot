#!/bin/bash

# for dev: create .venv.env and add the envs for your bot to test it
token=$(grep BOT_TOKEN .venv.env | cut -d '=' -f2)
admin_id=$(grep BOT_ADMIN_ID .venv.env | cut -d '=' -f2)

docker build -t osintbot .
docker run -p 5050:5000 --hostname osintbot -e BOT_TOKEN=$token -e BOT_ADMIN_ID=$admin_id --rm osintbot
