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
        
        # Project directory indicators
        self.project_indicators = {
            'package.json', 'package-lock.json', 'yarn.lock',  # Node.js
            'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',  # Python
            'Cargo.toml', 'Cargo.lock',  # Rust
            'pom.xml', 'build.gradle',  # Java
            'composer.json',  # PHP
            'Gemfile', 'Gemfile.lock',  # Ruby
            'go.mod', 'go.sum',  # Go
            'Makefile', 'CMakeLists.txt',  # Build systems
            '.gitignore', '.git',  # Version control
            'README.md', 'LICENSE',  # Project docs
            'docker-compose.yml', 'Dockerfile',  # Docker
            '.env.example', 'config.yaml',  # Config
        }
        
        # Critical files that should never be moved
        self.critical_files = {
            'package.json', 'package-lock.json', 'yarn.lock', 'node_modules',
            'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'Pipfile.lock',
            'Cargo.toml', 'Cargo.lock', 'target',
            'pom.xml', 'build.gradle', 'gradle.properties',
            'composer.json', 'composer.lock', 'vendor',
            'Gemfile', 'Gemfile.lock',
            'go.mod', 'go.sum',
            'Makefile', 'CMakeLists.txt', 'build',
            '.gitignore', '.gitattributes',
            'README.md', 'README.txt', 'LICENSE', 'CHANGELOG.md',
            'docker-compose.yml', 'Dockerfile', '.dockerignore',
            '.env.example', 'config.yaml', 'config.json',
            'tsconfig.json', 'webpack.config.js', 'babel.config.js',
            '.eslintrc.js', '.prettierrc', 'jest.config.js',
            'vite.config.js', 'rollup.config.js',
            '.travis.yml', '.github', '.gitlab-ci.yml',
            'tox.ini', 'pytest.ini', 'setup.cfg',
            '.vscode', '.idea',
        }
    
    def setup_logging(self):
        """Set up logging for the organizer."""
        log_dir = Path(__file__).parent / "fileorg_logs"
        log_dir.mkdir(exist_ok=True, mode=0o700)  # Secure permissions for log directory
        
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
        organized_dir.mkdir(exist_ok=True, mode=0o755)
        
        for category in self.file_types.keys():
            (organized_dir / category).mkdir(exist_ok=True, mode=0o755)
        
        (organized_dir / "Other").mkdir(exist_ok=True, mode=0o755)
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
        
        # Safety check: detect if this looks like a project directory
        safety_issues = self.check_directory_safety()
        if safety_issues:
            self.logger.warning("Safety concerns detected:")
            for issue in safety_issues:
                self.logger.warning(f"  - {issue}")
            if not dry_run:
                self.logger.error("Aborting organization due to safety concerns. Use dry-run to preview.")
                raise ValueError("Directory appears to contain projects or critical files. Aborting for safety.")
        
        try:
            organized_dir = self.create_organized_structure()
            moved_files = 0
            failed_files = 0
            
            self.logger.info(f"Starting file organization in {self.source_dir}")
            self.logger.info(f"Dry run mode: {dry_run}")
            
            # Get list of files first to avoid issues with directory changes
            # Enhanced filtering with comprehensive safety checks
            files_to_process = []
            for f in self.source_dir.iterdir():
                if self.is_safe_to_move(f):
                    files_to_process.append(f)
            
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
                        
                        # Use copy2 + remove for safer operation (preserves metadata)
                        shutil.copy2(str(file_path), str(target_path))
                        file_path.unlink()  # Remove original only after successful copy
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
    
    def organize_selective(self, selected_categories, dry_run=False):
        """Organize only files from selected categories."""
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory does not exist: {self.source_dir}")
        
        try:
            organized_dir = self.create_organized_structure()
            moved_files = 0
            failed_files = 0
            
            self.logger.info(f"Starting selective organization in {self.source_dir}")
            self.logger.info(f"Selected categories: {', '.join(selected_categories)}")
            self.logger.info(f"Dry run mode: {dry_run}")
            
            # Get only files that match selected categories and are safe to move
            files_to_process = []
            for f in self.source_dir.iterdir():
                if self.is_safe_to_move(f):
                    category = self.get_file_category(f)
                    if category in selected_categories or (category == 'Other' and 'Other' in selected_categories):
                        files_to_process.append(f)
            
            if not files_to_process:
                self.logger.info("No files found matching selected categories.")
                return {'moved': 0, 'failed': 0, 'total': 0}
            
            self.logger.info(f"Found {len(files_to_process)} files to process")
            
            for file_path in files_to_process:
                try:
                    category = self.get_file_category(file_path)
                    target_dir = organized_dir / category
                    target_path = target_dir / file_path.name
                    
                    # Handle filename conflicts
                    counter = 1
                    while target_path.exists():
                        if counter > 1000:
                            self.logger.error(f"Too many conflicts for {file_path.name}, skipping")
                            break
                        name_parts = file_path.stem, counter, file_path.suffix
                        target_path = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        counter += 1
                    
                    if dry_run:
                        self.logger.info(f"Would move: {file_path.name} → {category}/{target_path.name}")
                        moved_files += 1
                    else:
                        if not file_path.exists():
                            self.logger.warning(f"Source file disappeared: {file_path.name}")
                            continue
                        
                        shutil.copy2(str(file_path), str(target_path))
                        file_path.unlink()
                        self.logger.info(f"Moved: {file_path.name} → {category}/{target_path.name}")
                        moved_files += 1
                        
                except Exception as e:
                    self.logger.error(f"Error moving {file_path.name}: {e}")
                    failed_files += 1
            
            total_files = len(files_to_process)
            if not dry_run:
                self.logger.info(f"Selective organization complete! Moved {moved_files}/{total_files} files.")
            else:
                self.logger.info(f"Selective dry run complete. Would move {moved_files}/{total_files} files.")
            
            return {'moved': moved_files, 'failed': failed_files, 'total': total_files}
            
        except Exception as e:
            self.logger.error(f"Fatal error during selective organization: {e}")
            raise
    
    def check_directory_safety(self):
        """Check if directory contains projects or critical files that shouldn't be organized."""
        safety_issues = []
        
        # Check for project indicators in current directory
        current_files = set(f.name for f in self.source_dir.iterdir())
        project_files_found = current_files.intersection(self.project_indicators)
        if project_files_found:
            safety_issues.append(f"Project files detected: {', '.join(sorted(project_files_found))}")
        
        # Check for subdirectories that look like projects
        project_dirs = []
        try:
            for item in self.source_dir.iterdir():
                try:
                    if item.is_dir() and not item.name.startswith('.'):
                        subdir_files = set(f.name for f in item.iterdir() if f.is_file())
                        if subdir_files.intersection(self.project_indicators):
                            project_dirs.append(item.name)
                except (PermissionError, OSError):
                    # Skip directories we can't read
                    continue
        except (PermissionError, OSError):
            # Can't read the source directory
            pass
        
        if project_dirs:
            safety_issues.append(f"Project directories detected: {', '.join(project_dirs)}")
        
        # Check for critical files
        critical_found = current_files.intersection(self.critical_files)
        if critical_found:
            safety_issues.append(f"Critical files detected: {', '.join(sorted(critical_found))}")
        
        # Count different file types
        code_files = sum(1 for f in self.source_dir.iterdir() 
                        if f.is_file() and f.suffix.lower() in 
                        ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.ts', '.jsx'])
        
        if code_files > 5:
            safety_issues.append(f"Many code files detected ({code_files} files) - likely a project directory")
        
        return safety_issues
    
    def is_safe_to_move(self, file_path):
        """Determine if a file is safe to move based on comprehensive safety rules."""
        if not file_path.is_file():
            return False
        
        filename = file_path.name
        
        # Skip hidden files
        if filename.startswith('.'):
            return False
        
        # Skip symlinks for security
        if file_path.is_symlink():
            return False
        
        # Skip system files
        if filename in {'Thumbs.db', 'desktop.ini', '.DS_Store'}:
            return False
        
        # Skip critical project files
        if filename in self.critical_files:
            self.logger.info(f"Skipping critical file: {filename}")
            return False
        
        # Skip configuration files (common patterns)
        config_patterns = [
            '.config.', '.conf', '.ini', '.cfg', '.settings',
            'webpack.', 'babel.', 'eslint', 'prettier',
            'jest.', 'vitest.', 'vite.', 'rollup.',
            'tsconfig.', 'jsconfig.',
        ]
        
        if any(pattern in filename.lower() for pattern in config_patterns):
            self.logger.info(f"Skipping configuration file: {filename}")
            return False
        
        # Skip files that look like they belong to a specific project
        # (files with project-specific naming patterns)
        if self.appears_project_specific(file_path):
            self.logger.info(f"Skipping project-specific file: {filename}")
            return False
        
        return True
    
    def appears_project_specific(self, file_path):
        """Check if file appears to be project-specific based on naming and location."""
        filename = file_path.name.lower()
        
        # Check if file is in a subdirectory that looks like a project
        parent_dir = file_path.parent
        if parent_dir != self.source_dir:
            # This file is in a subdirectory - check if it's a project directory
            parent_files = set(f.name for f in parent_dir.iterdir() if f.is_file())
            if parent_files.intersection(self.project_indicators):
                return True
        
        # Files with specific project naming patterns
        project_patterns = [
            'test_', '_test.', 'spec_', '_spec.',  # Test files
            'mock_', '_mock.', 'fixture_',  # Test fixtures
            'migration_', '_migration.',  # Database migrations
            'component_', '_component.',  # UI components
            'service_', '_service.',  # Service files
            'controller_', '_controller.',  # Controller files
            'model_', '_model.',  # Model files
            'util_', '_util.', 'helper_', '_helper.',  # Utility files
        ]
        
        return any(pattern in filename for pattern in project_patterns)
    
    def get_safety_report(self):
        """Generate a safety report for the directory."""
        safety_issues = self.check_directory_safety()
        
        if not safety_issues:
            return "✅ Directory appears safe to organize - no project files or critical dependencies detected."
        
        report = "⚠️  SAFETY WARNINGS DETECTED:\n"
        report += "=" * 40 + "\n"
        for issue in safety_issues:
            report += f"• {issue}\n"
        
        report += "\n🛡️  RECOMMENDATION: Use dry-run mode first to preview changes."
        report += "\n   Consider organizing only specific file types or creating a separate folder."
        
        return report


def validate_directory_input(path_input):
    """Validate and normalize directory input."""
    if not path_input:
        return None
    
    # Security: Sanitize input
    path_input = path_input.strip().strip('"').strip("'")  # Remove quotes
    
    # Prevent path traversal attacks
    if '..' in path_input:
        # Allow absolute paths with .. if they resolve safely
        try:
            test_path = Path(path_input).resolve()
            if not str(test_path).startswith(str(Path.home())):
                raise ValueError("Invalid path: path traversal outside home directory detected")
        except Exception:
            raise ValueError("Invalid path: potential directory traversal detected")
    
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
        
        # Show safety report
        try:
            safety_report = organizer.get_safety_report()
            print("\n" + safety_report)
        except Exception as e:
            print(f"❌ Error generating safety report: {e}")
        
        # Check if there were safety warnings
        safety_issues = organizer.check_directory_safety()
        
        # Ask user what to do
        print("\nOptions:")
        print("1. Preview organization (dry run)")
        if safety_issues:
            print("2. Organize files (⚠️  SAFETY WARNINGS DETECTED - Will be blocked)")
        else:
            print("2. Organize files")
        print("3. Organize only specific file types")
        print("4. Exit")
        
        choice = get_user_choice("\nEnter your choice (1-4): ", ["1", "2", "3", "4"])
        
        if choice is None:  # User cancelled
            return
        
        if choice == "1":
            try:
                result = organizer.organize_files(dry_run=True)
                print(f"\n📊 Summary: {result['moved']} files would be moved, {result['failed']} would fail")
            except Exception as e:
                print(f"❌ Error during dry run: {e}")
                
        elif choice == "2":
            if safety_issues:
                print("\n🚫 Organization blocked due to safety warnings.")
                print("   Use option 1 (dry run) to see what would be moved,")
                print("   or option 3 to organize specific file types only.")
            else:
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
            # Selective organization
            print("\n📋 Available file types:")
            for i, category in enumerate(organizer.file_types.keys(), 1):
                print(f"{i}. {category}")
            
            type_choice = input("\nEnter category numbers to organize (comma-separated, or 'all'): ").strip()
            
            if type_choice.lower() == 'all':
                selected_types = list(organizer.file_types.keys())
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in type_choice.split(',')]
                    categories = list(organizer.file_types.keys())
                    selected_types = [categories[i] for i in indices if 0 <= i < len(categories)]
                except (ValueError, IndexError):
                    print("❌ Invalid selection. Exiting.")
                    return
            
            if selected_types:
                print(f"\n📁 Will organize: {', '.join(selected_types)}")
                confirm = get_user_choice("Proceed with selective organization? (yes/no): ", ["yes", "no"])
                if confirm == "yes":
                    try:
                        result = organizer.organize_selective(selected_types, dry_run=False)
                        print("\n✅ Selective organization complete!")
                        print(f"📊 Summary: {result['moved']} files moved, {result['failed']} failed")
                    except Exception as e:
                        print(f"❌ Error during selective organization: {e}")
                else:
                    print("Organization cancelled.")
            else:
                print("❌ No valid categories selected.")
        elif choice == "4":
            print("Goodbye!")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the logs for more details.")


if __name__ == "__main__":
    main()