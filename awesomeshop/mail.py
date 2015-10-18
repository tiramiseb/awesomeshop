from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from flask import render_template

from . import app, get_locale

def send_message(recipient, msg_id, **kwargs):
    locale = kwargs.get('locale', get_locale())
    # Get the message content
    sender = app.config['MAIL_FROM']
    subject = render_template('email/{}/{}.subject'.format(msg_id, locale),
                              **kwargs)
    text = render_template('email/{}/{}.txt'.format(msg_id, locale), **kwargs)
    html = render_template('email/{}/{}.html'.format(msg_id, locale),
                           subject=subject, **kwargs)
    # Create the message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    part_text = MIMEText(text.encode('utf8'), 'plain')
    part_html = MIMEText(html.encode('utf8'), 'html')
    msg.attach(part_text)
    msg.attach(part_html)
    s = smtplib.SMTP(app.config['SMTP_SERVER'])
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()
