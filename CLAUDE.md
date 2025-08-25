# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
File Organizer - A Python utility that automatically organizes files by type into categorized folders. Zero external dependencies by design.

**Project Location**: `/home/william-cloutman/Vibes/fileorg/`

## Development Commands

### Running the Application
```bash
# Main execution
python3 file_organizer.py

# Dry-run mode (preview changes)
python3 file_organizer.py --dry-run
```

### Testing
```bash
# Run tests
python3 -m unittest test_fileorg.py test_integration.py test_safety.py -v

# Run tests with coverage (if coverage installed)
coverage run -m unittest test_fileorg.py test_integration.py test_safety.py
coverage report -m

# Run a single test file
python3 -m unittest test_safety.py -v

# Run a specific test
python3 -m unittest test_fileorg.TestFileOrganizer.test_organize_files -v
```

### Code Quality
```bash
# Lint code
ruff check .

# Format check
ruff format --check .

# Auto-fix linting issues
ruff check . --fix

# Format code
ruff format .

# Security scan
bandit -r .
```

## Architecture

### Core Design Principles
- **Zero dependencies**: Uses only Python standard library - no requirements.txt needed
- **Single file application**: All core logic in `file_organizer.py`
- **Security-first**: Checksum verification, permission validation, safe operations

### Key Components

**FileOrganizer Class** (`file_organizer.py`)
- Main orchestrator for file organization
- Categorizes files into 9 types: Documents, Images, Videos, Audio, Archives, Code, Spreadsheets, Presentations, Other
- Implements safe file operations with rollback capability
- Comprehensive logging of all operations

### File Categories Mapping
```python
FILE_CATEGORIES = {
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.tiff'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
    'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c', '.h', '.json', '.xml', '.sql'],
    'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
    'Presentations': ['.ppt', '.pptx', '.odp'],
}
```

### Testing Strategy
- Comprehensive unit tests in `test_fileorg.py`
- Tests cover: core functionality, edge cases, error handling, permissions, cross-platform compatibility
- Mock filesystem operations for isolated testing
- Target: 95%+ code coverage

### CI/CD Pipeline
GitHub Actions workflow tests across:
- **Platforms**: Ubuntu, Windows, macOS
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Checks**: Linting, formatting, security scanning, test coverage

## Important Implementation Notes

### Error Handling
- All file operations wrapped in try-except blocks
- Detailed logging with timestamps for audit trails
- Graceful degradation on permission errors

### File Conflict Resolution
- Automatic renaming with incrementing numbers for duplicates
- Pattern: `filename_1.ext`, `filename_2.ext`, etc.

### Security Considerations
- Never moves system files or hidden files (starting with '.')
- Validates read/write permissions before operations
- Maintains SHA-256 checksums in `checksums.txt`
- Secure installer with integrity verification

### Cross-Platform Compatibility
- Uses `pathlib` for path operations
- Handles Windows, Linux, macOS path separators
- Tested on all major platforms via CI/CD