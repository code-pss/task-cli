import sys
from app.manager import TaskManager, VALID_STATUSES
from app import display
from rich import print as rprint
from rich.console import Console

console  = Console()
manager  = TaskManager()


# ── Help ─────────────────────────────────────────────────────────────────────

def print_help():
    console.print()
    rprint("[grey37]─────────────────────────────────────────────[/grey37]")
    rprint("[bright_green bold]  task  —  Git-style Task Manager[/bright_green bold]")
    rprint("[grey37]─────────────────────────────────────────────[/grey37]")
    console.print()

    cmds = [
        ("task add",        '"<title>" [-c context]',              "Start tracking a new task"),
        ("task commit",     '-m "<message>" [-s status]',          "Log progress on active task"),
        ("task push",       '-s <status>',                         "Push a status update"),
        ("task status",     "",                                     "Show active task (like git status)"),
        ("task log",        "[id]",                                 "Show commit history"),
        ("task checkout",   "<id>",                                 "Switch active task"),
        ("task show",       "[-s status]",                         "List all tasks or filter by status"),
        ("task search",     "<keyword>",                           "Search tasks by keyword"),
        ("task delete",     "<id>",                                 "Delete a task"),
        ("task help",       "",                                     "Show this help"),
    ]

    for cmd, args, desc in cmds:
        rprint(
            f"  [bright_green]{cmd:<18}[/bright_green]"
            f"[grey58]{args:<36}[/grey58]"
            f"[grey70]{desc}[/grey70]"
        )

    console.print()
    rprint(f"[grey58]  Statuses: {' | '.join(VALID_STATUSES)}[/grey58]")
    console.print()
    rprint("[grey37]─────────────────────────────────────────────[/grey37]")
    console.print()


# ── Flag Parser ──────────────────────────────────────────────────────────────

def parse_args(tokens: list[str]) -> tuple[list[str], dict]:
    """
    Split tokens into positional args and --flag / -f value pairs.
    Handles:
      -m "message"
      --status complete
      -s in-progress
    """
    positional = []
    flags      = {}
    i          = 0

    while i < len(tokens):
        tok = tokens[i]

        if tok.startswith("--"):
            key = tok[2:]
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                flags[key] = tokens[i + 1]
                i += 2
            else:
                flags[key] = True
                i += 1

        elif tok.startswith("-") and len(tok) == 2:
            key = tok[1]
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                flags[key] = tokens[i + 1]
                i += 2
            else:
                flags[key] = True
                i += 1

        else:
            positional.append(tok)
            i += 1

    return positional, flags


# ── Command Handlers ─────────────────────────────────────────────────────────

def cmd_add(pos, flags):
    if not pos:
        display.error('Usage: task add "<title>" [-c context]')
        return
    title   = " ".join(pos)
    context = flags.get("c", flags.get("context", ""))
    task    = manager.add(title, context)
    console.print()
    rprint(f"[bright_green]Initialized task[/bright_green] [grey58]#{task.id}[/grey58]")
    rprint(f"[bright_green]→[/bright_green] [bright_green bold]{task.title}[/bright_green bold]")
    if task.context:
        rprint(f"  [grey58]{task.context}[/grey58]")
    console.print()


def cmd_commit(pos, flags):
    message = flags.get("m", flags.get("message", ""))
    status  = flags.get("s", flags.get("status", None))

    if not message:
        display.error('Usage: task commit -m "<message>" [-s status]')
        return
    try:
        task, commit = manager.commit(message, status)
        display.commit_line(task, commit)
    except ValueError as e:
        display.error(str(e))


def cmd_push(pos, flags):
    status = flags.get("s", flags.get("status", pos[0] if pos else None))
    if not status:
        display.error("Usage: task push -s <status>")
        return
    try:
        task = manager.push(status)
        console.print()
        rprint(f"[bright_green]Pushed[/bright_green] [grey58]#{task.id}[/grey58] [bright_green bold]{task.title}[/bright_green bold]")
        rprint(f"  [grey58]status →[/grey58] {display._status_badge(task.status)}")
        console.print()
    except ValueError as e:
        display.error(str(e))


def cmd_status(pos, flags):
    try:
        task = manager.status()
        display.render_status(task)
    except ValueError as e:
        display.error(str(e))


def cmd_log(pos, flags):
    try:
        task_id = int(pos[0]) if pos else None
        task, commits = manager.log(task_id)
        display.render_log(task, commits)
    except ValueError as e:
        display.error(str(e))


def cmd_checkout(pos, flags):
    if not pos:
        display.error("Usage: task checkout <id>")
        return
    try:
        task = manager.checkout(int(pos[0]))
        console.print()
        rprint(f"[bright_green]Switched to task[/bright_green] [grey58]#{task.id}[/grey58]  [bright_green bold]{task.title}[/bright_green bold]")
        console.print()
    except ValueError as e:
        display.error(str(e))


def cmd_show(pos, flags):
    status = flags.get("s", flags.get("status", None))
    try:
        tasks = manager.show(status)
        title = f"status: {status}" if status else "all tasks"
        display.render_tasks(tasks, active_id=manager.active_id, title=title)
    except ValueError as e:
        display.error(str(e))


def cmd_search(pos, flags):
    if not pos:
        display.error("Usage: task search <keyword>")
        return
    keyword = " ".join(pos)
    results = manager.search(keyword)
    display.render_tasks(results, active_id=manager.active_id, title=f'search: "{keyword}"')


def cmd_delete(pos, flags):
    if not pos:
        display.error("Usage: task delete <id>")
        return
    try:
        task = manager.delete(int(pos[0]))
        rprint(f"\n[grey58]Deleted task #{task.id} — {task.title}[/grey58]\n")
    except ValueError as e:
        display.error(str(e))


# ── Router ────────────────────────────────────────────────────────────────────

COMMANDS = {
    "add":      cmd_add,
    "commit":   cmd_commit,
    "push":     cmd_push,
    "status":   cmd_status,
    "log":      cmd_log,
    "checkout": cmd_checkout,
    "show":     cmd_show,
    "search":   cmd_search,
    "delete":   cmd_delete,
    "help":     lambda p, f: print_help(),
}


def run(argv: list[str]):
    """
    Entry point called from task.py with sys.argv[1:]
    e.g.  task add "Reading" -c "Read 15 pages"
    """
    if not argv:
        print_help()
        return

    command = argv[0].lower()
    rest    = argv[1:]

    pos, flags = parse_args(rest)

    if command in COMMANDS:
        COMMANDS[command](pos, flags)
    else:
        display.error(f'Unknown command "{command}". Run: task help')