import os
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from google import genai
from google.genai import types

from schemas import TicketAnalysis

app = typer.Typer(help="Automated Customer Support Intent & Sentiment Router CLI")
console = Console()


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]Error: File not found -> {file_path}[/bold red]")
        raise typer.Exit(1)

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[bold red]Failed to read file: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def route(
    ticket: str = typer.Argument(
        ..., help="Path to support ticket file or raw text string"
    ),
):
    """Analyze a customer support ticket, classify intent/sentiment, assign priority queue, and draft a response."""

    if not os.environ.get("GEMINI_API_KEY"):
        console.print(
            "[bold red]Error: GEMINI_API_KEY environment variable is not set.[/bold red]"
        )
        raise typer.Exit(1)

    # Handle ticket being a file path or inline text
    if Path(ticket).exists():
        ticket_text = extract_text(ticket)
    else:
        ticket_text = ticket

    client = genai.Client()

    prompt = f"""
You are an advanced enterprise customer support routing and triage engine. 
Analyze the incoming customer ticket below. Classify its intent, assess customer sentiment and urgency, assign an appropriate priority queue (P0-Critical to P3-Low), extract key technical entities, and draft a professional support response.

=== INCOMING TICKET ===
{ticket_text}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description="Routing ticket & analyzing sentiment with Gemini...",
            total=None,
        )

        try:
            # Temporarily suppress stderr to keep terminal output clean
            original_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=TicketAnalysis,
                        temperature=0.1,
                    ),
                )
            finally:
                sys.stderr.close()
                sys.stderr = original_stderr

            result = TicketAnalysis.model_validate_json(response.text)
        except Exception as e:
            console.print(f"[bold red]Ticket routing failed: {e}[/bold red]")
            raise typer.Exit(1)

    # Render Dashboard using Rich
    console.print("\n")
    console.print(
        Panel.fit(
            f"[bold cyan]🎫 Support Ticket Routing Report[/bold cyan]\n"
            f"Customer: [bold green]{result.customer_name or 'Unidentified'}[/bold green]",
            title="Intent & Sentiment Router",
            border_style="cyan",
        )
    )

    # Triage Table
    triage_table = Table(show_header=True, header_style="bold magenta")
    triage_table.add_column("Routing Metric", style="dim")
    triage_table.add_column("Classification", justify="right")

    # Color-code priority queue
    p_color = (
        "red"
        if "P0" in result.priority_queue
        else (
            "dark_orange"
            if "P1" in result.priority_queue
            else ("yellow" if "P2" in result.priority_queue else "green")
        )
    )
    sentiment_color = "red" if result.sentiment in ["Angry", "Frustrated"] else "green"

    triage_table.add_row(
        "Assigned Priority Queue",
        f"[{p_color} bold]{result.priority_queue}[/{p_color} bold]",
    )
    triage_table.add_row("Intent Category", f"[bold blue]{result.intent}[/bold blue]")
    triage_table.add_row(
        "Customer Sentiment",
        f"[{sentiment_color}]{result.sentiment}[/{sentiment_color}]",
    )
    triage_table.add_row("Urgency Score", f"{result.urgency_score * 100:.0f}%")
    triage_table.add_row("Router Confidence", f"{result.confidence_score * 100:.0f}%")
    console.print(triage_table)

    # Key Entities Panel
    entities_str = (
        ", ".join([f"[yellow]{e}[/yellow]" for e in result.key_entities])
        or "None detected"
    )
    console.print(
        Panel(
            entities_str,
            title="[bold blue]🏷️ Extracted Entities & Codes[/bold blue]",
            border_style="blue",
        )
    )

    # Summary Panel
    console.print(
        Panel(
            result.summary,
            title="[bold yellow]📋 Issue Summary[/bold yellow]",
            border_style="yellow",
        )
    )

    # Draft Response Panel
    console.print(
        Panel(
            result.suggested_response,
            title="[bold green]✉️ Suggested Auto-Response Draft[/bold green]",
            border_style="green",
        )
    )
    console.print("\n")


if __name__ == "__main__":
    app()
