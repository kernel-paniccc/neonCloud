import smtplib
import main_mod.sec
from email.mime.text import MIMEText
from email.header import Header

def send_ya_mail(recipients_emails: str, msg_text: str):
    login = main_mod.sec.login
    password = main_mod.sec.password

    msg = MIMEText(f'{msg_text}', 'plain', 'utf-8')
    msg['Subject'] = Header('Yor code for Neon Cloud', 'utf-8')
    msg['From'] = login
    msg['To'] = recipients_emails

    s = smtplib.SMTP('smtp.yandex.ru', 587, timeout=10)

    s.starttls()
    s.login(login, password)
    s.sendmail(msg['From'], recipients_emails, msg.as_string())