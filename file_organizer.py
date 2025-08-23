#!/usr/bin/env python3
"""
File Organizer - Automatically organize files by type
Author: William Cloutman
"""

import os
import shutil
from pathlib import Path
import logging
from datetime import datetime

class FileOrganizer:
    def __init__(self, source_dir=None):
        """Initialize the file organizer."""
        self.source_dir = Path(source_dir) if source_dir else Path.home() / "Downloads"
        self.setup_logging()
        
        # File type mappings
        self.file_types = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php'],
            'Spreadsheets': ['.xlsx', '.xls', '.csv', '.ods'],
            'Presentations': ['.pptx', '.ppt', '.odp']
        }
    
    def setup_logging(self):
        """Set up logging for the organizer."""
        log_dir = Path.home() / "Documents" / "fileorg_logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"organizer_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_file_category(self, file_path):
        """Determine the category of a file based on its extension."""
        extension = file_path.suffix.lower()
        
        for category, extensions in self.file_types.items():
            if extension in extensions:
                return category
        
        return 'Other'
    
    def create_organized_structure(self):
        """Create the organized folder structure."""
        organized_dir = self.source_dir / "Organized"
        organized_dir.mkdir(exist_ok=True)
        
        for category in self.file_types.keys():
            (organized_dir / category).mkdir(exist_ok=True)
        
        (organized_dir / "Other").mkdir(exist_ok=True)
        return organized_dir
    
    def organize_files(self, dry_run=False):
        """Organize files in the source directory."""
        if not self.source_dir.exists():
            self.logger.error(f"Source directory {self.source_dir} does not exist!")
            raise FileNotFoundError(f"Source directory does not exist: {self.source_dir}")
        
        if not self.source_dir.is_dir():
            self.logger.error(f"Path is not a directory: {self.source_dir}")
            raise NotADirectoryError(f"Path is not a directory: {self.source_dir}")
        
        # Check permissions
        if not os.access(self.source_dir, os.R_OK):
            self.logger.error(f"No read permission for directory: {self.source_dir}")
            raise PermissionError(f"No read permission for directory: {self.source_dir}")
        
        if not dry_run and not os.access(self.source_dir, os.W_OK):
            self.logger.error(f"No write permission for directory: {self.source_dir}")
            raise PermissionError(f"No write permission for directory: {self.source_dir}")
        
        try:
            organized_dir = self.create_organized_structure()
            moved_files = 0
            failed_files = 0
            
            self.logger.info(f"Starting file organization in {self.source_dir}")
            self.logger.info(f"Dry run mode: {dry_run}")
            
            # Get list of files first to avoid issues with directory changes
            files_to_process = [f for f in self.source_dir.iterdir() 
                              if f.is_file() and f.name not in {".DS_Store", "Thumbs.db", ".gitignore"}]
            
            if not files_to_process:
                self.logger.info("No files found to organize.")
                return {'moved': 0, 'failed': 0, 'total': 0}
            
            self.logger.info(f"Found {len(files_to_process)} files to process")
            
            for file_path in files_to_process:
                try:
                    category = self.get_file_category(file_path)
                    target_dir = organized_dir / category
                    target_path = target_dir / file_path.name
                    
                    # Handle filename conflicts
                    counter = 1
                    original_name = file_path.name
                    while target_path.exists():
                        if counter > 1000:  # Prevent infinite loops
                            self.logger.error(f"Too many conflicts for {original_name}, skipping")
                            break
                        name_parts = file_path.stem, counter, file_path.suffix
                        target_path = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        counter += 1
                    
                    if dry_run:
                        self.logger.info(f"Would move: {file_path.name} → {category}/{target_path.name}")
                    else:
                        # Verify source file still exists before moving
                        if not file_path.exists():
                            self.logger.warning(f"Source file disappeared: {file_path.name}")
                            continue
                        
                        shutil.move(str(file_path), str(target_path))
                        self.logger.info(f"Moved: {file_path.name} → {category}/{target_path.name}")
                        moved_files += 1
                        
                except PermissionError as e:
                    self.logger.error(f"Permission denied for {file_path.name}: {e}")
                    failed_files += 1
                except OSError as e:
                    self.logger.error(f"OS error moving {file_path.name}: {e}")
                    failed_files += 1
                except Exception as e:
                    self.logger.error(f"Unexpected error moving {file_path.name}: {e}")
                    failed_files += 1
            
            # Summary
            total_files = len(files_to_process)
            if not dry_run:
                self.logger.info(f"Organization complete! Moved {moved_files}/{total_files} files.")
                if failed_files > 0:
                    self.logger.warning(f"{failed_files} files failed to move.")
            else:
                self.logger.info(f"Dry run complete. Would move {moved_files}/{total_files} files.")
            
            return {'moved': moved_files, 'failed': failed_files, 'total': total_files}
            
        except Exception as e:
            self.logger.error(f"Fatal error during organization: {e}")
            raise
    
    def generate_report(self):
        """Generate a report of the current file distribution."""
        if not self.source_dir.exists():
            return "Source directory does not exist!"
        
        file_counts = {}
        total_files = 0
        
        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                category = self.get_file_category(file_path)
                file_counts[category] = file_counts.get(category, 0) + 1
                total_files += 1
        
        report = f"\n📊 File Organization Report for {self.source_dir}\n"
        report += "=" * 50 + "\n"
        report += f"Total files: {total_files}\n\n"
        
        for category, count in sorted(file_counts.items()):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            report += f"{category:12}: {count:3} files ({percentage:.1f}%)\n"
        
        return report


