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
            return
        
        organized_dir = self.create_organized_structure()
        moved_files = 0
        
        self.logger.info(f"Starting file organization in {self.source_dir}")
        self.logger.info(f"Dry run mode: {dry_run}")
        
        for file_path in self.source_dir.iterdir():
            if file_path.is_file() and file_path.name != ".DS_Store":
                category = self.get_file_category(file_path)
                target_dir = organized_dir / category
                target_path = target_dir / file_path.name
                
                # Handle filename conflicts
                counter = 1
                while target_path.exists():
                    name_parts = file_path.stem, counter, file_path.suffix
                    target_path = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                    counter += 1
                
                if dry_run:
                    self.logger.info(f"Would move: {file_path.name} → {category}/{target_path.name}")
                else:
                    try:
                        shutil.move(str(file_path), str(target_path))
                        self.logger.info(f"Moved: {file_path.name} → {category}/{target_path.name}")
                        moved_files += 1
                    except Exception as e:
                        self.logger.error(f"Failed to move {file_path.name}: {e}")
        
        if not dry_run:
            self.logger.info(f"Organization complete! Moved {moved_files} files.")
        else:
            self.logger.info("Dry run complete. Use organize_files(dry_run=False) to actually move files.")
    
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


def main():
    """Main function to demonstrate the file organizer."""
    print("🗂️  File Organizer v1.0")
    print("=" * 30)
    
    # Get source directory from user
    source = input("Enter directory to organize (or press Enter for Downloads): ").strip()
    if not source:
        source = None
    
    organizer = FileOrganizer(source)
    
    # Show current state
    print(organizer.generate_report())
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Preview organization (dry run)")
    print("2. Organize files")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        organizer.organize_files(dry_run=True)
    elif choice == "2":
        confirm = input("Are you sure you want to move files? (yes/no): ").strip().lower()
        if confirm == "yes":
            organizer.organize_files(dry_run=False)
        else:
            print("Organization cancelled.")
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()