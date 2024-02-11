import os
import sys
import threading
import dotenv
import osintbot.mail_bot as mail_bot
import osintbot.discord_bot as discord_bot
import osintbot.db as db

if __name__ == "__main__":

    class Environment:

        DISCORD_BOT = False
        MAIL_BOT = False

        def __init__(self):
            if os.path.isfile('.env'):
                dotenv.load_dotenv(dotenv_path='.env')
            self.discord_bot()
            self.mail_bot()

        def discord_bot(self):
            try:
                self.bot_token = os.getenv('BOT_TOKEN') if os.getenv('BOT_TOKEN') else ValueError('No bot token provided')
                self.bot_name = os.getenv('BOT_NAME') if os.getenv('BOT_NAME') else "osintbot"
                self.bot_channel = os.getenv('BOT_CHANNEL') if os.getenv('BOT_CHANNEL') else "osint"
                self.DISCORD_BOT = True
            except ValueError as e:
                print(e)
            
        def mail_bot(self):
            try:
                self.mail_user = os.getenv('MAIL_USER') if os.getenv('MAIL_USER') else ValueError('No email provided')
                self.mail_password = os.getenv('MAIL_PASS') if os.getenv('MAIL_PASS') else ValueError('No password provided')
                self.smtp_server = os.getenv('MAIL_SMTP_SERVER') if os.getenv('MAIL_SMTP_SERVER') else ValueError('No SMTP server provided')
                self.smtp_port = os.getenv('MAIL_SMTP_PORT') if os.getenv('MAIL_SMTP_PORT') else ValueError('No SMTP port provided')
                self.imap_server = os.getenv('MAIL_IMAP_SERVER') if os.getenv('MAIL_IMAP_SERVER') else ValueError('No IMAP server provided')
                self.imap_port = os.getenv('MAIL_IMAP_PORT') if os.getenv('MAIL_IMAP_PORT') else ValueError('No IMAP port provided')
                self.MAIL_BOT = True
                return True
            except ValueError as e:
                print(e)

    env_instance = Environment()
    db_instance = db.Database()

    # start mail_bot
    if env_instance.MAIL_BOT:
        mailbot_instance = mail_bot.Mailbot(env_instance, db_instance)
        mail_thread = threading.Thread(target=mailbot_instance.mail_run)
        mail_thread.start()

    # start discord_bot
    if env_instance.DISCORD_BOT:
        discord_instance = discord_bot.main(env_instance, db_instance)
        discord_thread = threading.Thread(target=discord_instance.discord_run)
        discord_thread.start()