#!/usr/bin/env python3
"""
Safety tests for File Organizer
Tests the new project detection and safety features
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from file_organizer import FileOrganizer


class TestProjectDetection(unittest.TestCase):
    """Test project directory detection and safety features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_nodejs_project_detection(self):
        """Test detection of Node.js projects."""
        # Create a Node.js project structure
        (self.temp_dir / "package.json").write_text('{"name": "test-project"}')
        (self.temp_dir / "app.js").touch()
        (self.temp_dir / "README.md").touch()
        (self.temp_dir / "random.pdf").touch()  # Safe file
        
        organizer = FileOrganizer(str(self.temp_dir))
        safety_issues = organizer.check_directory_safety()
        
        # Should detect project files
        self.assertTrue(len(safety_issues) > 0)
        self.assertTrue(any("package.json" in issue for issue in safety_issues))
        
        # Should prevent organization
        with self.assertRaises(ValueError):
            organizer.organize_files(dry_run=False)
        
        # But dry run should work
        result = organizer.organize_files(dry_run=True)
        self.assertIsInstance(result, dict)
    
    def test_python_project_detection(self):
        """Test detection of Python projects."""
        # Create a Python project structure
        (self.temp_dir / "requirements.txt").write_text("flask==2.0.1")
        (self.temp_dir / "main.py").touch()
        (self.temp_dir / "setup.py").touch()
        (self.temp_dir / "random.jpg").touch()  # Safe file
        
        organizer = FileOrganizer(str(self.temp_dir))
        safety_issues = organizer.check_directory_safety()
        
        # Should detect project files
        self.assertTrue(len(safety_issues) > 0)
        self.assertTrue(any("requirements.txt" in issue for issue in safety_issues))
        
    def test_git_repository_detection(self):
        """Test detection of Git repositories."""
        # Create a Git repo structure
        git_dir = self.temp_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").touch()
        (self.temp_dir / ".gitignore").write_text("*.pyc\n")
        (self.temp_dir / "README.md").touch()
        (self.temp_dir / "document.pdf").touch()  # Safe file
        
        organizer = FileOrganizer(str(self.temp_dir))
        safety_issues = organizer.check_directory_safety()
        
        # Should detect project files
        self.assertTrue(len(safety_issues) > 0)
        self.assertTrue(any(".gitignore" in issue or "README.md" in issue for issue in safety_issues))
    
    def test_multiple_projects_subdirectories(self):
        """Test detection of project subdirectories."""
        # Create project subdirectories
        project1 = self.temp_dir / "project1"
        project1.mkdir()
        (project1 / "package.json").write_text('{"name": "project1"}')
        (project1 / "app.js").touch()
        
        project2 = self.temp_dir / "project2"
        project2.mkdir()
        (project2 / "requirements.txt").write_text("flask==2.0.1")
        (project2 / "main.py").touch()
        
        # Add some safe files in root
        (self.temp_dir / "photo.jpg").touch()
        (self.temp_dir / "document.pdf").touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        safety_issues = organizer.check_directory_safety()
        
        # Should detect project directories
        self.assertTrue(len(safety_issues) > 0)
        self.assertTrue(any("project1" in issue or "project2" in issue for issue in safety_issues))
    
    def test_safe_directory(self):
        """Test that truly safe directories are not flagged."""
        # Create only safe files
        safe_files = [
            "vacation_photo.jpg",
            "important_document.pdf",
            "music_file.mp3",
            "backup.zip",
            "presentation.pptx",
            "random_file.xyz"
        ]
        
        for filename in safe_files:
            (self.temp_dir / filename).touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        safety_issues = organizer.check_directory_safety()
        
        # Should be safe
        self.assertEqual(len(safety_issues), 0)
        
        # Should allow organization
        result = organizer.organize_files(dry_run=False)
        self.assertEqual(result['moved'], len(safe_files))
        self.assertEqual(result['failed'], 0)
    
    def test_many_code_files_detection(self):
        """Test detection of directories with many code files."""
        # Create many code files (indicating a project)
        for i in range(10):
            (self.temp_dir / f"module{i}.py").touch()
        
        # Add a regular file
        (self.temp_dir / "document.pdf").touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        safety_issues = organizer.check_directory_safety()
        
        # Should detect many code files
        self.assertTrue(len(safety_issues) > 0)
        self.assertTrue(any("code files" in issue.lower() for issue in safety_issues))
    
    def test_critical_file_skipping(self):
        """Test that critical files are skipped."""
        critical_files = [
            "package.json", "requirements.txt", "Makefile",
            "docker-compose.yml", "README.md", ".gitignore"
        ]
        
        for filename in critical_files:
            (self.temp_dir / filename).touch()
        
        # Add some safe files
        (self.temp_dir / "photo.jpg").touch()
        (self.temp_dir / "document.pdf").touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        
        # Check which files would be moved
        safe_files = []
        for f in self.temp_dir.iterdir():
            if organizer.is_safe_to_move(f):
                safe_files.append(f.name)
        
        # Should only include the safe files
        expected_safe = {"photo.jpg", "document.pdf"}
        actual_safe = set(safe_files)
        self.assertEqual(actual_safe, expected_safe)
        
        # Critical files should not be in the safe list
        for critical_file in critical_files:
            self.assertNotIn(critical_file, actual_safe)
    
    def test_config_file_patterns(self):
        """Test that configuration files with common patterns are skipped."""
        config_files = [
            "webpack.config.js", "babel.config.js", ".eslintrc.js",
            "jest.config.js", "vite.config.js", "app.config.json",
            "database.conf", "server.ini", "app.settings"
        ]
        
        for filename in config_files:
            (self.temp_dir / filename).touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        
        # None of these should be considered safe to move
        for config_file in config_files:
            file_path = self.temp_dir / config_file
            self.assertFalse(organizer.is_safe_to_move(file_path), 
                           f"Config file {config_file} should not be safe to move")
    
    def test_project_specific_naming_patterns(self):
        """Test detection of project-specific file naming patterns."""
        project_files = [
            "test_user_model.py", "user_service.js", "auth_controller.py",
            "migration_001.sql", "component_header.tsx", "util_helpers.js",
            "mock_data.json", "fixture_users.py", "spec_auth.js"
        ]
        
        for filename in project_files:
            (self.temp_dir / filename).touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        
        # None of these should be considered safe to move
        for project_file in project_files:
            file_path = self.temp_dir / project_file
            self.assertFalse(organizer.is_safe_to_move(file_path), 
                           f"Project-specific file {project_file} should not be safe to move")


