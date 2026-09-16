import json
from pathlib import Path

import httpx
import yaml

from .models import (
    Classification,
    Email,
    Kind,
    Status,
    Topic,
)

OLLAMA_URL = "http://localhost:11434"
MODEL = "gemma3:12b"

def build_system_prompt() -> str:
    """Build the classifier system prompt."""

    topics = "\n".join(
        f"- {topic.value}"
        for topic in Topic
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

    - Choose the single most specific topic that describes why this
    email matters to the recipient.
    - Do NOT add a general parent or related category.
    - FEUP/General means general FEUP institutional communication.
    Do not use it merely because the recipient works at FEUP.
    - FEUP/Management/M.EIC is for management and scientific
    committee work concerning M.EIC. An email about supervising an
    M.EIC dissertation belongs to FEUP/Dissertations, not M.EIC.
    - FEUP/Management/L.EIC is for management work concerning L.EIC.
    - FEUP/Dissertations is for dissertation supervision, students,
    meetings, reviews, defenses and related dissertation work.
    - FEUP/Teaching/* is for teaching a specific course.
    - Newsletters/* is for newsletters and mass informational mail.
    - Services/Security is for security alerts and warnings.
    - Services/Accounts is for account configuration and service
    account information that is not primarily a security warning.
    - Research/Papers is for papers, reviews, submissions and
    publication-related correspondence.
    - Research/Conferences is for conference organization,
    attendance, registration and calls relating to legitimate
    conferences.
    - Research/Other is the fallback for research correspondence
    that does not fit another Research category.
    - Low Priority/Academic Solicitation is for unsolicited journal,
    conference, editorial-board and similar academic solicitations.
    - Low Priority/Commercial is for marketing and sales messages.
    - Other is the final fallback.

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
    "topics": ["EXACTLY_ONE_TOPIC_FROM_THE_LIST"],
    "status": "STATUS",
    "kind": "KIND",
    "confidence": 0.0
    }}

    confidence is your confidence that the COMPLETE classification
    is correct, from 0.0 to 1.0.
    """.strip()


def classify(email: Email) -> Classification:
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
            "format": Classification.model_json_schema(),
            "options": {
                "temperature": 0,
            },
            "messages": [
                {
                    "role": "system",
                    "content": build_system_prompt(),
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

    return Classification.model_validate_json(raw_content)
