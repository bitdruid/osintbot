import os
from dotenv import load_dotenv
import time
import smtplib
import imaplib

import osintbot.datarequest as datarequest
import osintbot.mail as m
import osintbot.log as log

import osintkit.helper as kit_helper

class Mailbot:

    IMAP = None
    SMTP = None

    HELP = "Available commands:\n" \
    " whois <domain/ip> - Retrieve whois data for a domain or IP address\n" \
    " iplookup <domain/ip> - Retrieve IP lookup data for a domain or IP address\n" \
    " geoip <domain/ip> - Retrieve GeoIP data for a domain or IP address\n" \
    " arecord <domain> - Retrieve A record data for a domain\n" \
    " report <domain/ip> - Retrieve all available data for a domain or IP address\n"

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
                log.log("mail", f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Emails found: {len(mail_list)}")
                expired_mails = self.filter_expired_email(mail_list)
                mail_list = [mail for mail in mail_list if mail not in expired_mails]
                rejected_mails = self.filter_rejected_email(mail_list)
                mail_list = [mail for mail in mail_list if mail not in rejected_mails]
                delete_mails = list(set(expired_mails + rejected_mails))
                for mail in mail_list:
                    log.log("mail", f"Processing email: {mail.MAIL_ID} - time: {mail.MAIL_TIME}, from: {mail.MAIL_FROM}, subject: {mail.MAIL_SUBJECT}")
                    time.sleep(1)
                    if not mail.REQUEST_STATUS:
                        log.log("mail", f"--> Invalid request: {mail.MAIL_SUBJECT}")
                        self.send_email(mail.MAIL_FROM, 'osintbot invalid request: "' + mail.MAIL_SUBJECT + '"', self.HELP)
                    else:
                        self.send_email(mail.MAIL_FROM, 'osintbot response to: "' + mail.REQUEST_FUNCTION + ' ' + mail.REQUEST_TARGET + '"', self.run_function(mail))
                    delete_mails.append(mail)
                self.delete_email(delete_mails)

            if time.time() - current_time > self.connection_expire:
                log.log("mail", f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Connection expired. Reconnecting to IMAP server {self.env_instance.imap_server}.")
                self.imap_disconnect()
                current_time = time.time()
                self.imap_connect()
            time.sleep(30)





    def imap_connect(self):
        while Exception:
            try:
                self.IMAP = imaplib.IMAP4_SSL(self.env_instance.imap_server)
                self.IMAP.login(self.env_instance.mail_user, self.env_instance.mail_password)
                break
            except Exception as e:
                log.log("mail", '!-- IMAP connection failed')
                log.exception("mail", e)
                time.sleep(60)
    def imap_disconnect(self):
        self.IMAP.close()

    def smtp_connect(self):
        while Exception:
            try:
                self.SMTP = smtplib.SMTP(self.env_instance.smtp_server, self.env_instance.smtp_port)
                self.SMTP.starttls()
                self.SMTP.login(self.env_instance.mail_user, self.env_instance.mail_password)
                break
            except Exception as e:
                log.log("mail", '!-- SMTP connection failed')
                log.exception("mail", e)
                time.sleep(60)
    def smtp_disconnect(self):
        self.SMTP.quit()





    def delete_email(self, mail_list: list) -> None:
        try:
            for mail in mail_list:
                self.IMAP.store(mail.MAIL_ID, '+FLAGS', '\\Deleted')
            self.IMAP.expunge()
            log.log("mail", f"--> Emails deleted successfully: {len(mail_list)}") if mail_list else None
        except Exception as e:
            log.log("mail", '!-- Email failed to delete')
            log.exception("mail", e)
        
    def filter_expired_email(self, mail_list: list) -> None:
        try:
            expired_emails = []
            for mail in mail_list:
                if time.time() - time.mktime(time.strptime(mail.MAIL_TIME, '%d-%b-%Y %H:%M:%S')) > self.mail_expire:
                    log.log("mail", f"--> Expired email {mail.MAIL_ID}. From: {mail.MAIL_FROM}, Subject: {mail.MAIL_SUBJECT}, Time: {mail.MAIL_TIME}")
                    expired_emails.append(mail)
                self.db_instance.mail_insert(True, mail.MAIL_FROM, mail.MAIL_SUBJECT)
            log.log("mail", f"--> Expired emails overall: {len(expired_emails)}") if expired_emails else None
            return expired_emails
        except Exception as e:
            log.log("mail", '!-- Could not sort expired emails')
            log.exception("mail", e)
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
                        log.log("mail", f"--> Rejected email. From: {mail.MAIL_FROM}, Subject: {mail.MAIL_SUBJECT}, Time: {mail.MAIL_TIME}")
                        rejected_mails.append(mail)
                        if mail.MAIL_FROM not in rejected_sender:
                            rejected_sender.append(mail.MAIL_FROM)
            # inform the sender about the rejected emails
            for sender in rejected_sender:
                message = "Some of your emails have been rejected due to multiple submissions. Wait until your previous request has been processed before submitting a new one."
                deleted_mails = []
                for mail in rejected_mails:
                    deleted_mails.append(f"{mail.MAIL_TIME} --> {mail.MAIL_SUBJECT}")
                message += f"\n\nThe following emails were deleted:\n{chr(10).join(deleted_mails)}"
                self.send_email(sender, 'osintbot rejected emails', message)
            # remove all remaining mails of the sender
            log.log("mail", f"--> Rejected emails overall: {len(rejected_mails)}") if rejected_mails else None
            return rejected_mails
        except Exception as e:
            log.log("mail", '!-- Could not sort rejected emails')
            log.exception("mail", e)





    def send_email(self, to: str, subject: str, message: str) -> None:
        try:
            self.smtp_connect()
            message = f'Subject: {subject}\r\n\r\n{message}\r\n'
            self.SMTP.sendmail(self.env_instance.mail_user, to, message.encode('utf-8'))
            self.SMTP.quit()
            log.log("mail", f"--> Response sent successfully. To: {to}, Subject: {subject}")
        except Exception as e:
            log.log("mail", f"!-- Email failed to send. To: {to}, Subject: {subject}")
            log.exception("mail", e)

    def fetch_email(self):
        try:
            self.IMAP.select('inbox')
            status, messages = self.IMAP.search(None, '(TO ' + self.env_instance.mail_user + ')')
            messages = messages[0].split()
            mail_list = []
            for mail_id in messages:
                mail_list.append(m.Mail(mail_id, self.IMAP.fetch(mail_id, '(RFC822)')[1][0][1].decode('utf-8')))
            return mail_list
        except Exception as e:
            log.log("mail", '!-- Email failed to fetch')
            log.exception("mail", e)





    def run_function(self, mail: m.Mail):
        if mail.REQUEST_FUNCTION and mail.REQUEST_TARGET:
            if mail.REQUEST_FUNCTION == 'whois':
                import osintkit.whois as whois
                response = whois.request(mail.REQUEST_TARGET)
            elif mail.REQUEST_FUNCTION == 'geoip':
                import osintkit.geoip as geoip
                response = geoip.request(mail.REQUEST_TARGET)
            elif mail.REQUEST_FUNCTION == 'iplookup':
                import osintkit.iplookup as iplookup
                response = iplookup.request(mail.REQUEST_TARGET)
            elif mail.REQUEST_FUNCTION == 'arecord':
                import osintkit.arecord as arecord
                response = arecord.request(mail.REQUEST_TARGET)
            elif mail.REQUEST_FUNCTION == 'report':
                response = datarequest.full_report(mail.REQUEST_TARGET)
            else:
                response = "Invalid function"
            log.log("mail", f"--> Running function: '{mail.REQUEST_FUNCTION}' with input: '{mail.REQUEST_TARGET}'")
            return kit_helper.json_to_string(response)

def main():
    if os.path.isfile('.env'):
        load_dotenv(dotenv_path='.env')
    Mailbot()

if __name__ == '__main__':
    main()