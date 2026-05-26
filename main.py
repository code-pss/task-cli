import shlex
from rich import print as rprint
from rich.console import Console
from app.cli import run

console = Console()


def main():
    rprint("\n[bright_green bold]task[/bright_green bold] [grey58]interactive shell  ·  type 'help' or 'exit'[/grey58]\n")

    while True:
        try:
            raw = console.input("[grey37]>[/grey37] [bright_green]task[/bright_green] [grey58]»[/grey58] ").strip()
        except (KeyboardInterrupt, EOFError):
            rprint("\n[grey58]bye.[/grey58]\n")
            break

        if not raw:
            continue
        if raw in ("exit", "quit", "q"):
            rprint("\n[grey58]bye.[/grey58]\n")
            break

        try:
            tokens = shlex.split(raw)
            run(tokens)
        except Exception as e:
            rprint(f"[bright_red]error:[/bright_red] [grey58]{e}[/grey58]")


if __name__ == "__main__":
    main()