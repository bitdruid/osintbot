FROM python:3.12 AS whois
RUN apt-get update && apt-get install whois

FROM python:3.12 AS requirements
WORKDIR /app
COPY osintbot/requirements.txt /app
RUN pip3 install -r requirements.txt

FROM python:3.12
WORKDIR /app
COPY --from=whois /usr/bin/whois /usr/bin/whois
COPY --from=requirements /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY osintbot/* /app/
ENV BOT_TOKEN=
ENV BOT_ADMIN_ID=
ENV BOT_ALLOWED_USERS=
CMD ["python3", "osintbot.py"]