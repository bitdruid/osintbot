FROM python:3.12-alpine AS whois
RUN apk update && apk add whois

FROM python:3.12-alpine AS requirements
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt

FROM python:3.12-alpine
WORKDIR /app
COPY --from=whois /usr/bin/whois /usr/bin/whois
COPY --from=requirements /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY osintbot/* /app/
ENV BOT_TOKEN=
ENV BOT_ADMIN_ID=
ENV BOT_ALLOWED_USERS=
CMD ["python3", "osintbot.py"]