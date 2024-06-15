import os
import shlex
from dotenv import load_dotenv
import time
import smtplib
import imaplib

import osintbot.datarequest as datarequest
from osintbot.MailRequest import MailRequest
from osintbot.MailResponse import MailResponse
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
    " report <domain/ip> - Retrieve all available data for a domain or IP address\n" \
    " screenshot <url> - Take a full-page screenshot of a URL and receive the image + printable A4 PDF\n" \
    "\n" \
    "Write a single request in the subject line or the body and multiple requests in the body.\n" \
    "Example single subject request: 'subject = whois example.com'\n" \
    "Example single body request: 'subject = whois, body = example.com'\n" \
    "Example multiple body request: 'subject = whois, body = example.com <newline> example.net <newline> example.org'\n"

    FUNCTIONS = {
        'help' : None,
        'whois': datarequest.single_report,
        'geoip': datarequest.single_report,
        'iplookup': datarequest.single_report,
        'arecord': datarequest.single_report,
        'report': datarequest.full_report,
        'screenshot': datarequest.file_output_report
    }

    def __init__(self, env_instance, db_instance):
        self.mail_expire = 360
        self.connection_expire = 3600
        self.env_instance = env_instance
        self.db_instance = db_instance
        self.mail_run()





    def mail_run(self):
        """
        Continuously loops and checks for new emails using IMAP protocol.
        If a new email is found, it parses the subject, sends a response email, and deletes the original email.
        The connection to the IMAP server is re-established after a certain period of time.
        """
        current_time = time.time()
        self.imap_connect()
        while True:
            mail_request_list = self.fetch_email()
            if mail_request_list:
                log.log("mail", f"----- Emails found: {len(mail_request_list)} -----")
                [self.validate_request(mail) for mail in mail_request_list]
                [self.db_instance.mail_insert(False, mail.MAIL_TIME, mail.MAIL_FROM, mail.MAIL_SUBJECT, mail.REQUEST_FUNCTION, mail.REQUEST_TARGET) for mail in mail_request_list]
                wrong_mails = self.filter_wrong_email(mail_request_list)
                mail_request_list = [mail for mail in mail_request_list if mail not in wrong_mails]
                expired_mails = self.filter_expired_email(mail_request_list)
                mail_request_list = [mail for mail in mail_request_list if mail not in expired_mails]
                rejected_mails = self.filter_rejected_email(mail_request_list)
                mail_request_list = [mail for mail in mail_request_list if mail not in rejected_mails]
                delete_mails = list(set(wrong_mails + expired_mails + rejected_mails))
                for mail_request in mail_request_list:
                    log.log("mail", f"Processing email: {mail_request.MAIL_ID} - time: {mail_request.MAIL_TIME}, from: {mail_request.MAIL_FROM}, subject: {mail_request.MAIL_SUBJECT}, jobs: {len(mail_request.REQUEST_TARGET)}")
                    mail_response = MailResponse()
                    mail_response.set_sender(self.env_instance.mail_user)
                    mail_response.set_receiver(mail_request.MAIL_FROM)
                    mail_response.set_subject(f'osintbot response to: {mail_request.MAIL_SUBJECT} for {len(mail_request.REQUEST_TARGET)} jobs')
                    mail_response.set_content(self.run_function(mail_request))
                    self.send_email(mail_response)
                    delete_mails.append(mail_request)
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
                log.exception("mail", "IMAP connection failed", e)
                time.sleep(60)
    def imap_disconnect(self):
        try:
            self.IMAP.close()
            self.IMAP.logout()
        except Exception as e:
            log.exception("mail", "IMAP disconnection failed", e)

    def smtp_connect(self):
        while Exception:
            try:
                self.SMTP = smtplib.SMTP(self.env_instance.smtp_server, self.env_instance.smtp_port)
                self.SMTP.starttls()
                self.SMTP.login(self.env_instance.mail_user, self.env_instance.mail_password)
                break
            except Exception as e:
                log.exception("mail", "SMTP connection failed", e)
                time.sleep(60)
    def smtp_disconnect(self):
        try:
            self.SMTP.quit()
        except Exception as e:
            log.exception("mail", "SMTP disconnection failed", e)





    def delete_email(self, mail_list: list) -> None:
        try:
            for mail in mail_list:
                self.IMAP.store(mail.MAIL_ID, '+FLAGS', '\\Deleted')
            self.IMAP.expunge()
            log.log("mail", f"--> Emails deleted successfully: {len(mail_list)}") if mail_list else None
        except Exception as e:
            log.exception("mail", "Email failed to delete", e)

    def filter_wrong_email(self, mail_list: list) -> None:
        try:
            wrong_emails = []
            for mail in mail_list:
                if not mail.REQUEST_STATUS:
                    log.log("mail", f"--> Wrong email {mail.MAIL_ID}. From: {mail.MAIL_FROM}, Subject: {mail.MAIL_SUBJECT}, Time: {mail.MAIL_TIME}")
                    wrong_emails.append(mail)
                    self.db_instance.mail_refused(mail.MAIL_TIME, mail.MAIL_FROM, mail.MAIL_SUBJECT)
            log.log("mail", f"--> Wrong emails overall: {len(wrong_emails)}") if wrong_emails else None
            return wrong_emails
        except Exception as e:
            log.exception("mail", "Could not sort wrong emails", e)
        
    def filter_expired_email(self, mail_list: list) -> None:
        try:
            expired_emails = []
            for mail in mail_list:
                if time.time() - time.mktime(time.strptime(mail.MAIL_TIME, '%d-%b-%Y %H:%M:%S')) > self.mail_expire:
                    log.log("mail", f"--> Expired email {mail.MAIL_ID}. From: {mail.MAIL_FROM}, Subject: {mail.MAIL_SUBJECT}, Time: {mail.MAIL_TIME}")
                    expired_emails.append(mail)
                    self.db_instance.mail_refused(mail.MAIL_TIME, mail.MAIL_FROM, mail.MAIL_SUBJECT)
            log.log("mail", f"--> Expired emails overall: {len(expired_emails)}") if expired_emails else None
            return expired_emails
        except Exception as e:
            log.exception("mail", "Could not sort expired emails", e)
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
                        self.db_instance.mail_refused(mail.MAIL_TIME, mail.MAIL_FROM, mail.MAIL_SUBJECT)
                        if mail.MAIL_FROM not in rejected_sender:
                            rejected_sender.append(mail.MAIL_FROM)
            # inform the sender about the rejected emails
            for sender in rejected_sender:
                message = "Some of your emails have been rejected due to multiple submissions. Wait until your previous request has been processed before submitting a new one."
                deleted_mails = []
                for mail in rejected_mails:
                    deleted_mails.append(f"{mail.MAIL_TIME} --> {mail.MAIL_SUBJECT}")
                message += f"\n\nThe following emails were deleted:\n{chr(10).join(deleted_mails)}"
                rejected_mails_response = MailResponse()
                rejected_mails_response.set_sender(self.env_instance.mail_user)
                rejected_mails_response.set_receiver(sender)
                rejected_mails_response.set_subject('osintbot rejected emails')
                rejected_mails_response.set_body(message)
                self.send_email(rejected_mails_response)
            # remove all remaining mails of the sender
            log.log("mail", f"--> Rejected emails overall: {len(rejected_mails)}") if rejected_mails else None
            return rejected_mails
        except Exception as e:
            log.exception("mail", "Could not sort rejected emails", e)





    def send_email(self, mail: MailResponse):
        try:
            self.smtp_connect()
            self.SMTP.sendmail(mail.mail['From'], mail.mail['To'], mail.mail.as_string())
            self.SMTP.quit()
            log.log("mail", f"--> Response sent successfully. To: {mail.mail['To']}, Subject: {mail.mail['Subject']}")
        except Exception as e:
            log.exception("mail", f"Email failed to send. To: {mail.mail['To']}, Subject: {mail.mail['Subject']}", e)

    def fetch_email(self):
        try:
            self.IMAP.select('inbox')
            status, messages = self.IMAP.search(None, '(TO ' + self.env_instance.mail_user + ')')
            messages = messages[0].split()
            mail_list = []
            for mail_id in messages:
                mail_list.append(MailRequest(mail_id, self.IMAP.fetch(mail_id, '(RFC822)')[1][0][1].decode('utf-8')))
            return mail_list
        except Exception as e:
            log.exception("mail", "Email failed to fetch", e)





    def run_function(self, mail_request: MailRequest):
        try:
            if mail_request.REQUEST_FUNCTION == 'help':
                return self.HELP
            response = []
            function = self.FUNCTIONS[mail_request.REQUEST_FUNCTION]
            for target in mail_request.REQUEST_TARGET:
                log.log("mail", f"--> Running function: '{mail_request.REQUEST_FUNCTION}' with input: '{target}'")
                result = function(input=target, function=mail_request.REQUEST_FUNCTION)
                response.append({"target": target, "result": result})
                time.sleep(10)
            return kit_helper.json_to_string(response)
        except Exception as e:
            log.exception("mail", f"Function failed to run: '{mail_request.REQUEST_FUNCTION}'", e)
        
    def validate_request(self, mail_request: MailRequest):
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&'()*+,;="
        request_status = True
        request = mail_request.MAIL_SUBJECT.split(' ')
        target = []

        if len(request) == 0:
            request_status = False
            log.log("mail", "No query args in mail subject")
        elif len(request) == 1:
            target = mail_request.MAIL_BODY.splitlines() if mail_request.MAIL_BODY else []
            if len(target) > 5:
                request_status = False
                log.log("mail", "Too many query args in mail body")
        elif len(request) == 2:
            target = [request[1]]
        elif len(request) > 2:
            request_status = False
            log.log("mail", "Too many query args in mail subject")

        function = request[0].lower()
        target = [item.lower() for item in target]

        if not all(c in allowed_chars for c in function):
            request_status = False
            log.log("mail", "Invalid characters in function")

        for item in target:
            if not all(c in allowed_chars for c in item):
                request_status = False
                log.log("mail", "Invalid characters in query args")

        if request_status:
            if function in self.FUNCTIONS:
                mail_request.REQUEST_FUNCTION = shlex.quote(function)
                mail_request.REQUEST_TARGET = [shlex.quote(item) for item in target]
                mail_request.REQUEST_STATUS = True
            else:
                log.log("mail", f"Invalid request function: '{function}'")

                mail_request.REQUEST_STATUS = False
        else:
            mail_request.REQUEST_STATUS = False





def main():
    if os.path.isfile('.env'):
        load_dotenv(dotenv_path='.env')
    Mailbot()

if __name__ == '__main__':
    main()
