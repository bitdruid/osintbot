

class Mail:
    
    MAIL_ID = None
    MAIL_TIME = None
    MAIL_FROM = None
    MAIL_SUBJECT = None
    MAIL_BODY = None

    def __init__(self, mail_id: bytes, mail_time: str, mail_from: str, mail_subject: str, mail_body: str):
        self.MAIL_ID = mail_id
        self.MAIL_TIME = mail_time
        self.MAIL_FROM = mail_from
        self.MAIL_SUBJECT = mail_subject
        self.MAIL_BODY = mail_body