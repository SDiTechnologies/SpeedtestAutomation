from pathlib import Path
from smtplib import SMTP  # (port 25)
# from smtplib import SMTP_SSL as SMTP   # (port 465)
from email.mime.text import MIMEText

from .Loggers import Logger

class Email:
    from_addr:str
    to_addr:list[str]
    subject:str
    content: str
    text_subtype: str = 'plain'

class SmtpHandler:
    host:str
    port:str
    username:str
    password:str
    _logger: Logger = Logger()

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, email:Email):
        try:
            msg = MIMEText(email.content, email.text_subtype)
            msg["Subject"] = email.subject
            msg["From"] = email.from_addr

            with SMTP(self.host) as conn:
                conn.set_debuglevel(False)
                conn.login(self.username, self.password)
                try:
                    conn.sendmail(email.from_addr, email.to_addr, msg.as_string())
                finally:
                    conn.close()
        except Exception as e:
            print(e)


class DummySmtpHandler(SmtpHandler):
    path:str
    host:str
    port:str
    username:str
    password:str

    def __init__(self, path='email.txt', host=None, port=None, username=None, password=None):
        self.path = Path('.').joinpath('mail', path)
        super().__init__(host, port, username, password)

    def send(self, email:Email):
        self._logger.log("(DummySmtpHandler): Attempting to Send Email")
        try:
            msg = MIMEText(email.content, email.text_subtype)
            msg["Subject"] = email.subject
            msg["From"] = email.from_addr
            with open(self.path, 'w') as conn:
                try:
                    output = [f"FROM: {email.from_addr}", f"TO: [{email.to_addr}]", f"{msg.as_string()}"]
                    conn.writelines(output)
                finally:
                    conn.close()
                    self._logger.log("(DummySmtpHandler): Email Successfully 'Sent'")
        except Exception as e:
            self._logger.log(f"(DummySmtpHandler) Exception: Email 'Send' Failed - {e}")