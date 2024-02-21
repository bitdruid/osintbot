import os
import sys
from dotenv import load_dotenv
import time
import smtplib
import imaplib

import osintbot.datarequest as datarequest
import osintbot.mail as mail

import osintkit.helper as kit_helper

class Mailbot:

    IMAP = None
    SMTP = None

    FUNCTION = None
    INPUT = None

    def __init__(self, env_instance, db_instance):
        self.mail_expire = 360
        self.connection_expire = 3600
        self.env_instance = env_instance
        self.db_instance = db_instance





    def mail_run(self):
        """
        Continuously loops and checks for new emails using IMAP protocol.
        If a new email is found, it parses the subject, sends a response email, and deletes the original email.
        The connection to the IMAP server is re-established after a certain period of time.
        """
        current_time = time.time()
        self.imap_connect()
        while True:
            mail_list = self.fetch_email()
            if mail_list:
                self.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Emails found: {len(mail_list)}") if mail_list else None
                expired_mails = self.filter_expired_email(mail_list)
                mail_list = self.mail_filter(mail_list, expired_mails)
                rejected_mails = self.filter_rejected_email(mail_list)
                mail_list = self.mail_filter(mail_list, rejected_mails)
                delete_mails = list(set(expired_mails + rejected_mails))
                if mail_list:
                    for mail in mail_list:
                        self.log(f"Processing email: {mail.MAIL_ID} - time: {mail.MAIL_TIME}, from: {mail.MAIL_FROM}, subject: {mail.MAIL_SUBJECT}")
                        time.sleep(1)
                        if not self.parse_subject(mail):
                            delete_mails.append(mail.MAIL_ID)
                            continue
                        self.send_email(mail.MAIL_FROM, 'osintbot response to: "' + self.FUNCTION + ' ' + self.INPUT + '"', self.run_function())
                        delete_mails.append(mail.MAIL_ID)
                self.delete_email(delete_mails)

            if time.time() - current_time > self.connection_expire:
                self.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Connection expired. Reconnecting to IMAP server {self.env_instance.imap_server}.")
                self.imap_disconnect()
                current_time = time.time()
                self.imap_connect()
            time.sleep(30)

    def mail_filter(self, mail_list, filter_list):
        try:
            filtered_mail_list = []
            for mail in mail_list:
                if mail.MAIL_ID not in filter_list:
                    filtered_mail_list.append(mail)
            return filtered_mail_list
        except Exception as e:
            self.log('!-- Could not filter emails')
            self.exception(e)





    def imap_connect(self):
        try:
            self.IMAP = imaplib.IMAP4_SSL(self.env_instance.imap_server)
            self.IMAP.login(self.env_instance.mail_user, self.env_instance.mail_password)
        except Exception as e:
            self.log('!-- IMAP connection failed')
            self.exception(e)

    def imap_disconnect(self):
        self.IMAP.close()

    def smtp_connect(self):
        try:
            self.SMTP = smtplib.SMTP(self.env_instance.smtp_server, self.env_instance.smtp_port)
            self.SMTP.starttls()
            self.SMTP.login(self.env_instance.mail_user, self.env_instance.mail_password)
        except Exception as e:
            self.log('!-- SMTP connection failed')
            self.exception(e)

    def smtp_disconnect(self):
        self.SMTP.quit()





    def delete_email(self, mail: list or bytes) -> None:
        try:
            if type(mail) == list:
                for mail_id in mail:
                    self.IMAP.store(mail_id, '+FLAGS', '\\Deleted')
                self.IMAP.expunge()
                self.log(f"--> Emails deleted successfully: {len(mail)}")
            else:
                mail_id = mail
                self.IMAP.store(mail_id, '+FLAGS', '\\Deleted')
                self.IMAP.expunge()
                self.log('--> Email deleted successfully')
        except Exception as e:
            self.log('!-- Email failed to delete')
            self.exception(e)
        
    def filter_expired_email(self, mail_list: list) -> None:
        try:
            expired_emails = []
            for mail in mail_list:
                if time.time() - time.mktime(time.strptime(mail.MAIL_TIME, '%d-%b-%Y %H:%M:%S')) > self.mail_expire:
                    self.log(f"--> Expired email {mail.MAIL_ID}. From: {mail.MAIL_FROM}, Subject: {mail.MAIL_SUBJECT}, Time: {mail.MAIL_TIME}")
                    expired_emails.append(mail)
                self.db_instance.mail_insert(True, mail.MAIL_FROM, mail.MAIL_SUBJECT)
            self.log(f"--> Expired emails overall: {len(expired_emails)}") if expired_emails else None
            return expired_emails
        except Exception as e:
            self.log('!-- Could not sort expired emails')
            self.exception(e)
    def filter_rejected_email(self, mail_list: list) -> None:
        try:
            rejected_sender = []
            rejected_mails = []
            oldest_mail_by_sender = {}
            # get the oldest mail by each sender
            for mail in mail_list:
                if mail.MAIL_FROM in oldest_mail_by_sender:
                    if mail.MAIL_TIME < oldest_mail_by_sender[mail.MAIL_FROM].MAIL_TIME:
                        oldest_mail_by_sender[mail.MAIL_FROM] = mail
                else:
                    oldest_mail_by_sender[mail.MAIL_FROM] = mail
            # add all remaining mails of the sender to the rejected_mails list
            for mail in mail_list:
                if mail.MAIL_FROM in oldest_mail_by_sender:
                    if mail.MAIL_ID != oldest_mail_by_sender[mail.MAIL_FROM].MAIL_ID:
                        self.log(f"--> Rejected email. From: {mail.MAIL_FROM}, Subject: {mail.MAIL_SUBJECT}, Time: {mail.MAIL_TIME}")
                        rejected_mails.append(mail)
                        if mail.MAIL_FROM not in rejected_sender:
                            rejected_sender.append(mail.MAIL_FROM)
            # inform the sender about the rejected emails
            for sender in rejected_sender:
                message = f"Some of your emails have been rejected due to multiple submissions. Wait until your previous request has been processed before submitting a new one."
                deleted_mails = []
                for mail in rejected_mails:
                    deleted_mails.append(f"{mail.MAIL_TIME} --> {mail.MAIL_SUBJECT}")
                message += f"\n\nThe following emails were deleted:\n{chr(10).join(deleted_mails)}"
                self.send_email(sender, 'osintbot rejected emails', message)
            # remove all remaining mails of the sender
            self.log(f"--> Rejected emails overall: {len(rejected_mails)}") if rejected_mails else None
            return rejected_mails
        except Exception as e:
            self.log('!-- Could not sort rejected emails')
            self.exception(e)





    def send_email(self, to: str, subject: str, message: str) -> None:
        try:
            self.smtp_connect()
            message = f'Subject: {subject}\n\n{message}'
            self.SMTP.sendmail(self.env_instance.mail_user, to, message.encode('utf-8'))
            self.SMTP.quit()
            self.log(f"--> Response sent successfully. To: {to}, Subject: {subject}")
        except Exception as e:
            self.log(f"!-- Email failed to send. To: {to}, Subject: {subject}")
            self.exception(e)

    def fetch_email(self):
        try:
            self.IMAP.select('inbox')
            status, messages = self.IMAP.search(None, '(TO ' + self.env_instance.mail_user + ')')
            messages = messages[0].split()
            mail_list = []
            for mail_id in messages:
                mail_time = self.IMAP.fetch(mail_id, '(INTERNALDATE)')[1][0].decode().split('INTERNALDATE ')[1].split('"')[1].split(' +')[0].strip()
                mail_from = self.IMAP.fetch(mail_id, '(BODY[HEADER.FIELDS (FROM)])')[1][0][1].decode().split('<')[1].split('>')[0].strip()
                mail_subject = self.IMAP.fetch(mail_id, '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1].decode().split('Subject: ')[1].removesuffix('\r\n\r\n').strip()
                mail_body = self.IMAP.fetch(mail_id, '(BODY[TEXT])')[1][0][1].decode().removesuffix('\r\n').strip()
                mail_list.append(mail(mail_id, mail_time, mail_from, mail_subject, mail_body))
            return mail_list
        except Exception as e:
            self.log('!-- Email failed to fetch')
            self.exception(e)





    def parse_subject(self, mail):
        import shlex
        try:
            subject = mail.MAIL_SUBJECT
            arguments = subject.split(' ')
            if len(arguments) != 2:
                raise ValueError('Invalid subject')
            # only allow alphanumeric characters, hyphen, and period
            allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789.-'
            if not all(char in allowed_chars for char in arguments[0].lower()) or not all(char in allowed_chars for char in arguments[1].lower()):
                raise ValueError('Invalid subject')
            # filter anyway to prevent injection
            self.FUNCTION = shlex.quote(''.join(filter(lambda char: char in allowed_chars, arguments[0].lower())))
            self.INPUT = shlex.quote(''.join(filter(lambda char: char in allowed_chars, arguments[1].lower())))
            return True
        except ValueError:
            message = 'Invalid subject. Please use the following format: <function> <input>. Example: "whois example.com"'
            commands = "Available commands:\n" \
            " whois <domain/ip> - Retrieve whois data for a domain or IP address\n" \
            " iplookup <domain/ip> - Retrieve IP lookup data for a domain or IP address\n" \
            " geoip <domain/ip> - Retrieve GeoIP data for a domain or IP address\n" \
            " arecord <domain> - Retrieve A record data for a domain\n" \
            " report <domain/ip> - Retrieve all available data for a domain or IP address"
            self.send_email(mail.MAIL_FROM, 'osintbot invalid subject: "' + mail.MAIL_SUBJECT + '"', message + '\n\n' + commands)
            return False

            


    

    def run_function(self):
        if self.FUNCTION and self.INPUT:
            if self.FUNCTION == 'whois':
                import osintkit.whois as whois
                response = whois.request(self.INPUT)
            elif self.FUNCTION == 'geoip':
                import osintkit.geoip as geoip
                response = geoip.request(self.INPUT)
            elif self.FUNCTION == 'iplookup':
                import osintkit.iplookup as iplookup
                response = iplookup.request(self.INPUT)
            elif self.FUNCTION == 'arecord':
                import osintkit.arecord as arecord
                response = arecord.request(self.INPUT)
            elif self.FUNCTION == 'report':
                response = datarequest.full_report(self.INPUT)
            else:
                response = "Invalid function"
            self.log(f"--> Running function: '{self.FUNCTION}' with input: '{self.INPUT}'")
            return kit_helper.json_to_string(response)
        
    def exception(self, e):
        self.log(f"!-- Error function: {sys.exc_info()[-1].tb_frame.f_code.co_name}")
        self.log(f"!-- Error line: {sys.exc_info()[-1].tb_lineno}")
        self.log(f"!-- Error stacktrace: {e}")

    def log(self, message):
        print(message)
        os.makedirs('log', exist_ok=True)
        with open('log/mail.log', 'a') as log:
            log.write(message + '\n')

def main():
    if os.path.isfile('.env'):
        load_dotenv(dotenv_path='.env')
    Mailbot()

if __name__ == '__main__':
    main()