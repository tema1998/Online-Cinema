import logging
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from aiosmtplib import send, SMTPException
from jinja2 import Environment, FileSystemLoader

from consumer_messages.config.settings import settings

env = Environment(loader=FileSystemLoader("templates"))


def get_template(message_type, message_transfer):
    try:
        # TODO path
        template_path = f"{message_transfer}/{message_type}.html"
        template = env.get_template(template_path)
        return template
    except Exception as e:
        logging.error(f"Template for {message_transfer}/{message_type} not found: {str(e)}")
        raise


def render_template(template, data):
    return template.render(data)


async def send_email(recipient: str, rendered_content: str, subject: Optional[str] = "Notification"):
    """
    Asynchronously sends an email to the recipient.

    :param recipient: The email address of the recipient.
    :param rendered_content: The HTML content rendered by Jinja.
    :param subject: The subject of the email.
    """

    # Setup the MIME message
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg["Reply-To"] = settings.smtp_email  # Set a Reply-To address

    # Add plain text version of the message
    plain_text_content = "Please confirm your email address by clicking the link provided."
    msg.attach(MIMEText(plain_text_content, "plain"))

    # Attach the rendered HTML content
    html_part = MIMEText(rendered_content, "html")
    msg.attach(html_part)

    # Create an SSL context for secure connection
    tls_context = ssl.create_default_context()

    # Send the email asynchronously with Yandex SMTP server
    try:
        await send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_email,
            password=settings.smtp_pass,
            tls_context=tls_context,
            use_tls=True  # Use SSL/TLS directly on port 465
        )
        logging.info(f"Email sent to {recipient}")
    except SMTPException as e:
        logging.error(f"Failed to send email to {recipient}: {e}")
