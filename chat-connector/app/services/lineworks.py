"""LINE WORKS bot API client for webhook verification and outbound messages."""

import base64
import hashlib
import hmac
import logging
from datetime import datetime

import httpx
import jwt

logger = logging.getLogger(__name__)


class LineWorksClient:
    """Client for LINE WORKS OAuth, webhook verification, and bot messaging."""

    def __init__(self, config):
        """Initialize credentials and normalize PEM private key formatting."""
        self.client_id = config.LW_CLIENT_ID
        self.client_secret = config.LW_CLIENT_SECRET
        self.service_account_id = config.LW_SERVICE_ACCOUNT_ID
        self.private_key = config.LW_PRIVATE_KEY
        self.bot_id = config.LW_BOT_ID
        self.bot_secret = config.LW_BOT_SECRET
        self.base_api_url = config.BASE_API_URL
        self.base_auth_url = config.BASE_AUTH_URL

        self.token_cache = {
            'access_token': None,
            'expires_at': 0
        }

        # PEM private keys require newlines around the header/footer markers,
        # but environment variables in container platforms (Cloud Run, etc.) often
        # mangle them. Handle two common cases:

        # Case 1: Env var contains literal "\n" strings (e.g. from CLI --set-env-vars)
        if self.private_key and '\\n' in self.private_key:
            self.private_key = self.private_key.replace('\\n', '\n')

        # Case 2: Newlines were converted to spaces (e.g. pasted in Cloud Run console).
        # Reconstruct valid PEM by extracting the base64 body between markers.
        if self.private_key and '\n' not in self.private_key:
            pk = self.private_key.strip()
            for begin_marker in ('-----BEGIN PRIVATE KEY-----', '-----BEGIN RSA PRIVATE KEY-----'):
                end_marker = begin_marker.replace('BEGIN', 'END')
                if pk.startswith(begin_marker) and pk.endswith(end_marker):
                    body = pk[len(begin_marker):-len(end_marker)].replace(' ', '')
                    self.private_key = f"{begin_marker}\n{body}\n{end_marker}"
                    break

    def validate_config(self):
        """Return True when required LINE WORKS credentials are present."""
        return all([
            self.client_id,
            self.client_secret,
            self.service_account_id,
            self.private_key,
            self.bot_id
        ])

    def verify_signature(self, request_body: bytes, signature: str) -> bool:
        """Verify LINE WORKS webhook signature (HMAC-SHA256 with Bot Secret).

        Returns True if verification passes or if bot_secret is not configured
        (to preserve backward compatibility for development setups).
        """
        if not self.bot_secret:
            logger.warning(
                "LW_API_20_BOT_SECRET not set — skipping webhook signature verification. "
                "This is insecure; set the Bot Secret for production deployments."
            )
            return True

        expected = hmac.new(
            self.bot_secret.encode("utf-8"),
            request_body,
            hashlib.sha256
        ).digest()
        expected_b64 = base64.b64encode(expected).decode("utf-8")

        return hmac.compare_digest(expected_b64, signature)

    def _get_jwt(self):
        """Build a signed JWT for LINE WORKS OAuth token exchange."""
        current_time = datetime.now().timestamp()
        return jwt.encode(
            {
                "iss": self.client_id,
                "sub": self.service_account_id,
                "iat": current_time,
                "exp": current_time + 3600
            },
            self.private_key,
            algorithm="RS256"
        )

    def get_access_token(self, scope="bot"):
        """Return a cached LINE WORKS access token, refreshing it when expired."""
        current_time = datetime.now().timestamp()

        # 5-minute buffer before expiry
        if self.token_cache['access_token'] and current_time < (self.token_cache['expires_at'] - 300):
            return self.token_cache['access_token']

        logger.info("Requesting new LINE WORKS access token...")

        jws = self._get_jwt()
        url = f'{self.base_auth_url}/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        params = {
            "assertion": jws,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": scope,
        }

        r = httpx.post(url=url, data=params, headers=headers, timeout=30.0)
        r.raise_for_status()
        body = r.json()

        self.token_cache['access_token'] = body.get("access_token")
        self.token_cache['expires_at'] = current_time + int(body.get("expires_in", 3600))

        return self.token_cache['access_token']

    def send_message(self, user_id, content):
        """Send a bot message payload to a LINE WORKS user."""
        access_token = self.get_access_token()

        url = f"{self.base_api_url}/bots/{self.bot_id}/users/{user_id}/messages"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {access_token}"
        }

        r = httpx.post(url=url, json=content, headers=headers, timeout=30.0)
        r.raise_for_status()
