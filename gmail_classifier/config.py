import re
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, create_model

from .models import Kind, Status

TOPICS_FILE = Path("topics.yaml")


class TopicSpec(BaseModel):
    name: str
    rule: str | None = None


class Config(BaseModel):
    """Runtime configuration built from ``topics.yaml``."""

    model_config = {"arbitrary_types_allowed": True}

    topics: list[TopicSpec]
    guidance: str
    topic_enum: type[StrEnum]
    classification: type[BaseModel]


def _member_name(value: str) -> str:
    """Turn a topic value into a valid enum member name."""

    return re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_").upper()


def load_config(path: Path = TOPICS_FILE) -> Config:
    """Load the topic taxonomy and build the classification model from it."""

    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Copy topics.yaml.example to {path} "
            "and adapt it to your own categories."
        )

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    topics = [TopicSpec(**item) for item in data.get("topics", [])]

    if not topics:
        raise ValueError(f"{path} must define at least one topic.")

    names = [spec.name for spec in topics]

    if len(names) != len(set(names)):
        raise ValueError(f"{path} contains duplicate topic names.")

    topic_enum = StrEnum(
        "Topic",
        {_member_name(name): name for name in names},
    )

    classification = create_model(
        "Classification",
        topic=(topic_enum, ...),
        status=(Status, ...),
        kind=(Kind, ...),
        confidence=(float, Field(ge=0.0, le=1.0)),
    )

    return Config(
        topics=topics,
        guidance=(data.get("guidance") or "").strip(),
        topic_enum=topic_enum,
        classification=classification,
    )
