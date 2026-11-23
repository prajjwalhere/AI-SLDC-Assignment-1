"""Offline tests for the LLM-backed reminder agent (no network, no API key).

Derived from specification Amendment 1 (FR-B8 failure classes, GR-1) and the plan's retry policy.
The HTTP transport, the sleep function and the key lookup are replaced by fakes.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import reminder_agent_llm as agent

FAKE_CREDENTIAL = "FAKE-CREDENTIAL-FOR-OFFLINE-TESTS"

VALID_OUTPUT = {
    "status": "success",
    "intent": "cancel",
    "confidence": 0.9,
    "description": "dentist appointment",
    "datetime": None,
    "error": None,
}


def chat(content):
    """Build a chat-completions response body around the given message content."""
    return json.dumps({"choices": [{"message": {"content": content}}]})


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, payload, api_key):
        self.calls.append((payload, api_key))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def setup(monkeypatch):
    sleeps = []
    monkeypatch.setattr(agent, "_sleep", lambda seconds: sleeps.append(seconds))
    monkeypatch.setattr(agent, "_get_api_key", lambda: FAKE_CREDENTIAL)

    def install(responses):
        transport = FakeTransport(responses)
        monkeypatch.setattr(agent, "_post", transport)
        return transport

    install.sleeps = sleeps
    return install


class TestInputGuard:
    @pytest.mark.parametrize("text", ["", "   ", "\n\t"])
    def test_empty_input_returns_error_without_api_call(self, setup, text):
        transport = setup([])
        out = agent.parse_reminder(text)
        assert out["status"] == "error"
        assert out["intent"] is None
        assert out["error"]
        assert transport.calls == []


class TestSuccessPath:
    def test_valid_model_output_is_returned(self, setup):
        transport = setup([(200, chat(json.dumps(VALID_OUTPUT)), {})])
        out = agent.parse_reminder("Cancel my reminder about the dentist appointment")
        assert out == VALID_OUTPUT
        assert len(transport.calls) == 1

    def test_request_shape(self, setup):
        transport = setup([(200, chat(json.dumps(VALID_OUTPUT)), {})])
        agent.parse_reminder("Cancel my reminder about the dentist appointment")
        payload, key = transport.calls[0]
        assert key == FAKE_CREDENTIAL
        assert payload["model"] == agent.MODEL
        assert payload["temperature"] == 0
        assert payload["response_format"] == {"type": "json_object"}
        assert payload["messages"][-1] == {
            "role": "user",
            "content": "Cancel my reminder about the dentist appointment",
        }
        assert "{{NOW}}" not in payload["messages"][0]["content"]


class TestRetryPolicy:
    def test_rate_limit_then_success_is_retried(self, setup):
        transport = setup([(429, "{}", {}), (200, chat(json.dumps(VALID_OUTPUT)), {})])
        out = agent.parse_reminder("Cancel my reminder about the dentist appointment")
        assert out["intent"] == "cancel"
        assert len(transport.calls) == 2
        assert len(setup.sleeps) == 1

    def test_repeated_unavailable_raises_service_error(self, setup):
        transport = setup([(503, "{}", {})] * 3)
        with pytest.raises(agent.ServiceError) as info:
            agent.parse_reminder("Remind me to call mom tomorrow at 5pm")
        assert info.value.code == "SERVICE_UNAVAILABLE"
        assert info.value.is_service_error is True
        assert len(transport.calls) == agent.MAX_ATTEMPTS == 3

    def test_repeated_rate_limit_raises_service_error(self, setup):
        setup([(429, "{}", {})] * 3)
        with pytest.raises(agent.ServiceError) as info:
            agent.parse_reminder("Remind me to call mom tomorrow at 5pm")
        assert info.value.code == "SERVICE_RATE_LIMIT"

    def test_timeout_is_retried_then_raises(self, setup):
        transport = setup([TimeoutError("timed out")] * 3)
        with pytest.raises(agent.ServiceError) as info:
            agent.parse_reminder("Remind me to call mom tomorrow at 5pm")
        assert info.value.code == "SERVICE_TIMEOUT"
        assert len(transport.calls) == 3

    def test_network_error_raises_service_error(self, setup):
        setup([OSError("connection refused")] * 3)
        with pytest.raises(agent.ServiceError) as info:
            agent.parse_reminder("Remind me to call mom tomorrow at 5pm")
        assert info.value.code == "SERVICE_NETWORK"

    def test_auth_error_is_not_retried(self, setup):
        transport = setup([(401, "{}", {})])
        with pytest.raises(agent.ServiceError) as info:
            agent.parse_reminder("Remind me to call mom tomorrow at 5pm")
        assert info.value.code == "SERVICE_AUTH"
        assert len(transport.calls) == 1


class TestBadModelOutput:
    def test_invalid_json_is_not_retried(self, setup):
        transport = setup([(200, chat("this is not json"), {})])
        out = agent.parse_reminder("Snooze for 30 minutes")
        assert out["status"] == "error"
        assert out["error"].startswith("MODEL_OUTPUT_INVALID")
        assert len(transport.calls) == 1

    def test_missing_contract_fields_are_rejected(self, setup):
        setup([(200, chat(json.dumps({"status": "success", "intent": "snooze"})), {})])
        out = agent.parse_reminder("Snooze for 30 minutes")
        assert out["status"] == "error"
        assert out["error"].startswith("MODEL_OUTPUT_INVALID")

    def test_non_object_json_is_rejected(self, setup):
        setup([(200, chat(json.dumps(["not", "an", "object"])), {})])
        out = agent.parse_reminder("Snooze for 30 minutes")
        assert out["error"].startswith("MODEL_OUTPUT_INVALID")


class TestKeyHandling:
    def test_missing_key_raises_service_config_without_api_call(self, monkeypatch):
        monkeypatch.setattr(agent, "_get_api_key", lambda: None)
        calls = []
        monkeypatch.setattr(agent, "_post", lambda payload, api_key: calls.append(1))
        with pytest.raises(agent.ServiceError) as info:
            agent.parse_reminder("Snooze for 30 minutes")
        assert info.value.code == "SERVICE_CONFIG"
        assert calls == []

    def test_key_never_appears_in_error_text(self, setup):
        setup([(401, "bad key " + FAKE_CREDENTIAL, {})])
        with pytest.raises(agent.ServiceError) as info:
            agent.parse_reminder("Snooze for 30 minutes")
        assert FAKE_CREDENTIAL not in str(info.value)
