import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import osintbot.log as log

class MailResponse:

    def __init__(self):
        self.mail = MIMEMultipart()

    def set_sender(self, sender):
        self.mail['From'] = sender

    def set_receiver(self, receiver):
        self.mail['To'] = receiver

    def set_subject(self, subject):
        self.mail['Subject'] = subject

    def set_content(self, response_contents: list):
        try:
            
            # if there is only one response, check if it is a file or text
            if len(response_contents) == 1:

                if isinstance(response_contents[0]['result'], list): # check if the result is a list of files
                    for file_path in response_contents[0]['result']:
                        self.attach_file(file_path)
                elif not os.path.isfile(response_contents[0]['result']): # check if the result is not a file
                    self.mail.attach(MIMEText(response_contents[0]['result'], 'plain'))
                else: # else attach the result as just one file
                    self.attach_file(response_contents[0]['result'])

            # if there are multiple responses, check if they are files or text
            if len(response_contents) > 1:
                for entry in response_contents:
                    if isinstance(entry['result'], list): # check if the result is a list of files
                        for file_path in entry['result']:
                            self.attach_file(file_path)
                    elif os.path.isfile(entry['result']): # check if the result is a filepath and attach it as a file
                        self.attach_file(entry['result'])
                    else: # else attach the result as plain text
                        self.attach_text(entry['target'], entry['result'])

        except Exception as e:
            log.exception("mail", "Error parsing response-mail content", e)

    # attach a file to the mail
    def attach_file(self, file_path):
        attachment = MIMEApplication(open(file_path, 'rb').read())
        attachment.add_header('Content-Disposition', f"attachment; filename={os.path.basename(file_path)}")
        self.mail.attach(attachment)
        os.remove(file_path)

    # attach a text as text file to the mail
    def attach_text(self, target, result):
        attachment = MIMEText(result, 'plain')
        attachment.add_header('Content-Disposition', f"attachment; filename={target}.txt")
        self.mail.attach(attachment)