import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_email(to_email, subject, body):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")

    try:
        # Email content
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect and send the email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"Email sent successfully to {to_email}.")
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
    except Exception as e:
        print(f"General error: {e}")

# Example usage
if __name__ == "__main__":
    send_email("recipient@example.com", "Test Subject", "Test Body")
