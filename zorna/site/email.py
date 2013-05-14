from django.core import mail
from django.conf import settings
from django.template.loader import render_to_string

class ZornaEmail(object):

    def __init__(self):
        self.emails = []

    def append(self, subject='', body_txt='', body_html='', from_email=None, to=None, bcc=None,
            attachments=None, headers=None, alternatives=None,
            cc=None):
        content = render_to_string(['text_email_template.html', 'site/text_email_template.html'], {'body': body_txt})
        email = mail.EmailMultiAlternatives(subject, content, from_email or settings.DEFAULT_FROM_EMAIL, to, bcc, None, attachments, headers, cc)
        if body_html:
            content = render_to_string(['html_email_template.html', 'site/html_email_template.html'], {'body': body_html})
            email.attach_alternative(content, 'text/html')

        self.emails.append(email)
        return email

    def send(self):
        if self.emails:
            connection = mail.get_connection()
            connection.open()
            connection.send_messages(self.emails)
            connection.close()
