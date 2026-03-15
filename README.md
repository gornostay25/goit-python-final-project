# Personal Assistant

A command-line Personal Assistant for managing contacts and notes. Built as a final project for the Python Programming: Foundations and Best Practices course.

## Description

This Personal Assistant is designed to help you manage your personal information efficiently through an intuitive command-line interface. It serves as both a practical application and a demonstration of team collaboration, software development best practices, and project management skills.

## Demo

![Demo Asciinema](./docs/demo.gif)

### Key Features

- **Contact Management**
  - Store contacts with names, addresses, phone numbers, emails, and birthdays
  - Validate phone numbers and email addresses during entry
  - Search contacts by various criteria
  - Edit and delete contact records
  - Display upcoming birthdays within a specified number of days

- **Notes Management**
  - Create and store text notes with optional tags for organization
  - Search, edit, and delete notes
  - Sort notes by tags
  - Find notes by tag

- **Intelligent Command Interface**
  - Command completion with suggestions
  - Intelligent command suggestions for typos
  - Rich text output with tables and colored messages

- **Data Persistence**
  - All data stored securely on disk in JSON format
  - Application can be restarted without data loss
  - Automatic data validation and error handling

## Installation

### Prerequisites

- [uv](https://github.com/astral-sh/uv) package manager

### Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/gornostay25/goit-python-final-project.git
   cd goit-python-final-project
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

That's it! uv automatically creates a virtual environment (`.venv`) and installs all dependencies including dev dependencies (ruff, pre-commit). No manual activation needed when using `uv run`.

To install only production dependencies (excluding dev tools), use:

```bash
uv sync --no-dev
```

## Usage

### Running the Application

Start the Personal Assistant:

```bash
uv run python -m app
```

Alternatively, run the script directly:

```bash
uv run src/app/__main__.py
```

## Development

### Project Structure

```
goit-python-final-project/
├── .github/
│   └── workflows/
│       └── ruff.yml              # GitHub Actions workflow for Ruff CI
├── .gitignore                 # Git ignore patterns
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── .python-version            # Python version pin
├── LICENSE                    # MIT License
├── pyproject.toml             # Project configuration
├── README.md                  # This file
├── contacts.json              # Persistent storage for contacts (.gitignore)
├── notes.json                 # Persistent storage for notes (.gitignore)
└── src/
    └── app/
        ├── __init__.py        # Package initialization with metadata
        ├── __main__.py        # Entry point with storage initialization
        ├── cli.py             # CLI implementation with Rich-based UI
        ├── contacts.py        # Contact models, Birthday class, ContactBook
        ├── notes.py           # Note models, NotesBook with tag support
        ├── storage.py         # Data persistence layer
        ├── utils.py           # Utility functions and validators
        └── types.py           # Type definitions and enums
└── tests/
    ├── __init__.py            # Test package
    ├── conftest.py            # Pytest fixtures
    ├── test_contacts.py       # Contact-related tests
    ├── test_notes.py          # Note-related tests
    ├── test_cli.py            # CLI tests
    ├── test_storage.py        # Storage tests
    └── test_utils.py          # Utility tests
```

### Development Setup

1. Ensure dependencies are installed:

   ```bash
   uv sync
   ```

   Note: The dev dependency group is installed by default. Use `uv sync --no-dev` to exclude dev dependencies.

2. Add new dependencies:

   ```bash
   uv add <package-name>
   ```

3. Add development dependencies:

   ```bash
   uv add --dev <package-name>
   ```

4. Run linting:

   ```bash
   uv run ruff check src/
   ```

5. Format code:

   ```bash
   uv run ruff format src/
   ```

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) for automated code quality checks before commits.

To set up pre-commit hooks:

1. Ensure dependencies are installed:

   ```bash
   uv sync
   ```

2. Install the pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

Now the hooks will run automatically before each commit. To run them manually:

```bash
uv run pre-commit run --all-files
```

The pre-commit configuration includes:
- **ruff**: Python linter with auto-fix
- **ruff-format**: Python code formatter
- **General checks**: Trailing whitespace, end-of-file fixer, YAML validation, etc.

### Git Workflow

This project follows a simple Git workflow to maintain code quality:

