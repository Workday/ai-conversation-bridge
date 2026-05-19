"""OpenRouter chat-completions client for demo and experiment use."""

import logging
import time
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Demo/experiment chat provider via OpenRouter API."""

    def __init__(self, api_key, model, api_url, system_prompt=None, reasoning_effort=None):
        """Store OpenRouter credentials, model selection, and in-memory history settings."""
        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        self.base_system_prompt = system_prompt
        self.reasoning_effort = reasoning_effort

        self.chat_history = {}
        self.history_limit = 10

    def _get_user_history(self, user_id):
        """Return the in-memory chat history list for a user, creating it if needed."""
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []
        return self.chat_history[user_id]

    def _append_to_history(self, user_id, role, content):
        """Append a chat turn and trim history to the configured limit."""
        history = self._get_user_history(user_id)
        history.append({"role": role, "content": content})

        if len(history) > self.history_limit:
            self.chat_history[user_id] = history[-self.history_limit:]

    def _get_dynamic_system_prompt(self):
        """Build the system prompt, including today's date when configured."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_prompt = f"Today's date is {current_date}."

        if self.base_system_prompt:
            return f"{self.base_system_prompt}\n{date_prompt}"
        return date_prompt

    def get_completion(self, user_message, user_id=None):
        """Send a chat completion request to OpenRouter and return the assistant reply."""
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY not set.")
            return "I am currently unable to think (API Key missing)."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": self._get_dynamic_system_prompt()}]

        if user_id:
            self._append_to_history(user_id, "user", user_message)
            messages.extend(self._get_user_history(user_id))
        else:
            messages.append({"role": "user", "content": user_message})

        payload = {"model": self.model, "messages": messages}

        if self.reasoning_effort:
            payload["reasoning"] = {"effort": self.reasoning_effort}

        t0 = time.time()
        try:
            response = httpx.post(self.api_url, headers=headers, json=payload, timeout=120.0)
            elapsed = time.time() - t0
            response.raise_for_status()
            data = response.json()

            if 'choices' in data and len(data['choices']) > 0:
                ai_text = data['choices'][0]['message']['content']
                if ai_text:
                    ai_text = ai_text.strip()
                if user_id:
                    self._append_to_history(user_id, "assistant", ai_text)
                logger.info(f"OpenRouter responded in {elapsed:.1f}s")
                return ai_text
            else:
                logger.error(f"Unexpected OpenRouter response format: {data}")
                return "I'm not sure how to respond to that."

        except httpx.TimeoutException as e:
            elapsed = time.time() - t0
            logger.error(f"OpenRouter timeout after {elapsed:.1f}s: {e}")
            return (
                "Sorry, the AI service is taking longer than expected. "
                "Please try again in a moment."
            )
        except httpx.HTTPStatusError as e:
            elapsed = time.time() - t0
            status = e.response.status_code
            logger.error(f"OpenRouter HTTP {status} after {elapsed:.1f}s: {e}")
            if status == 429:
                return (
                    "The AI model is temporarily rate-limited. "
                    "Please wait a moment and try again."
                )
            return "Sorry, the AI service returned an error. Please try again later."
        except Exception as e:
            elapsed = time.time() - t0
            logger.error(f"OpenRouter call failed after {elapsed:.1f}s ({type(e).__name__}): {e}")
            return "Sorry, I encountered an error while processing your request."
