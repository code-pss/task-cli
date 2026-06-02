from datetime import datetime
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from app.models import Task, Commit

console = Console()

# ── Theme ────────────────────────────────────────────────────────────────────
THEME = {
    "primary":   "bright_green",
    "dim":       "grey58",
    "border":    "grey37",
    "title":     "bright_green bold",
    "error":     "bright_red",
    "warning":   "yellow",
    "label":     "grey70",
    "highlight": "bright_green bold",
}

STATUS_COLOR = {
    "pending":     "grey58",
    "in-progress": "bright_green",
    "on-hold":     "yellow",
    "review":      "cyan",
    "complete":    "green",
    "dropped":     "red",
}

STATUS_ICON = {
    "pending":     "[ ]",
    "in-progress": "[>]",
    "on-hold":     "[=]",
    "review":      "[?]",
    "complete":    "[v]",
    "dropped":     "[x]",
}


def _status_badge(status) -> str:
    # Handle Status Enum or string
    val = status.value if hasattr(status, "value") else str(status)
    color = STATUS_COLOR.get(val, "white")
    icon  = STATUS_ICON.get(val, "?")
    return f"[{color}]{icon} {val}[/{color}]"


def _fmt_time(val) -> str:
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M")
    try:
        dt = datetime.fromisoformat(str(val))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(val)


# ── Task Table ───────────────────────────────────────────────────────────────

def render_tasks(tasks: list[Task], active_id: int = None, title: str = "Tasks") -> None:
    if not tasks:
        rprint(f"\n[{THEME['dim']}]  No tasks found.[/{THEME['dim']}]\n")
        return

    table = Table(
        show_header   = True,
        header_style  = f"bold {THEME['border']}",
        border_style  = THEME["border"],
        show_lines    = True,
        title         = f"[{THEME['title']}]{title}[/{THEME['title']}]",
        title_justify = "left",
    )

    table.add_column("",        width=2)                      # active marker
    table.add_column("ID",      style=THEME["dim"],   width=4)
    table.add_column("Task",    style="bright_green",  min_width=20)
    table.add_column("Status",  width=14)
    table.add_column("Context", style=THEME["dim"],   min_width=16)
    table.add_column("Commits", style=THEME["dim"],   width=8, justify="center")
    table.add_column("Updated", style=THEME["dim"],   width=16)

    for t in tasks:
        marker = f"[{THEME['primary']}]>>[/{THEME['primary']}]" if t.id == active_id else ""
        table.add_row(
            marker,
            str(t.id),
            t.title,
            _status_badge(t.status),
            t.context or "—",
            str(len(t.commits)),
            _fmt_time(t.updated_at),
        )

    console.print()
    console.print(table)
    console.print()


# ── Commit Log ───────────────────────────────────────────────────────────────

def render_log(task: Task, commits: list[Commit]) -> None:
    console.print()
    rprint(f"[{THEME['dim']}]task[/{THEME['dim']}] [{THEME['primary']}]#{task.id}[/{THEME['primary']}]  [{THEME['title']}]{task.title}[/{THEME['title']}]")
    rprint(f"[{THEME['dim']}]status  {_status_badge(task.status)}[/{THEME['dim']}]")
    console.print()

    if not commits:
        rprint(f"[{THEME['dim']}]  No commits yet.[/{THEME['dim']}]\n")
        return

    for i, c in enumerate(reversed(commits)):
        is_last = i == 0
        color   = THEME["primary"] if is_last else THEME["dim"]
        dot     = "*" if is_last else "o"

        rprint(f"  [{color}]{dot}[/{color}]  [{color}]{c.message}[/{color}]")
        rprint(f"       [{THEME['dim']}]{_status_badge(c.status)}  ·  {_fmt_time(c.timestamp)}[/{THEME['dim']}]")
        if i < len(commits) - 1:
            rprint(f"       [{THEME['dim']}]│[/{THEME['dim']}]")

    console.print()


# ── Status Panel (git status style) ─────────────────────────────────────────

def render_status(task: Task, active: bool = True) -> None:
    console.print()

    lines = [
        f"[{THEME['dim']}]On task[/{THEME['dim']}]  [{THEME['primary']} bold]{task.title}[/{THEME['primary']} bold]",
        f"[{THEME['dim']}]Status  [/{THEME['dim']}]{_status_badge(task.status)}",
        "",
    ]

    if task.context:
        lines.append(f"[{THEME['dim']}]Context:[/{THEME['dim']}]  [{THEME['label']}]{task.context}[/{THEME['label']}]")
        lines.append("")

    if task.commits:
        last = task.last_commit
        lines.append(f"[{THEME['dim']}]Last commit:[/{THEME['dim']}]")
        lines.append(f"  [{THEME['primary']}]* {last.message}[/{THEME['primary']}]")
        lines.append(f"    [{THEME['dim']}]{_fmt_time(last.timestamp)}[/{THEME['dim']}]")
    else:
        lines.append(f"[{THEME['dim']}]No commits yet.[/{THEME['dim']}]")

    content = Text.from_markup("\n".join(lines))
    panel = Panel(
        content,
        border_style = THEME["border"],
        padding      = (1, 2),
    )
    console.print(panel)
    console.print()


# ── Inline Messages ──────────────────────────────────────────────────────────

def success(msg: str):
    rprint(f"[{THEME['primary']}]✔  {msg}[/{THEME['primary']}]")

def error(msg: str):
    rprint(f"[{THEME['error']}]✖  {msg}[/{THEME['error']}]")

def info(msg: str):
    rprint(f"[{THEME['dim']}]ℹ  {msg}[/{THEME['dim']}]")

def commit_line(task: Task, commit: Commit):
    rprint(f"[{THEME['primary']}][task #{task.id}][/{THEME['primary']}] [{THEME['dim']}]{task.title}[/{THEME['dim']}]")
    rprint(f"  [{THEME['primary']}]* {commit.message}[/{THEME['primary']}]")
    rprint(f"    [{THEME['dim']}]{_status_badge(commit.status)}  ·  {_fmt_time(commit.timestamp)}[/{THEME['dim']}]")
    console.print()