"""LLM-backed Natural-Language Reminder Agent (specification Amendment 1).

Produces the same output contract as reminder_agent.py by calling a hosted LLM (Groq, OpenAI-compatible
chat completions). Uses the standard library only. The API key is read from the environment or from the
git-ignored Part-1B/.env file and is never logged or written anywhere.

Failure classes (FR-B8):
  - service failure   -> raises ServiceError (timeout, rate limit, unavailable, auth, network, config)
  - bad model output  -> returns status "error" with an error text starting "MODEL_OUTPUT_INVALID"
  - bad input (empty) -> returns status "error" without any API call (GR-1, INV-6)
"""

import http.client
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

PART_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = PART_DIR / "prompts" / "system_prompt_llm.md"
ENV_PATH = PART_DIR / ".env"

API_HOST = "api.groq.com"
API_PATH = "/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 0
REASONING_EFFORT = "low"
MAX_COMPLETION_TOKENS = 1024
TIMEOUT_SECONDS = 45
MAX_ATTEMPTS = 3
RETRY_WAITS = (2.0, 5.0)
MAX_RETRY_AFTER = 30.0

REQUIRED_FIELDS = ("status", "intent", "confidence", "description", "datetime", "error")

AGENT_INFO = {
    "module": "reminder_agent_llm",
    "provider": "groq",
    "model": MODEL,
    "temperature": TEMPERATURE,
    "reasoning_effort": REASONING_EFFORT,
    "response_format": "json_object",
    "timeout_seconds": TIMEOUT_SECONDS,
    "max_request_attempts": MAX_ATTEMPTS,
}


class ServiceError(Exception):
    """The provider or the connection failed; this is not a verdict on the application."""

    is_service_error = True

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


def _get_api_key() -> str | None:
    for name in ("GROQ_API_KEY", "GROQ-KEY"):
        value = os.environ.get(name)
        if value:
            return value.strip()
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() in ("GROQ_API_KEY", "GROQ-KEY") and value.strip():
                return value.strip().strip('"').strip("'")
    return None


def _post(payload: dict, api_key: str) -> tuple[int, str, dict]:
    """Send one chat-completions request. Returns (status, body text, lower-cased headers)."""
    connection = http.client.HTTPSConnection(API_HOST, timeout=TIMEOUT_SECONDS)
    try:
        connection.request(
            "POST",
            API_PATH,
            json.dumps(payload),
            {
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json",
                "User-Agent": "reminder-agent-eval/1.0",
            },
        )
        response = connection.getresponse()
        text = response.read().decode("utf-8", errors="replace")
        headers = {name.lower(): value for name, value in response.getheaders()}
        return response.status, text, headers
    finally:
        connection.close()


def _mask(text: str, api_key: str) -> str:
    return text.replace(api_key, "***") if api_key else text


def _error_response(message: str, intent: str | None = None) -> dict:
    return {
        "status": "error",
        "intent": intent,
        "confidence": 0.0,
        "description": None,
        "datetime": None,
        "error": message,
    }


def _system_prompt() -> str:
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S (%A)")
    return PROMPT_PATH.read_text(encoding="utf-8").replace("{{NOW}}", now)


def _retry_wait(attempt: int, headers: dict) -> float:
    try:
        advised = float(headers.get("retry-after", ""))
        if 0 <= advised <= MAX_RETRY_AFTER:
            return advised
    except ValueError:
        pass
    return RETRY_WAITS[min(attempt - 1, len(RETRY_WAITS) - 1)]


def _request_with_retries(payload: dict, api_key: str) -> str:
    """Return the response body of a successful call, or raise ServiceError after bounded retries."""
    last_code, last_message = "SERVICE_UNAVAILABLE", "no attempt made"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        headers: dict = {}
        try:
            status, text, headers = _post(payload, api_key)
        except TimeoutError:
            last_code, last_message = "SERVICE_TIMEOUT", "request timed out"
        except OSError as exc:
            last_code, last_message = "SERVICE_NETWORK", _mask(f"network error: {exc}", api_key)
        else:
            if status == 200:
                return text
            detail = _mask(text[:200], api_key)
            if status == 429:
                last_code, last_message = "SERVICE_RATE_LIMIT", f"HTTP 429: {detail}"
            elif status >= 500:
                last_code, last_message = "SERVICE_UNAVAILABLE", f"HTTP {status}: {detail}"
            elif status in (401, 403):
                raise ServiceError("SERVICE_AUTH", f"HTTP {status}: {detail}")
            else:
                raise ServiceError("SERVICE_CONFIG", f"HTTP {status}: {detail}")
        if attempt < MAX_ATTEMPTS:
            _sleep(_retry_wait(attempt, headers))
    raise ServiceError(last_code, f"{last_message} (after {MAX_ATTEMPTS} attempts)")


def _extract_output(body_text: str) -> dict:
    """Parse the provider response into the contract object, or raise ValueError (bad model output)."""
    try:
        content = json.loads(body_text)["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ValueError(f"unexpected response structure: {exc}") from exc
    try:
        output = json.loads(content)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"content is not valid JSON: {exc}") from exc
    if not isinstance(output, dict):
        raise ValueError("content is not a JSON object")
    missing = [name for name in REQUIRED_FIELDS if name not in output]
    if missing:
        raise ValueError("missing contract fields: " + ", ".join(missing))
    return output


def parse_reminder(text: str) -> dict:
    """Parse a natural-language reminder request into the structured output contract."""
    if not text or not text.strip():
        return _error_response("Empty input provided")

    api_key = _get_api_key()
    if not api_key:
        raise ServiceError("SERVICE_CONFIG", "no API key configured (set GROQ_API_KEY or GROQ-KEY in Part-1B/.env)")

    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "reasoning_effort": REASONING_EFFORT,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": text.strip()},
        ],
    }
    body_text = _request_with_retries(payload, api_key)
    try:
        return _extract_output(body_text)
    except ValueError as exc:
        return _error_response(_mask(f"MODEL_OUTPUT_INVALID: {exc}", api_key))


def process_batch(inputs: list[str]) -> list[dict]:
    """Process multiple reminder inputs and return structured results."""
    return [parse_reminder(text) for text in inputs]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            print(json.dumps(parse_reminder(" ".join(sys.argv[1:])), indent=2))
        except ServiceError as exc:
            print(f"{exc.code}: {exc}", file=sys.stderr)
            sys.exit(2)
    else:
        print("Usage: python reminder_agent_llm.py <reminder text>")
        sys.exit(1)
