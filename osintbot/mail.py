import os
import sys
import threading
from dotenv import load_dotenv
import time
import smtplib
import imaplib

import db
import datarequest

import osintkit.helper as kit_helper

class Mail:
    """
    Class representing an email client.

    Attributes:
        IMAP (None): IMAP connection object.
        SMTP (None): SMTP connection object.
        FUNCTION (None): The function specified in the email subject.
        INPUT (None): The input specified in the email subject.

    Methods:
        __init__(): Initializes the Mail object and establishes connections to the email servers.
        imap_loop(): Continuously checks for new emails and performs actions based on the email content.
        imap_connect(): Connects to the IMAP server.
        imap_disconnect(): Disconnects from the IMAP server.
        smtp_connect(): Connects to the SMTP server.
        smtp_disconnect(): Disconnects from the SMTP server.
        fetch_email(): Fetches the list of emails from the inbox.
        delete_email(mail: list or bytes): Deletes the specified email(s) from the inbox.
        delete_expired_email(messages: list): Deletes expired emails from the inbox.
        send_email(to: str, subject: str, message: str): Sends an email to the specified recipient.
        read_email(): Reads the content of the emails in the inbox.
        parse_subject(mail): Parses the subject of the email to extract the function and input.
        run_function(): Executes the specified function with the given input.
        exception(e): Handles exceptions and prints error details.

    Note:
        This class requires the following environment variables to be set:
        - MAIL_USER: Email address of the user.
        - MAIL_PASS: Password for the email account.
        - MAIL_SMTP_SERVER: SMTP server address.
        - MAIL_SMTP_PORT: SMTP server port.
        - MAIL_IMAP_SERVER: IMAP server address.
        - MAIL_IMAP_PORT: IMAP server port.
    """

    IMAP = None
    SMTP = None

    FUNCTION = None
    INPUT = None

    def __init__(self):
        self.mail_expire = 360
        self.connection_expire = 3600
        self.mail_user = os.getenv('MAIL_USER') if os.getenv('MAIL_USER') else sys.exit('No email provided')
        self.mail_password = os.getenv('MAIL_PASS') if os.getenv('MAIL_PASS') else sys.exit('No password provided')
        self.smtp_server = os.getenv('MAIL_SMTP_SERVER') if os.getenv('MAIL_SMTP_SERVER') else sys.exit('No SMTP server provided')
        self.smtp_port = os.getenv('MAIL_SMTP_PORT') if os.getenv('MAIL_SMTP_PORT') else sys.exit('No SMTP port provided')
        self.imap_server = os.getenv('MAIL_IMAP_SERVER') if os.getenv('MAIL_IMAP_SERVER') else sys.exit('No IMAP server provided')
        self.imap_port = os.getenv('MAIL_IMAP_PORT') if os.getenv('MAIL_IMAP_PORT') else sys.exit('No IMAP port provided')
        self.db = db.Database()
        mail_thread = threading.Thread(target=self.imap_loop)
        mail_thread.start()





    def imap_loop(self):
        """
        Continuously loops and checks for new emails using IMAP protocol.
        If a new email is found, it parses the subject, sends a response email, and deletes the original email.
        The connection to the IMAP server is re-established after a certain period of time.
        """
        current_time = time.time()
        self.imap_connect()
        while True:
            emails = self.fetch_email()
            if emails:
                self.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Emails found: {len(emails)}")
            self.delete_expired_email(emails)
            emails = self.fetch_email()
            mail_dict = self.read_email(emails)
            if mail_dict:
                for mail_id in mail_dict:
                    mail_id = mail_dict[mail_id]['id']
                    mail_from = mail_dict[mail_id]['from']
                    mail_subject = mail_dict[mail_id]['subject']
                    mail_time = mail_dict[mail_id]['time']
                    self.log(f"Processing email: {mail_id} - time: {mail_time}, from: {mail_from}, subject: {mail_subject}")
                    time.sleep(1)
                    if not self.parse_subject(mail_dict[mail_id]):
                        continue
                    self.send_email(mail_dict[mail_id]['from'], 'osintbot response to: "' + self.FUNCTION + ' ' + self.INPUT + '"', self.run_function())
                    self.delete_email(mail_id)

            if time.time() - current_time > self.connection_expire:
                self.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Connection expired. Reconnecting to IMAP server {self.imap_server}.")
                self.imap_disconnect()
                current_time = time.time()
                self.imap_connect()
            time.sleep(10)





    def imap_connect(self):
        try:
            self.IMAP = imaplib.IMAP4_SSL(self.imap_server)
            self.IMAP.login(self.mail_user, self.mail_password)
        except Exception as e:
            self.log('!-- IMAP connection failed')
            self.exception(e)

    def imap_disconnect(self):
        self.IMAP.close()

    def smtp_connect(self):
        try:
            self.SMTP = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.SMTP.starttls()
            self.SMTP.login(self.mail_user, self.mail_password)
        except Exception as e:
            self.log('!-- SMTP connection failed')
            self.exception(e)

    def smtp_disconnect(self):
        self.SMTP.quit()




    def fetch_email(self):
        try:
            self.IMAP.select('inbox')
            status, messages = self.IMAP.search(None, '(TO ' + self.mail_user + ')')
            messages = messages[0].split()
            return messages
        except Exception as e:
            self.log('!-- Email failed to fetch')
            self.exception(e)

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
        
    def delete_expired_email(self, messages: list) -> None:
        expired = False
        expired_emails = []
        for mail_id in messages:
            mail_time = self.IMAP.fetch(mail_id, '(INTERNALDATE)')[1][0].decode().split('INTERNALDATE ')[1].split('"')[1].split(' +')[0].strip()
            mail_from = self.IMAP.fetch(mail_id, '(BODY[HEADER.FIELDS (FROM)])')[1][0][1].decode().split('<')[1].split('>')[0].strip()
            mail_subject = self.IMAP.fetch(mail_id, '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1].decode().split('Subject: ')[1].removesuffix('\r\n\r\n').strip()
            if time.time() - time.mktime(time.strptime(mail_time, '%d-%b-%Y %H:%M:%S')) > self.mail_expire:
                self.log(f"--> Email {mail_id} expired. From: {mail_from}, Subject: {mail_subject}, Time: {mail_time}")
                expired = True
                expired_emails.append(mail_id)
            self.db.mail_insert(expired, mail_from, mail_subject)
        if expired_emails:
            self.delete_email(expired_emails)





    def send_email(self, to: str, subject: str, message: str) -> None:
        try:
            self.smtp_connect()
            message = f'Subject: {subject}\n\n{message}'
            self.SMTP.sendmail(self.mail_user, to, message.encode('utf-8'))
            self.SMTP.quit()
            self.log(f"--> Response sent successfully. To: {to}, Subject: {subject}")
        except Exception as e:
            self.log(f"!-- Email failed to send. To: {to}, Subject: {subject}")
            self.exception(e)

    def read_email(self, messages: list) -> dict:
        try:
            mail_dict = {}
            for mail_id in messages:
                mail_id = mail_id.decode()
                mail_time = self.IMAP.fetch(mail_id, '(INTERNALDATE)')[1][0].decode().split('INTERNALDATE ')[1].split('"')[1].split(' +')[0].strip()
                mail_from = self.IMAP.fetch(mail_id, '(BODY[HEADER.FIELDS (FROM)])')[1][0][1].decode().split('<')[1].split('>')[0].strip()
                mail_subject = self.IMAP.fetch(mail_id, '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1].decode().split('Subject: ')[1].removesuffix('\r\n\r\n').strip()
                mail_dict[mail_id] = {'id': mail_id, 'from': mail_from, 'subject': mail_subject, 'time': mail_time}
            return mail_dict
        except Exception as e:
            self.log(f"!-- Email failed to read. Mail: {mail_id}")
            self.exception(e)





    def parse_subject(self, mail):
        import shlex
        try:
            subject = mail['subject']
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
            self.send_email(mail['from'], 'osintbot invalid subject: "' + mail['subject'] + '"', message + '\n\n' + commands)
            self.delete_email(mail['id'])
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
    Mail() 

if __name__ == '__main__':
    main()