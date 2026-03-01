import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_gmail_to_everyone(email_queue):
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    if not sender_email or not app_password:
        print("Error: Missing SENDER_EMAIL or APP_PASSWORD in environment variables.")
        return

    try:
        print("Connecting to Gmail server...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
        server.login(sender_email, app_password)

        for item in email_queue:
            recipient = item.get("email")
            subject = item.get("subject")
            body = item.get("matter")

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server.send_message(msg)
            print(f"Successfully sent to: {recipient}")

        server.quit()
        print("All emails sent successfully.")

    except Exception as e:
        print(f"SMTP Error: {e}")
