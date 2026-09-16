from enum import StrEnum

from pydantic import BaseModel, Field


class Topic(StrEnum):
    FEUP_MANAGEMENT_MEIC = "FEUP/Management/M.EIC"
    FEUP_MANAGEMENT_LEIC = "FEUP/Management/L.EIC"
    FEUP_MANAGEMENT_MECD = "FEUP/Management/MECD"
    FEUP_DEI = "FEUP/DEI"

    FEUP_TEACHING_LTW = "FEUP/Teaching/LTW"
    FEUP_TEACHING_LDTS = "FEUP/Teaching/LDTS"
    FEUP_TEACHING_FCED = "FEUP/Teaching/FCED"
    FEUP_TEACHING_OTHER = "FEUP/Teaching/Other"

    FEUP_DISSERTATIONS = "FEUP/Dissertations"
    FEUP_ADMIN = "FEUP/Admin"
    FEUP_GENERAL = "FEUP/General"

    RESEARCH_PAPERS = "Research/Papers"
    RESEARCH_PHD = "Research/PhD"
    RESEARCH_CONFERENCES = "Research/Conferences"
    RESEARCH_CITATIONS = "Research/Citations"
    RESEARCH_OTHER = "Research/Other"

    PROJECTS_JURISVIS = "Projects/JurisVis"
    PROJECTS_OTHER = "Projects/Other"

    NEWSLETTERS_ACM = "Newsletters/ACM"
    NEWSLETTERS_UPORTO = "Newsletters/U.Porto"
    NEWSLETTERS_OTHER = "Newsletters/Other"

    SERVICES_SECURITY = "Services/Security"
    SERVICES_ACCOUNTS = "Services/Accounts"

    LOW_PRIORITY_ACADEMIC_SOLICITATION = (
        "Low Priority/Academic Solicitation"
    )
    LOW_PRIORITY_COMMERCIAL = "Low Priority/Commercial"
    LOW_PRIORITY_SPAM = "Low Priority/Spam"

    OTHER = "Other"


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


class Classification(BaseModel):
    topic: Topic
    status: Status
    kind: Kind
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
