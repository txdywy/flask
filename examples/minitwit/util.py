import smtplib
import email.utils
from email.mime.text import MIMEText
ALANCER_SUPPORT = 'support@alancer.cf'

def makes(s):
    if type(s)==unicode:
        return s.encode('utf8','ignore')
    else:
        return s

def makeu(s):
    if type(s)==str:
        return s.decode('utf8','ignore')
    else:
        return s

def send_email(title, content, addr_to, addr_fr=None):
    # Create the message
    if not addr_fr:
        addr_fr = ALANCER_SUPPORT   
    msg = MIMEText(makes(content), 'html')
    msg['To'] = email.utils.formataddr(('Recipient', addr_to))
    msg['From'] = email.utils.formataddr(('Alancer', addr_fr))
    msg['Subject'] = title

    server = smtplib.SMTP('localhost')
    #server.set_debuglevel(True) # show communication with the server
    try:
        server.sendmail(addr_fr, [addr_to], msg.as_string())
    finally:
        server.quit()
