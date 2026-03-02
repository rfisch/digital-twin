"""One-time OAuth2 flow for LinkedIn API access.

Usage:
    python scripts/linkedin_auth.py

Prerequisites:
    1. Create a LinkedIn app at https://developer.linkedin.com
    2. Add the "Share on LinkedIn" product (grants w_member_social)
    3. Set redirect URI to http://localhost:8888/callback
    4. Save credentials to credentials/linkedin_credentials.json:
       {"client_id": "...", "client_secret": "..."}
"""

import json
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx


CREDENTIALS_DIR = Path(__file__).parent.parent / "credentials"
CREDENTIALS_PATH = CREDENTIALS_DIR / "linkedin_credentials.json"
TOKEN_PATH = CREDENTIALS_DIR / "linkedin_token.json"

REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "openid w_member_social"

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler that captures the OAuth callback."""

    auth_code = None

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            CallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<h2>LinkedIn authorization successful!</h2>"
                b"<p>You can close this tab and return to the terminal.</p>"
            )
        else:
            error = params.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<h2>Authorization failed: {error}</h2>".encode())

    def log_message(self, format, *args):
        pass  # Suppress request logs


def main():
    if not CREDENTIALS_PATH.exists():
        print(f"Missing: {CREDENTIALS_PATH}")
        print()
        print("Create a LinkedIn app and save your credentials:")
        print('  {"client_id": "YOUR_ID", "client_secret": "YOUR_SECRET"}')
        return

    creds = json.loads(CREDENTIALS_PATH.read_text())
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]

    # Build authorization URL
    auth_params = (
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}"
    )
    full_url = AUTH_URL + auth_params

    print("Opening browser for LinkedIn authorization...")
    print(f"If the browser doesn't open, visit:\n{full_url}\n")
    webbrowser.open(full_url)

    # Start local server to catch the callback
    server = HTTPServer(("localhost", 8888), CallbackHandler)
    print("Waiting for callback on http://localhost:8888/callback ...")
    server.handle_request()  # Handle one request then stop

    if not CallbackHandler.auth_code:
        print("No authorization code received.")
        return

    # Exchange code for access token
    print("Exchanging code for access token...")
    resp = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": CallbackHandler.auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
        },
        timeout=15.0,
    )
    resp.raise_for_status()
    token_data = resp.json()

    access_token = token_data["access_token"]

    # Fetch person ID using the token
    print("Fetching LinkedIn profile ID...")
    profile_resp = httpx.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10.0,
    )
    person_id = None
    if profile_resp.status_code == 200:
        person_id = profile_resp.json().get("sub")
    if not person_id:
        # Try /v2/me as fallback
        profile_resp = httpx.get(
            "https://api.linkedin.com/v2/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
        if profile_resp.status_code == 200:
            person_id = profile_resp.json().get("id")
    if not person_id:
        print("\nCould not fetch profile ID automatically (needs OpenID Connect product).")
        print("To find your ID: go to LinkedIn > View Profile > look at the URL.")
        print("Or: View Page Source on your profile and search for 'urn:li:fsd_profile:'")
        person_id = input("\nEnter your LinkedIn member ID: ").strip()

    # Save token with expiration and person ID
    token = {
        "access_token": access_token,
        "expires_at": time.time() + token_data.get("expires_in", 5184000),
        "person_id": person_id,
    }

    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(token, indent=2))
    print(f"\nToken saved to {TOKEN_PATH}")
    print(f"Person ID: {person_id}")
    print("LinkedIn is ready to use!")


if __name__ == "__main__":
    main()
