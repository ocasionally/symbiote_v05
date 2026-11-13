# -*- coding: utf-8 -*-
"""
Mailer - notification email via Gmail SMTP for the controlled-environment exercise.
Credentials are asked at startup and kept in memory only (never written to disk).
Use:  send <email>   (from the tool's monitor prompt)
For use in controlled environments only.
"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from getpass import getpass

CYAN, GREEN, RED, YELLOW, DEFAULT = '\033[1;36m', '\033[1;32m', '\033[1;91m', '\033[1;33m', '\033[0m'
TEMPLATE = 'Server/email_template.html'
SMTP_HOST, SMTP_PORT = 'smtp.gmail.com', 587
FROM_NAME = 'Veridia Solutions \u00b7 Talento Humano'
SUBJECT = 'Acci\u00f3n requerida: Verificaci\u00f3n de identidad facial \u2014 plazo 30/11/2026'


def askConfig():
    """Asks for the sender Gmail + app password. ENTER = skip. Returns dict or None."""
    print("\n[{0}#{1}] Notification email (Gmail SMTP)\n".format(CYAN, DEFAULT))
    print("  Sender account + app password (16 chars, https://myaccount.google.com/apppasswords).")
    print("  Press ENTER twice to skip; the 'send' command stays disabled.\n")
    user = input("  Sender Gmail: ").strip()
    if not user or '@' not in user:
        print("\n  [{0}*{1}] Email sending disabled.\n".format(YELLOW, DEFAULT))
        return None
    pwd = getpass("  App password (hidden): ").strip().replace(' ', '')
    return {'user': user, 'pass': pwd}


def sendMail(to, link, cfg):
    """Sends the template email to 'to' with 'link' injected. Returns None on success, error string otherwise."""
    try:
        with open(TEMPLATE, encoding='utf-8') as f:
            html = f.read().replace('{{LINK}}', link)
    except OSError as e:
        return 'email template not found: %s' % e

    plain = (
        "VERIDIA SOLUTIONS - TALENTO HUMANO\n\n"
        "Estimado(a) colaborador,\n\n"
        "Todo el personal activo debe completar la VERIFICACION DE IDENTIDAD FACIAL\n"
        "a traves del Portal del Empleado. El proceso toma menos de un minuto.\n\n"
        "-> %s\n\n"
        "PLAZO: 30 de noviembre de 2026. Vencido el plazo, el acceso a los sistemas\n"
        "internos se suspendera preventivamente.\n\n"
        "Dudas: Julian Restrepo - Talento Humano (j.restrepo@veridia-solutions.com)\n\n"
        "Veridia Solutions S.A. - NIT 901.234.567-8\n"
        "Este mensaje es parte de un ejercicio academico en ambiente controlado.\n" % link
    )

    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = formataddr((FROM_NAME, cfg['user']))
    msg['To'] = to
    msg.attach(MIMEText(plain, 'plain', 'utf-8'))
    msg.attach(MIMEText(html, 'html', 'utf-8'))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls(context=ctx)
            s.login(cfg['user'], cfg['pass'])
            s.send_message(msg)
    except Exception as e:
        return str(e)
    return None
