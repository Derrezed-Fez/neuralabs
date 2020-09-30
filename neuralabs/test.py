import threading
import smtpd
import asyncore
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content('TEST EMAIL')
msg['Subject'] = 'SUPER TEST'
msg['From'] = 'zpelleti@emich.edu'
msg['To'] = 'zpelleti@emich.edu'

# Send the message via our own SMTP server.
server = smtpd.SMTPServer(('localhost', 1025), None)
loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
loop_thread.start()
client = smtplib.SMTP('localhost', port=1025)
client.send_message(msg)
client.quit()
