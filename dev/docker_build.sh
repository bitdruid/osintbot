#!/bin/bash

if [ ! -f .env ]; then
    touch .env

docker build -t osintbot .
docker run -p 5050:5000 --hostname osintbot --env-file .env -rm osintbot
