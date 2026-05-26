#!/usr/bin/env python3
import shlex
from rich import print as rprint
from rich.console import Console
from rich.text import Text
from app.cli import run, print_help
from app.manager import TaskManager

console = Console()


def print_banner():
    console.print()
    rprint("[grey37]─────────────────────────────────────────────[/grey37]")
    rprint("[bright_green bold]  task[/bright_green bold] [grey58]— Git-style Task Manager[/grey58]")
    rprint("[grey37]─────────────────────────────────────────────[/grey37]")
    rprint("[grey58]  type 'help' for commands  ·  'exit' to quit[/grey58]")
    rprint("[grey37]─────────────────────────────────────────────[/grey37]")
    console.print()


def main():
    print_banner()

    while True:
        try:
            raw = console.input(
                "[grey37][[/grey37][bright_green]task[/bright_green][grey37]][/grey37] [bright_green]»[/bright_green] "
            ).strip()

        except (KeyboardInterrupt, EOFError):
            rprint("\n[grey58]bye.[/grey58]\n")
            break

        if not raw:
            continue

        if raw in ("exit", "quit", "q"):
            rprint("\n[grey58]bye.[/grey58]\n")
            break

        if raw == "help":
            print_help()
            continue

        try:
            tokens = shlex.split(raw)   # handles "quoted strings" properly
        except ValueError as e:
            rprint(f"[bright_red]parse error:[/bright_red] [grey58]{e}[/grey58]")
            continue

        # allow typing with or without the word "task" at the start
        # e.g. both "task add ..." and "add ..." work fine
        if tokens and tokens[0].lower() == "task":
            tokens = tokens[1:]

        if not tokens:
            continue

        try:
            run(tokens)
        except Exception as e:
            rprint(f"[bright_red]error:[/bright_red] [grey58]{e}[/grey58]")


if __name__ == "__main__":
    main()