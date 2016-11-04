# -*- coding: utf8 -*-

# Copyright 2015-2016 Sébastien Maccagnoni
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

from flask import render_template, request

from . import app, get_locale


def send_mail(recipient, template, **kwargs):
    if app.config['SEND_MAILS']:
        locale = kwargs.get('locale') or get_locale()
        # Get the message content
        sender = app.config['MAIL_FROM']
        subject = render_template('email/{}/{}.subject'.format(template,
                                                               locale),
                                  root=request.url_root, **kwargs)
        text = render_template('email/{}/{}.txt'.format(template, locale),
                               root=request.url_root, **kwargs)
        html = render_template('email/{}/{}.html'.format(template, locale),
                               subject=subject, root=request.url_root,
                               **kwargs)
        # Create the message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        part_text = MIMEText(text.encode('utf8'), 'plain', 'utf-8')
        part_html = MIMEText(html.encode('utf8'), 'html', 'utf-8')
        msg.attach(part_text)
        msg.attach(part_html)
        # TODO Delay the message when the SMTP server is not available
        s = smtplib.SMTP(app.config['SMTP_SERVER'])
        s.sendmail(sender, recipient, msg.as_string())
        s.quit()
