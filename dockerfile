FROM python:3.11-slim AS whois
RUN apt -qq update && apt -qq install -y whois

FROM python:3.11-slim AS requirements
WORKDIR /app
COPY osintbot/requirements.txt /app
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=whois /usr/bin/whois /usr/bin/whois
COPY --from=requirements /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY osintbot/* /app/
ENV BOT_TOKEN=
ENV BOT_ADMIN_ID=
ENV BOT_ALLOWED_USERS=
ENV BOT_NAME=
ENV BOT_CHANNEL=
CMD ["python3", "osintbot.py"]