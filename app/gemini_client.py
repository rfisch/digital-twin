"""Gemini-powered sender research for email reply mode.

Uses Gemini 2.0 Flash with Google Search grounding to look up who's emailing
and their connection to Jacq's world. Degrades gracefully — if anything fails,
generation proceeds without research context.
"""

import os

from google import genai
from google.genai import types

# Personal domains where company research isn't useful
_PERSONAL_DOMAINS = frozenset({
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk",
    "hotmail.com", "outlook.com", "live.com", "msn.com",
    "icloud.com", "me.com", "mac.com", "aol.com",
    "protonmail.com", "proton.me", "fastmail.com",
    "hey.com", "zoho.com", "mail.com", "ymail.com",
})


class GeminiResearcher:
    """Research email senders via Gemini with Google Search grounding."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.0-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def research_sender(
        self,
        sender_name: str,
        sender_email: str,
        email_body: str,
    ) -> str:
        """Research sender via Gemini with Google Search grounding.

        Returns a bullet-point summary, or a bracketed error message
        if anything fails (so generation can proceed without research).
        """
        if not self.api_key:
            return "[Research unavailable: no GEMINI_API_KEY set]"

        try:
            return self._do_research(sender_name, sender_email, email_body)
        except Exception as e:
            return f"[Research unavailable: {e}]"

    def _do_research(
        self,
        sender_name: str,
        sender_email: str,
        email_body: str,
    ) -> str:
        client = self._get_client()

        # Build research prompt
        domain_hint = ""
        if sender_email and "@" in sender_email:
            domain = sender_email.split("@", 1)[1].lower()
            if domain not in _PERSONAL_DOMAINS:
                domain_hint = f"\nTheir email domain is {domain} — look up this company/organization."

        prompt = (
            f"Research this person who emailed Jacq Fisch (a writing coach, author, "
            f"and creative entrepreneur based in Scottsdale, AZ).\n\n"
            f"Sender name: {sender_name}\n"
            f"Sender email: {sender_email}\n"
            f"{domain_hint}\n"
            f"Their email said:\n---\n{email_body}\n---\n\n"
            f"Find and return:\n"
            f"- Who this person is (title, role, company)\n"
            f"- What their company/organization does\n"
            f"- Any connection to coaching, wellness, writing, or creative entrepreneurship\n"
            f"- Anything that would help Jacq write a personalized reply\n\n"
            f"Return ONLY bullet points. Be concise. If you can't find info, say so."
        )

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.3,
                max_output_tokens=512,
            ),
        )

        return response.text.strip()
