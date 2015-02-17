import smtplib
import email.utils
from email.mime.text import MIMEText
ALANCER_SUPPORT = 'support@alancer.cf'

def send_email(title, content, addr_to, addr_fr=None):
    # Create the message
    if not addr_fr:
        addr_fr = ALANCER_SUPPORT   
    msg = MIMEText(content)
    msg['To'] = email.utils.formataddr(('Recipient', addr_to))
    msg['From'] = email.utils.formataddr(('Alancer', addr_fr))
    msg['Subject'] = title

    server = smtplib.SMTP('localhost')
    #server.set_debuglevel(True) # show communication with the server
    try:
        server.sendmail(addr_fr, [addr_to], msg.as_string())
    finally:
        server.quit()
