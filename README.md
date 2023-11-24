![Version](https://img.shields.io/badge/Version-0.1.0-blue.svg)
![Release](https://img.shields.io/badge/Release-Alpha-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

# osintbot
Playing around with possibilities of an osint-bot for telegram.

## Installation

### Docker

```
docker build -t osintbot .
docker run -d --name osintbot osintbot -e BOT_TOKEN=<token of your bot> -e BOT_ADMIN_ID=<telegram id of the bot admin>
```

### Environmental Variables

| env               | description                                          | default       |
|-------------------|------------------------------------------------------|---------------|
| BOT_TOKEN         | API-token of your telegram-bot                       | must be given |
| BOT_ADMIN         | telegram-ID of the admin-user                        | must be given |
| BOT_ALLOWED_USERS | comma-seperated list of users with access to the bot | None          |

## next steps

- [ ] admin can manage allowed users via bot chat
- [ ] more osint-modules (e.g. geoip)
- [ ] command-menu

## Dev & Test

create a virtualenv and install the requirements

```
bash dev/build_venv.sh
```

create file with environment variables in project root

```
touch .venv.env
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
