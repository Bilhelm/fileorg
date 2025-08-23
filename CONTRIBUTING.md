# Contributing to File Organizer

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/fileorg.git`
3. Create a branch: `git checkout -b feature-name`
4. Make your changes
5. Run tests: `python -m pytest test_fileorg.py`
6. Submit a pull request

## Development Setup

Install development dependencies:
```bash
pip install ruff pytest coverage
```

## Code Style

- Follow PEP 8 guidelines
- Use Ruff for linting: `ruff check .`
- Write tests for new features
- Add docstrings to functions

## Running Tests

```bash
# Run all tests
python -m pytest test_fileorg.py -v

# Check coverage
coverage run -m pytest test_fileorg.py
coverage report -m
```

## Pull Request Guidelines

- Include a clear description of changes
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

## Questions?

Open an issue or contact: wcloutman@hotmail.com