class TestSelectiveOrganization(unittest.TestCase):
    """Test selective organization feature."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_selective_organization(self):
        """Test organizing only specific file types."""
        # Create mixed files
        files = {
            "photo.jpg": "Images",
            "document.pdf": "Documents", 
            "music.mp3": "Audio",
            "video.mp4": "Videos",
            "archive.zip": "Archives"
        }
        
        for filename in files:
            (self.temp_dir / filename).touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        
        # Organize only Images and Documents
        result = organizer.organize_selective(["Images", "Documents"], dry_run=False)
        
        # Should move only 2 files
        self.assertEqual(result['moved'], 2)
        self.assertEqual(result['failed'], 0)
        
        # Check files are in correct places
        organized_dir = self.temp_dir / "Organized"
        self.assertTrue((organized_dir / "Images" / "photo.jpg").exists())
        self.assertTrue((organized_dir / "Documents" / "document.pdf").exists())
        
        # Other files should remain in root
        self.assertTrue((self.temp_dir / "music.mp3").exists())
        self.assertTrue((self.temp_dir / "video.mp4").exists())
        self.assertTrue((self.temp_dir / "archive.zip").exists())
    
    def test_selective_with_safety_checks(self):
        """Test that selective organization still respects safety checks."""
        # Create files including critical ones
        (self.temp_dir / "photo.jpg").touch()  # Safe
        (self.temp_dir / "package.json").touch()  # Critical - should be skipped
        (self.temp_dir / "README.md").touch()  # Critical - should be skipped
        
        organizer = FileOrganizer(str(self.temp_dir))
        
        # Try to organize Documents (which would include README.md)
        result = organizer.organize_selective(["Images", "Documents"], dry_run=False)
        
        # Should only move the safe image file
        self.assertEqual(result['moved'], 1)
        self.assertEqual(result['failed'], 0)
        
        # Critical files should remain
        self.assertTrue((self.temp_dir / "package.json").exists())
        self.assertTrue((self.temp_dir / "README.md").exists())


class TestSafetyReporting(unittest.TestCase):
    """Test safety reporting features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_safety_report_safe_directory(self):
        """Test safety report for a safe directory."""
        (self.temp_dir / "photo.jpg").touch()
        (self.temp_dir / "document.pdf").touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        report = organizer.get_safety_report()
        
        self.assertIn("appears safe", report)
        self.assertIn("✅", report)
    
    def test_safety_report_risky_directory(self):
        """Test safety report for a risky directory."""
        (self.temp_dir / "package.json").touch()
        (self.temp_dir / "app.js").touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        report = organizer.get_safety_report()
        
        self.assertIn("SAFETY WARNINGS", report)
        self.assertIn("⚠️", report)
        self.assertIn("package.json", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)