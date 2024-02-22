import shlex
import time
import osintbot.log as log

class Mail:
    
    MAIL_ID = None
    MAIL_TIME = None
    MAIL_FROM = None
    MAIL_SUBJECT = None
    MAIL_BODY = None

    REQUEST_FUNCTION = None
    REQUEST_TARGET = None
    REQUEST_STATUS = None

    def __init__(self, mail_id, mail_full):
        try:
            self.MAIL_ID = mail_id
            self.MAIL_TIME = mail_full.split('Date: ')[1].split('\r\n')[0].strip()
            self.MAIL_TIME = time.strftime('%d-%b-%Y %H:%M:%S', time.strptime(self.MAIL_TIME, '%a, %d %b %Y %H:%M:%S %z'))
            self.MAIL_FROM = mail_full.split('From: ')[1].split('\r\n')[0].strip()
            self.MAIL_FROM = self.MAIL_FROM.split('<')[1].split('>')[0] if '<' in self.MAIL_FROM else self.MAIL_FROM
            self.MAIL_SUBJECT = mail_full.split('Subject: ')[1].split('\r\n')[0].strip()
            self.MAIL_BODY = mail_full.split('\r\n\r\n')[1].strip()
            self.parse_mail_request()
        except Exception as e:
            log.log("mail", "!-- Mail failed to parse")
            log.exception("mail", e)

    def parse_mail_request(self):
        allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789.-'
        try:
            request = self.MAIL_SUBJECT.split(' ')
            if len(request) != 2:
                raise Exception('Invalid mail request')
            function = request[0]
            target = request[1]
            if not all(c in allowed_chars for c in function):
                raise Exception('Invalid mail function')
            if not all(c in allowed_chars for c in target):
                raise Exception('Invalid mail args')
            self.REQUEST_FUNCTION = shlex.quote(function)
            self.REQUEST_TARGET = shlex.quote(target)
            self.REQUEST_STATUS = True
        except Exception as e:
            self.REQUEST_STATUS = False
            log.log("mail", "!-- Invalid mail request: " + self.MAIL_SUBJECT)


