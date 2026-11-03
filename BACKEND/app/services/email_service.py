import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import settings


class EmailService:
    def __init__(self):
        self.smtp_server = getattr(settings, "SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_email = getattr(settings, "SMTP_EMAIL", None)
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", None)
        self.from_email = getattr(settings, "FROM_EMAIL", self.smtp_email)

    def is_configured(self) -> bool:
        return bool(self.smtp_email and self.smtp_password)

    def send_password_reset_email(self, email: str, reset_link: str) -> bool:
        if not self.is_configured():
            return False

        subject = "Reset Your NoteFlow Password"
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #172554;">Password Reset Request</h2>
              <p>Hello,</p>
              <p>We received a request to reset your NoteFlow password. If you made this request, click the link below to set a new password:</p>
              <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background: linear-gradient(135deg, #4f46e5 0%, #172554 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
              </p>
              <p style="color: #666; font-size: 14px;">Or copy and paste this link in your browser:</p>
              <p style="color: #666; font-size: 12px; word-break: break-all;">{reset_link}</p>
              <p style="color: #999; font-size: 12px;">This link expires in 1 hour.</p>
              <p style="margin-top: 30px; color: #999; font-size: 12px;">
                If you didn't request this, please ignore this email or contact support.
              </p>
              <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
              <p style="color: #999; font-size: 12px; text-align: center;">
                © 2026 NoteFlow. All rights reserved.
              </p>
            </div>
          </body>
        </html>
        """

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = email
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.sendmail(self.from_email, [email], msg.as_string())
            return True
        except Exception:
            return False


email_service = EmailService()
