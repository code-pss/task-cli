# 🚀 task-cli — Git-style Task Manager

A robust, terminal-based task manager built with Python, featuring a Git-inspired workflow and a focus on clean architecture using the Repository Pattern.

## ✨ Features

- **Git-Style Workflow**: Use `add`, `commit`, `checkout`, and `status` to manage your tasks.
- **Interactive Shell**: A smooth, colorized interactive shell (via `shlex` and `rich`).
- **Type-Safe Models**: Robust data validation and error handling.
- **Clean Architecture**: Implements the Repository Pattern, making it easy to swap persistence layers (e.g., JSON to Database).
- **Rich Visualization**: Beautifully formatted tables and logs using the `rich` library.

## 🛠️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd task-cli

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

Run the interactive shell:
```bash
python main.py
```

### Command Reference

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `add` | `"<title>"` | Create a new task and set it as active. |
| `commit` | `-m "<message>"` | Log progress on the active task. |
| `push` | `-s <status>` | Update the status of the active task. |
| `status` | — | Show the current state of the active task. |
| `log` | `[id]` | Show commit history for a task. |
| `checkout` | `<id>` | Switch the active task. |
| `show` | `[-s status]` | List all tasks or filter by status. |
| `search` | `"<keyword>"` | Search tasks by title or context. |
| `delete` | `<id>` | Remove a task. |
| `clear` | — | Clear the terminal (aliases: `cls`). |
| `exit` | — | Exit the interactive shell (aliases: `quit`, `q`). |

### Available Statuses
`pending` | `in-progress` | `on-hold` | `review` | `complete` | `dropped`

## 🏗️ Architecture

The application follows clean architecture principles:
- **Models (`models.py`)**: Defines `Task` and `Commit` data structures with Pydantic-like validation.
- **Repository Pattern (`repository.py`, `storage.py`)**: Abstracted data access layer using a `JSONStorage` implementation.
- **Manager (`manager.py`)**: Encapsulates business logic and orchestrates task state.
- **CLI/Display (`cli.py`, `display.py`)**: Handles user interaction and beautifully renders output.

## 📄 License
MIT
