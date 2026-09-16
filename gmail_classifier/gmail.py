import base64
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .models import Email


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]

TOKEN_FILE = Path("token.json")
CREDENTIALS_FILE = Path("credentials.json")


def get_service():
    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not credentials or not credentials.valid:
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )

            credentials = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(credentials.to_json())

    return build(
        "gmail",
        "v1",
        credentials=credentials,
    )


def decode(data: str | None) -> str:
    if not data:
        return ""

    data += "=" * (-len(data) % 4)

    return base64.urlsafe_b64decode(data).decode(
        "utf-8",
        errors="replace",
    )


def extract_text(payload: dict) -> str:
    if payload.get("mimeType") == "text/plain":
        return decode(
            payload.get("body", {}).get("data")
        )

    for part in payload.get("parts", []):
        text = extract_text(part)

        if text:
            return text

    return ""


def get_messages(
    limit: int = 10,
    query: str = "in:inbox",
):
    service = get_service()

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=query,
            maxResults=limit,
        )
        .execute()
    )

    for item in response.get("messages", []):
        raw = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=item["id"],
                format="full",
            )
            .execute()
        )

        headers = {
            header["name"].lower(): header["value"]
            for header in raw["payload"].get("headers", [])
        }

        yield Email(
            id=raw["id"],
            thread_id=raw["threadId"],
            sender=headers.get("from", ""),
            recipient=headers.get("to", ""),
            subject=headers.get("subject", ""),
            body=extract_text(raw["payload"]),
        )

def get_labels(service) -> dict[str, str]:
    """Return Gmail labels as {name: id}."""

    response = (
        service.users()
        .labels()
        .list(userId="me")
        .execute()
    )

    return {
        label["name"]: label["id"]
        for label in response.get("labels", [])
    }


def get_or_create_label(
    service,
    name: str,
) -> str:
    """Return a Gmail label ID, creating it if necessary."""

    labels = get_labels(service)

    if name in labels:
        return labels[name]

    label = (
        service.users()
        .labels()
        .create(
            userId="me",
            body={
                "name": name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        )
        .execute()
    )

    return label["id"]

def apply_label(
    service,
    message_id: str,
    label_id: str,
) -> None:
    """Add a label to a Gmail message."""

    (
        service.users()
        .messages()
        .modify(
            userId="me",
            id=message_id,
            body={
                "addLabelIds": [label_id],
            },
        )
        .execute()
    )
