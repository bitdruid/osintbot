FROM python:3.12
WORKDIR /app
COPY osintbot/* /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install whois
ENV BOT_TOKEN=
ENV BOT_ADMIN_ID=
ENV BOT_ALLOWED_USERS=
CMD ["python3", "osintbot.py"]