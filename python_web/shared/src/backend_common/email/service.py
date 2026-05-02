"""Async email sending service via SMTP.

Provides a simple interface for sending HTML emails, with a convenience
method for verification code delivery.
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

logger = logging.getLogger(__name__)


class EmailService:
    """Async SMTP email service for sending HTML messages.

    Attributes:
        smtp_host: SMTP server hostname.
        smtp_port: SMTP server port.
        sender_email: The sender email address (also used as SMTP username).
        sender_password: The SMTP authentication password.
        use_tls: Whether to use STARTTLS for the connection.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        use_tls: bool = True,
    ) -> None:
        """Initialize the email service.

        Args:
            smtp_host: SMTP server hostname.
            smtp_port: SMTP server port number.
            sender_email: Sender address and SMTP username.
            sender_password: SMTP authentication password.
            use_tls: Enable STARTTLS for the connection.
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls

    async def send_email(self, to: str, subject: str, body_html: str) -> None:
        """Send an HTML email.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body_html: The HTML body content.
        """
        message = MIMEMultipart("alternative")
        message["From"] = self.sender_email
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body_html, "html"))

        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.sender_email,
                password=self.sender_password,
                start_tls=self.use_tls,
            )
        except Exception:
            logger.exception("Failed to send email to %s", to)

    async def send_verification_code(self, to: str, code: str) -> None:
        """Send a verification code email using a standard HTML template.

        Args:
            to: Recipient email address.
            code: The verification code to include in the email body.
        """
        html = f"""
        <html><body>
            <h2>Your verification code</h2>
            <p>Your code is: <strong>{code}</strong></p>
            <p>This code expires in 5 minutes.</p>
        </body></html>
        """
        await self.send_email(to, "Verification Code", html)