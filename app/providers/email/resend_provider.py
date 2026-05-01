import requests
from app.core.config import config_settings
from app.providers.email.base import EmailProvider


class ResendProvider(EmailProvider):
    def send_email(self, to, subject, body, content_type):
        try:
            if content_type == "html":
                payload = {"html": body}
            else:
                payload = {"text": body}

            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {config_settings.RESEND_API_KEY}"
                },
                json={
                    "from": config_settings.EMAIL_FROM,
                    "to": to,
                    "subject": subject,
                    **payload
                },
                timeout=5
            )
            if response.status_code >= 400:
                raise Exception(f"Resend error: {response.text}")

        except Exception as e:
            raise Exception(f"Error calling Resend server for Email delivery. Error: {e}")