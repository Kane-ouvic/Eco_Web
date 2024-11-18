import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import json

class MailHandler:
    _host_email_address: str
    _host_passwd: str
    _subject: str
    
    def __init__(self):
        gmail_acct = "/home/ouvic/Eco_Web/config/gmail.json"
        with open(gmail_acct, "r") as f:
            gmail_acct = json.load(f)
        self._host_email_address = gmail_acct["email"]
        self._host_passwd = gmail_acct["password"]
        self._smtp_server = gmail_acct["smtp_server"]
        self._smtp_port = gmail_acct["smtp_port"]
        
        self._smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self._smtp.ehlo()
        self._smtp.login(self._host_email_address, self._host_passwd)
        self._local_time = datetime.date.today()
    
    def _create_mail(self, subject: str, to_address: str):
        mail = MIMEMultipart()
        mail["From"] = self._host_email_address
        mail["To"] = to_address
        mail["Subject"] = subject
        return mail
    
    def _add_file(self, mail: MIMEMultipart, file: str):
        with open(file, "rb") as fp:
            attach_file = MIMEBase("application", "octet-stream")
            attach_file.set_payload(fp.read())
        encoders.encode_base64(attach_file)
        attach_file.add_header("Content-Disposition", f"attachment", filename=f"{self._local_time}_signals_report.xlsx")
        mail.attach(attach_file)

    def send(self, to_address, file_path):
        mail = self._create_mail(f"Monitor Report {self._local_time}", to_address)
        contents = "This is signals report."
        mail.attach(MIMEText(contents))
        self._add_file(mail, file_path)
        status = self._smtp.sendmail(self._host_email_address, to_address, mail.as_string())
        
        return status