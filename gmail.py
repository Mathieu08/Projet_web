# coding: utf8

import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Gmail(object):

    def __init__(self):
        with open('email.json') as email_data:
            data = json.load(email_data)
            self.source_address = data['adresse']
            self.source_password = data['password']

    def envoyer_mail(self, adress, subject, body):
        destination_address = adress

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.source_address
        msg['To'] = destination_address

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.source_address, self.source_password)
        text = msg.as_string()
        server.sendmail(self.source_address, destination_address, text)
        server.quit()
