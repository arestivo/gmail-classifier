from enum import StrEnum

from pydantic import BaseModel


class Status(StrEnum):
    ACTION = "Action"
    WAITING = "Waiting"
    REFERENCE = "Reference"
    NONE = "None"


class Kind(StrEnum):
    HUMAN = "human"
    INSTITUTIONAL = "institutional"
    NEWSLETTER = "newsletter"
    ACADEMIC_SOLICITATION = "academic-solicitation"
    COMMERCIAL = "commercial"
    AUTOMATED_IMPORTANT = "automated-important"


class Email(BaseModel):
    id: str
    thread_id: str
    sender: str
    recipient: str
    subject: str
    body: str
