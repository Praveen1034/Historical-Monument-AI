import os
import smtplib
import imaplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Email config
EMAIL_CONFIG = {
    "user_email": os.getenv("USER_EMAIL"),
    "user_password": os.getenv("USER_PASSWORD"),
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),    
    "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
    "imap_port": int(os.getenv("IMAP_PORT", 993)),
    "sent_folder": os.getenv("SENT_FOLDER", "Sent Mail"),
}

# Temporary in-memory storage for OTPs
otp_store = {}

# --- EMAIL FUNCTION (from previous) ---
def send_email(to_addr, subject, body, html=None):
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_CONFIG["user_email"]
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg['Message-ID'] = msg.get('Message-ID') or make_msgid()

    msg.attach(MIMEText(body, 'plain'))
    if html:
        msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"], timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_CONFIG["user_email"], EMAIL_CONFIG["user_password"])
            server.send_message(msg)
            print(f"[INFO] OTP sent to {to_addr}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

# --- OTP GENERATOR FUNCTION ---
def generate_and_send_otp(email: str):
    try:
        if not email:
            raise ValueError("Email address is required.")
        otp = str(random.randint(100000, 999999))
        expires_at = datetime.now() + timedelta(minutes=5)

        otp_store[email] = {
            "otp": otp,
            "expires_at": expires_at
        }

        body = f"Your OTP code is: {otp}\nIt will expire in 5 minutes."

        send_email(
            to_addr=email,
            subject="Your OTP Code",
            body=body)
        return f"[INFO] OTP generated and sent to {email}"
    except Exception as e:
        print(f"[ERROR] Failed to generate or send OTP: {e}")

# --- OTP VALIDATOR FUNCTION ---
def validate_otp(email: str, input_otp: str) -> bool:
    try:
        if not email or not input_otp:
            raise ValueError("Email and OTP code are required.")
        record = otp_store.get(email)
        if not record:
            print("[ERROR] No OTP generated for this email.")
            return False

        if datetime.now() > record["expires_at"]:
            print("[ERROR] OTP has expired.")
            del otp_store[email]
            return False

        if record["otp"] == input_otp:
            print("[SUCCESS] OTP is valid.")
            del otp_store[email]  # remove OTP after successful validation
            return True
        else:
            print("[ERROR] Invalid OTP.")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to validate OTP: {e}")
        return False

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    user_email = input("Enter your email: ")

    generate_and_send_otp(user_email)

    user_input = input("Enter the OTP you received: ")
    is_valid = validate_otp(user_email, user_input)

    if is_valid:
        print("✅ Access granted.")
    else:
        print("❌ Access denied.")
