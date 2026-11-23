"""Natural-Language Reminder Agent — parses unstructured reminder requests into structured output.

Supports intents: create_reminder, reschedule, snooze, cancel, clarify.
Uses dateparser for non-deterministic date/time extraction.
Outputs structured JSON conforming to the reminder schema.
"""

import json
import random
import re
from datetime import datetime, timedelta

import dateparser

SUPPORTED_INTENTS = ["create_reminder", "reschedule", "snooze", "cancel"]

SNOOZE_DURATIONS = {
    "5 minutes": timedelta(minutes=5),
    "10 minutes": timedelta(minutes=10),
    "15 minutes": timedelta(minutes=15),
    "30 minutes": timedelta(minutes=30),
    "1 hour": timedelta(hours=1),
    "2 hours": timedelta(hours=2),
}

CANCEL_PATTERNS = [
    r"\bcancel\b.*\breminder\b",
    r"\bdelete\b.*\breminder\b",
    r"\bremove\b.*\breminder\b",
    r"\bstop\b.*\bremind",
]

SNOOZE_PATTERNS = [
    r"\bsnooze\b",
    r"\blater\b",
    r"\bpostpone\b.*\b(?:a bit|little|while)\b",
    r"\bremind me (?:again )?later\b",
]

RESCHEDULE_PATTERNS = [
    r"\breschedule\b",
    r"\bmove\b.*\breminder\b",
    r"\bchange\b.*\b(?:time|date)\b",
    r"\bpush\b.*\bback\b",
    r"\bpostpone\b.*\bto\b",
]


def classify_intent(text: str) -> dict:
    """Classify the user's intent from natural language input.

    Returns a dict with 'intent' and 'confidence' keys.
    Non-deterministic: confidence scores include small random noise.
    """
    text_lower = text.lower().strip()

    scores = {
        "cancel": 0.0,
        "snooze": 0.0,
        "reschedule": 0.0,
        "create_reminder": 0.0,
    }

    for pattern in CANCEL_PATTERNS:
        if re.search(pattern, text_lower):
            scores["cancel"] += 0.4

    for pattern in SNOOZE_PATTERNS:
        if re.search(pattern, text_lower):
            scores["snooze"] += 0.4

    for pattern in RESCHEDULE_PATTERNS:
        if re.search(pattern, text_lower):
            scores["reschedule"] += 0.35

    if re.search(r"\bremind\s+me\b", text_lower):
        scores["create_reminder"] += 0.3
    if re.search(r"\bset\s+(?:a\s+)?reminder\b", text_lower):
        scores["create_reminder"] += 0.35
    if re.search(r"\bdon'?t\s+(?:let\s+me\s+)?forget\b", text_lower):
        scores["create_reminder"] += 0.3

    noise = random.uniform(-0.05, 0.05)  # noqa: S311 — not crypto; deliberate non-determinism
    for intent in scores:
        scores[intent] += noise
        scores[intent] = max(0.0, min(1.0, scores[intent]))

    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    if best_score < 0.15:
        return {"intent": "create_reminder", "confidence": round(0.3 + noise, 3)}

    return {"intent": best_intent, "confidence": round(best_score, 3)}