def validate_directory_input(path_input):
    """Validate and normalize directory input."""
    if not path_input:
        return None
    
    path_input = path_input.strip().strip('"').strip("'")  # Remove quotes
    
    # Expand user path (~)
    expanded_path = Path(path_input).expanduser().resolve()
    
    if not expanded_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {expanded_path}")
    
    if not expanded_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {expanded_path}")
    
    return str(expanded_path)


def get_user_choice(prompt, valid_choices):
    """Get validated user choice."""
    while True:
        try:
            choice = input(prompt).strip()
            if choice in valid_choices:
                return choice
            print(f"Invalid choice. Please enter one of: {', '.join(valid_choices)}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.")
            return None


def main():
    """Main function to demonstrate the file organizer."""
    print("🗂️  File Organizer v1.1")
    print("=" * 30)
    
    try:
        # Get source directory from user
        while True:
            source_input = input("Enter directory to organize (or press Enter for Downloads): ").strip()
            
            try:
                source = validate_directory_input(source_input) if source_input else None
                break
            except (FileNotFoundError, NotADirectoryError) as e:
                print(f"❌ Error: {e}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    print("Exiting.")
                    return
        
        # Initialize organizer
        try:
            organizer = FileOrganizer(source)
        except Exception as e:
            print(f"❌ Failed to initialize organizer: {e}")
            return
        
        # Show current state
        try:
            print(organizer.generate_report())
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return
        
        # Ask user what to do
        print("\nOptions:")
        print("1. Preview organization (dry run)")
        print("2. Organize files")
        print("3. Exit")
        
        choice = get_user_choice("\nEnter your choice (1-3): ", ["1", "2", "3"])
        
        if choice is None:  # User cancelled
            return
        
        if choice == "1":
            try:
                result = organizer.organize_files(dry_run=True)
                print(f"\n📊 Summary: {result['moved']} files would be moved, {result['failed']} would fail")
            except Exception as e:
                print(f"❌ Error during dry run: {e}")
                
        elif choice == "2":
            confirm_choice = get_user_choice("Are you sure you want to move files? (yes/no): ", ["yes", "no"])
            if confirm_choice == "yes":
                try:
                    result = organizer.organize_files(dry_run=False)
                    print("\n✅ Organization complete!")
                    print(f"📊 Summary: {result['moved']} files moved, {result['failed']} failed")
                except Exception as e:
                    print(f"❌ Error during organization: {e}")
            else:
                print("Organization cancelled.")
        elif choice == "3":
            print("Goodbye!")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the logs for more details.")


if __name__ == "__main__":
    main()