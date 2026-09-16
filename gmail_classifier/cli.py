import typer
import csv

from .gmail import (
    apply_label,
    get_messages,
    get_or_create_label,
    get_service,
)
from .ollama import classify
from .config import load_config


app = typer.Typer()


@app.command()
def test_ollama():
    """Test the connection to Ollama."""

    from .models import Email

    email = Email(
        id="test",
        thread_id="test",
        sender="student@fe.up.pt",
        recipient="professor@fe.up.pt",
        subject="Dúvida sobre LTW",
        body=(
            "Bom dia Professor, tenho uma dúvida relativamente "
            "ao projeto de LTW. Pode ajudar-me?"
        ),
    )

    result = classify(email, load_config())

    typer.echo(result.model_dump_json(indent=2))


@app.command()
def test_gmail(limit: int = 5):
    """Read recent Gmail messages."""

    for email in get_messages(limit=limit):
        typer.echo("=" * 70)
        typer.echo(f"From:    {email.sender}")
        typer.echo(f"Subject: {email.subject}")
        typer.echo(email.body[:300])


@app.command()
def classify_recent(
    limit: int = 5,
    query: str = "in:inbox -label:AI/Classified",
):
    """Classify Gmail messages without modifying Gmail."""

    config = load_config()

    for email in get_messages(
        limit=limit,
        query=query,
    ):
        typer.echo("=" * 70)
        typer.echo(f"From:    {email.sender}")
        typer.echo(f"Subject: {email.subject}")

        try:
            result = classify(email, config)
            typer.echo(result.model_dump_json(indent=2))

        except Exception as exc:
            typer.secho(
                f"CLASSIFICATION ERROR: {exc}",
                fg=typer.colors.RED,
            )

@app.command()
def evaluate(
    limit: int = 200,
    query: str = "newer_than:180d -label:AI/Classified",
    output: str = "evaluation.csv",
):
    """Classify historical messages and save results for review."""

    config = load_config()

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "from",
                "subject",
                "topic",
                "status",
                "kind",
                "confidence",
            ],
        )
        writer.writeheader()

        for i, email in enumerate(
            get_messages(limit=limit, query=query),
            start=1,
        ):
            typer.echo(
                f"[{i}/{limit}] {email.subject[:70]}"
            )

            try:
                result = classify(email, config)

                writer.writerow({
                    "id": email.id,
                    "from": email.sender,
                    "subject": email.subject,
                    "topic": result.topic.value,
                    "status": result.status.value,
                    "kind": result.kind.value,
                    "confidence": result.confidence,
                })

                f.flush()

            except Exception as exc:
                typer.secho(
                    f"  ERROR: {exc}",
                    fg=typer.colors.RED,
                )

@app.command()
def show(
    topic: str,
    input: str = "evaluation.csv",
):
    """Show messages classified under a topic."""

    with open(input, encoding="utf-8") as f:
        rows = csv.DictReader(f)

        count = 0

        for row in rows:
            if row["topic"] == topic:
                count += 1

                typer.echo("=" * 70)
                typer.echo(f'From:    {row["from"]}')
                typer.echo(f'Subject: {row["subject"]}')
                typer.echo(
                    f'Status:  {row["status"]} | '
                    f'Kind: {row["kind"]} | '
                    f'Confidence: {row["confidence"]}'
                )

        typer.echo(f"\nTotal: {count}")


@app.command()
def create_labels():
    """Create Gmail labels for all classification topics."""

    service = get_service()

    for topic in load_config().topic_enum:
        label_id = get_or_create_label(
            service,
            topic.value,
        )

        typer.echo(
            f"{topic.value}: {label_id}"
        )

    get_or_create_label(
      service,
      "AI/Classified",
    )


@app.command()
def label_recent(
    limit: int = 10,
    query: str = "in:inbox -label:AI/Classified",
    apply: bool = False,
):
    """Classify recent messages and optionally apply topic labels."""

    config = load_config()

    service = get_service()

    classified_label_id = get_or_create_label(
        service,
        "AI/Classified",
    )

    for i, email in enumerate(
        get_messages(limit=limit, query=query),
        start=1,
    ):
        typer.echo(
            f"[{i}/{limit}] {email.subject[:70]}"
        )

        try:
            result = classify(email, config)

            topic = result.topic.value

            typer.echo(
                f"  → {topic}"
            )

            if apply:
                label_id = get_or_create_label(
                    service,
                    topic,
                )

                apply_label(
                    service,
                    email.id,
                    label_id,
                )

                apply_label(
                    service,
                    email.id,
                    classified_label_id,
                )

                typer.secho(
                    "  ✓ applied",
                    fg=typer.colors.GREEN,
                )

        except Exception as exc:
            typer.secho(
                f"  ERROR: {exc}",
                fg=typer.colors.RED,
            )

if __name__ == "__main__":
    app()
