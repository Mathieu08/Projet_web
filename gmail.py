# coding: utf8

# Copyright 2017 Jacques Berger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

class Gmail(object):

    def __init__(self):	
        self.source_address = "projet.inf3005@gmail.com"

    def envoyer_mail(self, adress, subject, body):
        destination_address = adress
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.source_address
        msg['To'] = destination_address

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.source_address, "secret_inf3005")
        text = msg.as_string()
        server.sendmail(self.source_address, destination_address, text)
        server.quit()