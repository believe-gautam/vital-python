import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    smtp_server = "smtp.hostinger.com"
    smtp_port = 465
    sender_email = "development@livepbx.us"  
    password = "@1234#Google"  

    try:
        # Email content
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:  
            server.login(sender_email, password)  
            server.send_message(msg)  
            print(f"Email sent successfully to {to_email}.")
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
    except Exception as e:
        print(f"General error: {e}")
