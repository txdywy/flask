from config import SMTP_SETTINGS
import smtplib
import email.utils
from email.mime.text import MIMEText

# Prompt the user for connection info
to_email = raw_input('Recipient: ')
servername = SMTP_SETTINGS['smtp_server']
username = SMTP_SETTINGS['smtp_user']
password = SMTP_SETTINGS['smtp_passwd']
support = 'geniusron@gmail.com'

# Create the message
msg = MIMEText('Test message from PyMOTW.')
msg.set_unixfrom('author')
msg['To'] = email.utils.formataddr(('Recipient', to_email))
msg['From'] = email.utils.formataddr(('Author', support))
msg['Subject'] = 'Test from PyMOTW'

server = smtplib.SMTP(servername)
try:
    server.set_debuglevel(True)

    # identify ourselves, prompting server for supported features
    server.ehlo()

    # If we can encrypt this session, do it
    if server.has_extn('STARTTLS'):
        server.starttls()
        server.ehlo() # re-identify ourselves over TLS connection

    server.login(username, password)
    server.sendmail(support, [to_email], msg.as_string())
finally:
    server.quit()
