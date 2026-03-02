"""Gmail API OAuth2 client for sending emails.

Follows the gemini_client.py pattern: lazy init, graceful degradation.
Requires a Google Cloud project with Gmail API enabled and OAuth2
credentials downloaded to credentials/gmail_credentials.json.

First run triggers a browser-based OAuth flow. Token is cached at
credentials/gmail_token.json for subsequent use.
"""

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


CREDENTIALS_DIR = Path(__file__).parent.parent / "credentials"
DEFAULT_CREDENTIALS = CREDENTIALS_DIR / "gmail_credentials.json"
DEFAULT_TOKEN = CREDENTIALS_DIR / "gmail_token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class GmailClient:
    """Send emails via Gmail API with OAuth2."""

    def __init__(
        self,
        credentials_path: Path | str | None = None,
        token_path: Path | str | None = None,
    ):
        self.credentials_path = Path(credentials_path) if credentials_path else DEFAULT_CREDENTIALS
        self.token_path = Path(token_path) if token_path else DEFAULT_TOKEN
        self._service = None

    def is_configured(self) -> bool:
        """Check if OAuth credentials file exists (UI uses this to show/hide Send button)."""
        return self.credentials_path.exists()

    def _get_service(self):
        """Lazy-init Gmail API service. Runs browser OAuth flow on first use."""
        if self._service is not None:
            return self._service

        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None

        # Load saved token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # Refresh or run new OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for next time
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(creds.to_json())

        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def send_email(self, to: str, subject: str, html_body: str) -> dict:
        """Send an HTML email via Gmail.

        Returns {"success": bool, "message": str, "message_id": str|None}.
        """
        try:
            service = self._get_service()

            msg = MIMEMultipart()
            msg["to"] = to
            msg["subject"] = subject
            msg.attach(MIMEText(html_body, "html"))

            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            result = service.users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()

            return {
                "success": True,
                "message": "Email sent!",
                "message_id": result.get("id"),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send: {e}",
                "message_id": None,
            }
