# File Organizer 🗂️

A Python utility to automatically organize files by type into categorized folders.

## Features

- **Smart categorization** - Automatically sorts files by type (Documents, Images, Videos, etc.)
- **Safe operation** - Dry run mode to preview changes before moving files
- **Conflict handling** - Automatically renames duplicate files
- **Detailed logging** - Tracks all operations with timestamps
- **Cross-platform** - Works on Windows, macOS, and Linux

## Installation

1. Clone this repository:
```bash
git clone https://github.com/wcloutman/fileorg.git
cd fileorg
```

2. Run the organizer:
```bash
python file_organizer.py
```

## Usage

### Interactive Mode
```bash
python file_organizer.py
```

### Programmatic Usage
```python
from file_organizer import FileOrganizer

# Organize Downloads folder
organizer = FileOrganizer()
organizer.organize_files()

# Organize custom directory
organizer = FileOrganizer("/path/to/messy/folder")
organizer.organize_files(dry_run=True)  # Preview first
organizer.organize_files()  # Actually move files
```

## File Categories

- **Documents**: PDF, Word, Text files
- **Images**: JPEG, PNG, GIF, SVG, etc.
- **Videos**: MP4, AVI, MKV, MOV, etc.
- **Audio**: MP3, WAV, FLAC, AAC, etc.
- **Archives**: ZIP, RAR, 7Z, TAR, etc.
- **Code**: Python, JavaScript, HTML, CSS, etc.
- **Spreadsheets**: Excel, CSV, ODS
- **Presentations**: PowerPoint, ODP
- **Other**: Unrecognized file types

## Example Output

```
📊 File Organization Report for /Users/you/Downloads
==================================================
Total files: 47

Documents   :  12 files (25.5%)
Images      :  18 files (38.3%)
Videos      :   8 files (17.0%)
Archives    :   6 files (12.8%)
Other       :   3 files (6.4%)
```

## Safety Features

- Creates organized folders without deleting originals
- Handles filename conflicts automatically
- Logs all operations for audit trail
- Dry run mode for safe testing

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Contributing

Pull requests welcome! Please add tests for new features.

## License

MIT License - feel free to use this in your own projects!

## Author

William Cloutman (wcloutman@hotmail.com)