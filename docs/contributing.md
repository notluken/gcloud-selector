# Contributing to GCloud Selector

Thank you for your interest in contributing!

## Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/gcloud-selector.git
cd gcloud-selector
pip install -e ".[dev]"

# Run checks
pytest              # Tests
ruff check .        # Linting
mypy gcloud_selector  # Type checking
```

## Development Setup

1. Fork the repository on GitHub
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

## Making Changes

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests: `pytest`
4. Format code: `ruff format gcloud_selector`
5. Commit with conventional messages: `feat: add new feature`

## Pull Request Process

1. Push your branch
2. Open a PR with description of changes
3. Respond to review feedback
4. Merge once approved

## Code Style

- Use type hints
- Follow PEP 8 (enforced by Ruff)
- Write docstrings for public APIs
- Add tests for new features

## Project Structure

```
gcloud_selector/
├── cli.py      # Entry point, argument parsing
├── config.py   # Configuration, caching, history
├── gcloud.py   # GCloud CLI wrapper
└── ui.py       # Terminal UI components
```

## Questions?

Open a GitHub issue or discussion.