#### Branches
- **main**: Production branch (protected, no direct pushes)
- **feature/***: Feature implementation branches
- **fix/***: Bugfix branches

#### Pull Request Workflow
1. Create a new branch from `main`:

   ```bash
   # For a new feature
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name

   # For a bugfix
   git checkout -b fix/your-fix-name
   ```

2. Make your changes and commit them

3. Push your branch:

   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request to merge into `main`

5. After review and approval, merge the PR into `main`

#### Merge Flow

```mermaid
graph LR
    A[feature/* or fix/*] -->|PR| B[main]
```

### GitHub Actions

This project uses GitHub Actions for automated code quality checks and testing.

#### Ruff CI

The [`.github/workflows/ruff.yml`](.github/workflows/ruff.yml) workflow runs on:
- Push to `main`, `feature/*`, `fix/*` branches
- Pull requests to `main` branch

It automatically runs Ruff checks with auto-fix on your code to ensure code quality before merging.

#### Pytest Testing

The [`.github/workflows/pytest.yml`](.github/workflows/pytest.yml) workflow runs on:
- Pull requests to `main` branch

It automatically runs the full test suite across multiple Python versions:
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

All tests use the project's virtual environment and pytest framework with verbose output.

### Testing

This project uses [pytest](https://docs.pytest.org/) for comprehensive testing. All core functionality is covered by unit tests.

To run tests:

```bash
uv run pytest
```

To run with coverage:

```bash
uv run pytest --cov=src/app --cov-report=html
```

Available test suites:
- **test_contacts.py**: Tests for Contact model, Birthday class, and ContactBook
- **test_notes.py**: Tests for Note model, tag management, and NotesBook
- **test_cli.py**: Integration tests for CLI commands and interactions
- **test_storage.py**: Tests for JSON persistence and data loading/saving
- **test_utils.py**: Tests for validators, error handling, and utility functions

## Features

### Contact Management

The Personal Assistant provides complete contact management capabilities:

- **Add Contacts**: Create contacts with name, address, phone number, email, and birthday
- **Validation**: Automatic validation of phone numbers (E.164 format) and email addresses
- **Search**: Find contacts by name, phone, email, or birthday
- **Edit & Delete**: Modify or remove contact records
- **Birthdays**: Display upcoming birthdays within a specified number of days

### Notes Management

Organize your notes with powerful tag-based organization:

- **Add Notes**: Create text notes with optional tags for categorization
- **Tag System**: Automatic tag cleaning (lowercase, stripped, deduplicated)
- **Search**: Find notes by text content or tags
- **Sort**: Sort notes alphabetically by tags
- **Edit & Delete**: Modify or remove notes

### Command-Line Interface

The CLI provides a rich interactive experience:

- **Command Completion**: Auto-completion for all available commands
- **Intelligent Suggestions**: Typo-aware command suggestions
- **Rich Output**: Tables, colored messages, and formatted displays
- **Error Handling**: Clear error messages with actionable guidance
- **Startup Screen**: Animated splash screen with project information

### Data Persistence

All data is stored in JSON format in the user's home directory:

- **Contacts**: Stored in `contacts.json`
- **Notes**: Stored in `notes.json`
- **Auto-Save**: Data is automatically saved after each operation
- **Data Recovery**: Application can be restarted without data loss
- **Error Resilience**: Graceful handling of corrupted data files

## Contributing

This is a team project developed by:
- [Volodymyr Palamar](https://gornostay25.dev)
- [Liudmyla Slipko](https://github.com/slipkoliudmyla)
- [Aurika](https://github.com/diagnosel)
- [Daniil Kukhar](https://github.com/DaniilKukhar)

### Contribution Guidelines

1. Create a new branch for your feature or bugfix
2. Write clear, descriptive commit messages
3. Ensure all tests pass
4. Follow the existing code style (enforced by ruff)
5. Submit a pull request for review

### Team Roles

- **Team Lead**: Coordinates project direction and team collaboration (Volodymyr Palamar)
- **Scrum Master**: Manages tasks using Trello and ensures sprint goals are met (Liudmyla Slipko)
- **Developer**: Implements features and bug fixes (Aurika, Daniil Kukhar)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was developed as part of the **Python Programming: Foundations and Best Practices** course. Special thanks to the instructors and team members for their collaboration and support.
