![Version](https://img.shields.io/badge/Version-0.1.5-blue.svg)
![Release](https://img.shields.io/badge/Release-Alpha-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Docker Pulls](https://img.shields.io/docker/pulls/bitdruid/osintbot.svg)](https://hub.docker.com/r/bitdruid/osintbot/)

# osintbot
Playing around with possibilities of an osint-bot for discord (telegram tested in other branch).

## Installation

### Docker

Populate .env with the table below or just pull the image from dockerhub (click on the badge above)

```
docker build -t osintbot .
docker run -d --name osintbot osintbot --env-file .env
```
or docker-compose
```
docker-compose up -d
```


### Environmental Variables

| env               | description                                          | default       |
|-------------------|------------------------------------------------------|---------------|
| BOT_TOKEN         | API-token of the bot                                 | must be given |
| BOT_NAME          | name of the bot                                      | osintbot      |
| BOT_CHANNEL       | channel the bot will create and post to              | osint         |

## used

### api

- [ipinfo.io](https://ipinfo.io/)
- [iplocation.net](https://iplocation.net/)
- [ipapi.com](https://ip-api.com/)
- [ipapi.co](https://ipapi.co/)
- [freegeoip.live](https://freegeoip.live/)

### repositories

- [whois](https://github.com/rfc1036/whois)

## Dev & Test

create a virtualenv and install the requirements

```
bash dev/venv_create.sh
```

create file with environment variables in project root

```
touch .env
```

add envs like

```
BOT_TOKEN=<token of your bot>
...
```

build and run docker with

```
bash dev/build_docker.sh
```