def extract_datetime(text: str) -> dict | None:
    """Extract date/time from natural language using dateparser.

    Non-deterministic: dateparser's interpretation can vary with locale,
    reference time, and ambiguous inputs.
    """
    settings = {
        "PREFER_DATES_FROM": "future",
        "RELATIVE_BASE": datetime.now(),
        "RETURN_AS_TIMEZONE_AWARE": False,
    }

    parsed = dateparser.parse(text, settings=settings)
    if parsed is None:
        time_patterns = [
            r"(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?)",
            r"(at\s+\d{1,2}\s*(?:am|pm|AM|PM))",
            r"(tomorrow|tonight|this evening|next week|next month)",
            r"(in\s+\d+\s+(?:minute|hour|day|week)s?)",
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed = dateparser.parse(match.group(1), settings=settings)
                if parsed:
                    break

    if parsed is None:
        return None

    return {
        "datetime": parsed.isoformat(),
        "is_date_only": parsed.hour == 0 and parsed.minute == 0 and parsed.second == 0,
    }


def extract_description(text: str) -> str:
    """Extract the reminder description by stripping time/intent phrases."""
    cleaned = text

    removal_patterns = [
        r"\bremind\s+me\s+(?:to\s+)?",
        r"\bset\s+(?:a\s+)?reminder\s+(?:to\s+)?",
        r"\bdon'?t\s+(?:let\s+me\s+)?forget\s+(?:to\s+)?",
        r"\b(?:at|on|by|before|after)\s+\d{1,2}[:/]\d{2}\s*(?:am|pm)?\b",
        r"\b(?:at|on|by|before|after)\s+\d{1,2}\s*(?:am|pm)\b",
        r"\btomorrow\b",
        r"\btonight\b",
        r"\btoday\b",
        r"\bnext\s+(?:week|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        r"\bin\s+\d+\s+(?:minute|hour|day|week)s?\b",
        r"\bthis\s+(?:evening|morning|afternoon)\b",
    ]

    for pattern in removal_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.strip(".,;:!? ")

    return cleaned


def extract_snooze_duration(text: str) -> str | None:
    """Extract snooze duration from text."""
    text_lower = text.lower()

    duration_patterns = [
        (r"\b(\d+)\s*min(?:ute)?s?\b", "minutes"),
        (r"\b(\d+)\s*hours?\b", "hours"),
        (r"\bhalf\s+(?:an\s+)?hour\b", None),
    ]

    for pattern, unit in duration_patterns:
        match = re.search(pattern, text_lower)
        if match:
            if unit is None:
                return "30 minutes"
            amount = int(match.group(1))
            return f"{amount} {unit}"

    return "15 minutes"


def parse_reminder(text: str) -> dict:
    """Parse a natural-language reminder request into structured output.

    Returns a dict conforming to the reminder output schema.
    Non-deterministic behavior sources:
      - Intent confidence scores include random noise
      - dateparser results can vary across runs for ambiguous inputs
    """
    if not text or not text.strip():
        return {
            "status": "error",
            "intent": None,
            "confidence": 0.0,
            "description": None,
            "datetime": None,
            "error": "Empty input provided",
        }

    text = text.strip()

    intent_result = classify_intent(text)
    intent = intent_result["intent"]
    confidence = intent_result["confidence"]

    if intent == "cancel":
        description = extract_description(text)
        return {
            "status": "success",
            "intent": "cancel",
            "confidence": confidence,
            "description": description if description else None,
            "datetime": None,
            "error": None,
        }

    if intent == "snooze":
        duration = extract_snooze_duration(text)
        return {
            "status": "success",
            "intent": "snooze",
            "confidence": confidence,
            "description": None,
            "datetime": None,
            "snooze_duration": duration,
            "error": None,
        }

    dt_result = extract_datetime(text)
    description = extract_description(text)

    if intent == "create_reminder":
        if not description:
            return {
                "status": "clarify",
                "intent": "create_reminder",
                "confidence": confidence,
                "description": None,
                "datetime": dt_result["datetime"] if dt_result else None,
                "error": None,
                "clarification_needed": "What would you like to be reminded about?",
            }

        if dt_result is None:
            return {
                "status": "clarify",
                "intent": "create_reminder",
                "confidence": confidence,
                "description": description,
                "datetime": None,
                "error": None,
                "clarification_needed": "When would you like to be reminded?",
            }

        return {
            "status": "success",
            "intent": "create_reminder",
            "confidence": confidence,
            "description": description,
            "datetime": dt_result["datetime"],
            "is_date_only": dt_result.get("is_date_only", False),
            "error": None,
        }

    if intent == "reschedule":
        dt_result = extract_datetime(text)
        if dt_result is None:
            return {
                "status": "clarify",
                "intent": "reschedule",
                "confidence": confidence,
                "description": extract_description(text) or None,
                "datetime": None,
                "error": None,
                "clarification_needed": "When would you like to reschedule to?",
            }

        return {
            "status": "success",
            "intent": "reschedule",
            "confidence": confidence,
            "description": extract_description(text) or None,
            "datetime": dt_result["datetime"],
            "error": None,
        }

    return {
        "status": "error",
        "intent": intent,
        "confidence": confidence,
        "description": None,
        "datetime": None,
        "error": f"Unhandled intent: {intent}",
    }


def process_batch(inputs: list[str]) -> list[dict]:
    """Process multiple reminder inputs and return structured results."""
    return [parse_reminder(text) for text in inputs]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = parse_reminder(text)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python reminder_agent.py <reminder text>")
        sys.exit(1)
