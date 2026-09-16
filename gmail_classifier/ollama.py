import httpx

from .config import Config
from .models import Email, Kind, Status

OLLAMA_URL = "http://localhost:11434"
MODEL = "gemma3:12b"


def build_system_prompt(config: Config) -> str:
    """Build the classifier system prompt."""

    topics = "\n".join(
        f"- {spec.name}"
        for spec in config.topics
    )

    topic_rules = "\n".join(
        f"- {spec.name}: {spec.rule}"
        for spec in config.topics
        if spec.rule
    )

    statuses = "\n".join(
        f"- {status.value}"
        for status in Status
    )

    kinds = "\n".join(
        f"- {kind.value}"
        for kind in Kind
    )

    return f"""
    You classify email for a university professor.

    Choose exactly ONE primary TOPIC from this list:

    {topics}

    You MUST use a value exactly as written above.
    Never invent, abbreviate, modify, or combine topic names.

    Choose exactly one STATUS:

    {statuses}

    Choose exactly one KIND:

    {kinds}

    TOPIC RULES:

    {config.guidance}
    {topic_rules}

    STATUS RULES:

    Action:
    The recipient currently needs to reply, review, decide, send
    something, investigate something, or perform another action.

    Waiting:
    The recipient has already acted and is currently waiting for
    someone else or an external event.

    Reference:
    Potentially useful information that does not currently require
    action.

    None:
    Informational or low-value mail with little continuing value.

    KIND RULES:

    human:
    A message primarily written by a person to the recipient.

    institutional:
    An organizational or administrative communication.

    newsletter:
    A recurring or mass informational publication. Do not classify
    ordinary automated service notifications as newsletters.

    academic-solicitation:
    Unsolicited academic invitations, journals, conferences,
    editorial boards, etc.

    commercial:
    Marketing or sales communication.

    automated-important:
    Automated service messages such as security, account, system,
    submission or other important notifications.

    Return JSON only:

    {{
    "topic": "EXACTLY_ONE_TOPIC_FROM_THE_LIST",
    "status": "STATUS",
    "kind": "KIND",
    "confidence": 0.0
    }}

    confidence is your confidence that the COMPLETE classification
    is correct, from 0.0 to 1.0.
    """.strip()


def classify(email: Email, config: Config):
    """Classify a single email using Ollama."""

    content = f"""
FROM: {email.sender}
TO: {email.recipient}
SUBJECT: {email.subject}

{email.body[:6000]}
""".strip()

    response = httpx.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "stream": False,
            "format": config.classification.model_json_schema(),
            "options": {
                "temperature": 0,
            },
            "messages": [
                {
                    "role": "system",
                    "content": build_system_prompt(config),
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
        },
        timeout=120,
    )

    response.raise_for_status()

    raw_content = response.json()["message"]["content"]

    return config.classification.model_validate_json(raw_content)
