import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os, sys
from glob import glob


def notify_me(smtp_server, sender_email, port, password, receiver_email,
              subject, body, filename, now):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Attaching log file
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


########################################################################################################################
########################################################################################################################

if __name__ == '__main__':

    now = datetime.now().strftime('%Y/%m/%d at %H:%M')
    smtp_server = "smtp.gmail.com"
    port = 465  # For starttls
    sender_email = "myapp.andreaperin@gmail.com"
    password = 'c327841b53823f6a7e6c0f787a5a3e4b'
    receiver_email = "andrea.perin1992@gmail.com"
    subject = f"Mail related to run '{now}'"

    filepath = '../logs/main'
    glob_pattern = os.path.join(filepath, '*')
    log_file = max(glob(glob_pattern), key=os.path.getctime)

    body = ''
    with open(log_file, 'r') as lf:
        for line in lf:
            if 'WARNING' in line:
                body = body + line + '\n'
    try:
        notify_me(smtp_server=smtp_server,
                sender_email=sender_email,
                port=port,
                password=password,
                receiver_email=receiver_email,
                subject=subject,
                body=body,
                filename=log_file,
                now=now)
    except Exception as e:
        print(e)