"""LinkedIn API client for posting content.

Follows the gmail_client.py pattern: lazy init, graceful degradation.
Requires a LinkedIn app with "Share on LinkedIn" product enabled.

Credentials: credentials/linkedin_credentials.json (client_id, client_secret)
Token: credentials/linkedin_token.json (access_token, expires_at)

Run scripts/linkedin_auth.py once to complete the OAuth2 flow.
"""

import json
import time
from pathlib import Path

import httpx


CREDENTIALS_DIR = Path(__file__).parent.parent / "credentials"
DEFAULT_CREDENTIALS = CREDENTIALS_DIR / "linkedin_credentials.json"
DEFAULT_TOKEN = CREDENTIALS_DIR / "linkedin_token.json"

API_VERSION = "202507"


class LinkedInClient:
    """Post content to LinkedIn via the REST API."""

    def __init__(
        self,
        credentials_path: Path | str | None = None,
        token_path: Path | str | None = None,
    ):
        self.credentials_path = (
            Path(credentials_path) if credentials_path else DEFAULT_CREDENTIALS
        )
        self.token_path = Path(token_path) if token_path else DEFAULT_TOKEN
        self._person_id: str | None = None

    def is_configured(self) -> bool:
        """Check if LinkedIn credentials and token exist."""
        return self.credentials_path.exists() and self.token_path.exists()

    def _load_token(self) -> str:
        """Load the access token, raising if expired or missing."""
        if not self.token_path.exists():
            raise RuntimeError(
                "LinkedIn token not found. Run: python scripts/linkedin_auth.py"
            )

        data = json.loads(self.token_path.read_text())
        expires_at = data.get("expires_at", 0)

        if time.time() > expires_at:
            raise RuntimeError(
                "LinkedIn token expired. Run: python scripts/linkedin_auth.py"
            )

        return data["access_token"]

    def _headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": API_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def get_profile_id(self) -> str:
        """Get the authenticated user's LinkedIn person ID from saved token."""
        if self._person_id:
            return self._person_id

        data = json.loads(self.token_path.read_text())
        person_id = data.get("person_id")
        if not person_id:
            raise RuntimeError(
                "LinkedIn person ID not found in token. "
                "Re-run: python scripts/linkedin_auth.py"
            )
        self._person_id = person_id
        return self._person_id

    def create_post(self, text: str) -> dict:
        """Post text content to LinkedIn personal profile.

        Returns {"success": bool, "message": str}.
        """
        try:
            token = self._load_token()
            person_id = self.get_profile_id()

            body = {
                "author": f"urn:li:person:{person_id}",
                "commentary": text,
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": [],
                },
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False,
            }

            resp = httpx.post(
                "https://api.linkedin.com/rest/posts",
                headers=self._headers(token),
                json=body,
                timeout=15.0,
            )

            if resp.status_code in (200, 201):
                return {"success": True, "message": "Posted to LinkedIn!"}

            return {
                "success": False,
                "message": f"LinkedIn API error ({resp.status_code}): {resp.text}",
            }

        except Exception as e:
            return {"success": False, "message": f"Failed to post: {e}"}
