# -*- coding: utf8 -*-

# Copyright 2015 Sébastien Maccagnoni-Munch
#
# This file is part of AwesomeShop.
#
# AwesomeShop is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# AwesomeShop is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AwesomeShop. If not, see <http://www.gnu.org/licenses/>.

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
