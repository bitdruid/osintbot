import os
import sys
from dotenv import load_dotenv
import time
import smtplib
import imaplib

class Mail:

    IMAP = None
    SMTP = None

    FUNCTION = None
    INPUT = None

    def __init__(self):
        self.mail_expire = 60
        self.connection_expire = 60
        self.email = os.getenv('MAIL_USER') if os.getenv('MAIL_USER') else sys.exit('No email provided')
        self.password = os.getenv('MAIL_PASS') if os.getenv('MAIL_PASS') else sys.exit('No password provided')
        self.smtp_server = os.getenv('MAIL_SMTP_SERVER') if os.getenv('MAIL_SMTP_SERVER') else sys.exit('No SMTP server provided')
        self.smtp_port = os.getenv('MAIL_SMTP_PORT') if os.getenv('MAIL_SMTP_PORT') else sys.exit('No SMTP port provided')
        self.imap_server = os.getenv('MAIL_IMAP_SERVER') if os.getenv('MAIL_IMAP_SERVER') else sys.exit('No IMAP server provided')
        self.imap_port = os.getenv('MAIL_IMAP_PORT') if os.getenv('MAIL_IMAP_PORT') else sys.exit('No IMAP port provided')
        self.imap_loop()

    def imap_loop(self):
        current_time = time.time()
        self.imap_connect()
        while True:
            mail_dict = self.read_email()
            if mail_dict:
                for mail_id in mail_dict:
                    time.sleep(1)
                    if not self.parse_subject(mail_dict[mail_id]):
                        continue
                    self.send_email(mail_dict[mail_id]['from'], 'osintbot response to: "' + self.FUNCTION + ' ' + self.INPUT + '"', self.run_function())
                    #self.imap_delete(imap, mail_id)

            if time.time() - current_time > self.connection_expire:
                print(f'Connection expired. Reconnecting to IMAP server {self.imap_server}.')
                self.imap_disconnect()
                current_time = time.time()
                self.imap_connect()
            time.sleep(10)

    def imap_connect(self):
        self.IMAP = imaplib.IMAP4_SSL(self.imap_server)
        self.IMAP.login(self.email, self.password)

    def imap_disconnect(self):
        self.IMAP.close()

    def smtp_connect(self):
        self.SMTP = smtplib.SMTP(self.smtp_server, self.smtp_port)
        self.SMTP.starttls()
        self.SMTP.login(self.email, self.password)

    def smtp_disconnect(self):
        self.SMTP.quit()

    def imap_delete(self, mail_id):
        try:
            self.IMAP.store(mail_id, '+FLAGS', '\\Deleted')
            self.IMAP.expunge()
            print('Email deleted successfully')
        except Exception as e:
            print('Email failed to delete')
            print(e)

    def send_email(self, to, subject, message):
        try:
            self.smtp_connect()
            message = f'Subject: {subject}\n\n{message}'
            self.SMTP.sendmail(self.email, to, message)
            self.SMTP.quit()
            print('Email sent successfully')
        except Exception as e:
            print('Email failed to send')
            print(e)

    def read_email(self):
        try:
            self.IMAP.select('inbox')
            mail_dict = {}
            status, messages = self.IMAP.search(None, '(TO "osintbot@apfelbaum.cloud")')
            messages = messages[0].split()
            print('Emails found:', len(messages))
            mail_expired = []
            for mail_id in messages:
                mail_time = self.IMAP.fetch(mail_id, '(INTERNALDATE)')[1][0].decode().split('INTERNALDATE ')[1].split('"')[1].split(' +')[0].strip()
                # if time.time() - time.mktime(time.strptime(mail_time, '%d-%b-%Y %H:%M:%S')) > self.mail_expire:
                #     print(f"Email {mail_id} expired - {mail_time}. Deleting email.")
                #     mail_expired.append(mail_id)
                #     continue
                mail_from = self.IMAP.fetch(mail_id, '(BODY[HEADER.FIELDS (FROM)])')[1][0][1].decode().split('<')[1].split('>')[0].strip()
                mail_subject = self.IMAP.fetch(mail_id, '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1].decode().split('Subject: ')[1].removesuffix('\r\n\r\n').strip()
                mail_dict[mail_id] = {'from': mail_from, 'subject': mail_subject, 'time': mail_time}
            # for mail_id in mail_expired:
            #     self.imap_delete(imap, mail_id)
            return mail_dict
        except Exception as e:
            print('Failed to read email')
            print(e)

    def parse_subject(self, mail):
        try:
            subject = mail['subject']
            arguments = subject.split(' ')
            self.FUNCTION = arguments[0].lower()
            self.INPUT = arguments[1].lower()
            return True
        except:
            message = 'Invalid subject. Please use the following format: <function> <input>. Send an email with subject help/start for more information.'
            self.send_email(mail['from'], 'osintbot invalid subject: "' + self.FUNCTION + ' ' + self.INPUT + '"', message)
            self.imap_delete(mail)
            return False
    
    def run_function(self):
        if self.FUNCTION and self.INPUT:
            if self.FUNCTION == 'whois':
                import osintkit.whois as whois
                response = whois.request(self.INPUT)
            if self.FUNCTION == 'geoip':
                import osintkit.geoip as geoip
                response = geoip.request(self.INPUT)
            if self.FUNCTION == 'iplookup':
                import osintkit.iplookup as iplookup
                response = iplookup.request(self.INPUT)
            if self.FUNCTION == 'arecord':
                import osintkit.arecord as arecord
                response = arecord.request(self.INPUT)
            message = ""
            for key in response:
                message += response[key]
            return message

def main():
    if os.path.isfile('.env'):
        load_dotenv(dotenv_path='.env')
    Mail() 

if __name__ == '__main__':
    main()