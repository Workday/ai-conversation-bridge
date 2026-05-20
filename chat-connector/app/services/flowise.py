"""Flowise prediction API client for the primary AI backend."""

import logging
import time

import httpx

logger = logging.getLogger(__name__)


class FlowiseClient:
    """Primary chat provider via Flowise prediction API."""

    def __init__(self, api_url, api_key=None, timeout=120):
        """Store Flowise endpoint settings and request timeout."""
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    def get_completion(self, user_message, user_id=None):
        """Send a user message to Flowise and return the model response text."""
        if not self.api_url:
            logger.error("FLOWISE_API_URL not set.")
            return "I am currently unable to think (Configuration Error)."

        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"question": user_message}

        if user_id:
            payload["overrideConfig"] = {"sessionId": user_id}

        t0 = time.time()
        try:
            response = httpx.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
            elapsed = time.time() - t0
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict):
                text = data.get("text", data.get("answer", str(data)))
            else:
                text = str(data)

            if text and not isinstance(text, str):
                text = str(text)

            logger.info(f"Flowise responded in {elapsed:.1f}s")
            return text.strip() if text else text

        except httpx.TimeoutException as e:
            elapsed = time.time() - t0
            logger.error(f"Flowise timeout after {elapsed:.1f}s: {e}")
            return (
                "Sorry, the AI service is taking longer than expected. "
                "Please try again in a moment."
            )
        except httpx.HTTPStatusError as e:
            elapsed = time.time() - t0
            status = e.response.status_code
            logger.error(f"Flowise HTTP {status} after {elapsed:.1f}s: {e}")
            if status == 429:
                return (
                    "The AI service is temporarily rate-limited. "
                    "Please wait a moment and try again."
                )
            return "Sorry, the AI service returned an error. Please try again later."
        except Exception as e:
            elapsed = time.time() - t0
            logger.error(f"Flowise call failed after {elapsed:.1f}s ({type(e).__name__}): {e}")
            return "Sorry, I encountered an error while processing your request."
