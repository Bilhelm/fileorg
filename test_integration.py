#!/usr/bin/env python3
"""
Integration tests for File Organizer
Tests real-world scenarios and security edge cases
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import os
import sys
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from file_organizer import FileOrganizer, validate_directory_input


class TestSecurityAndEdgeCases(unittest.TestCase):
    """Test security vulnerabilities and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_symlink_security(self):
        """Test that symlinks are not followed (security)."""
        # Create a symlink that points outside the directory
        target_dir = Path(tempfile.mkdtemp())
        sensitive_file = target_dir / "sensitive.txt"
        sensitive_file.write_text("sensitive data")
        
        try:
            # Create symlink in our test directory
            symlink = self.temp_dir / "link_to_sensitive.txt"
            symlink.symlink_to(sensitive_file)
            
            # Create regular file
            regular_file = self.temp_dir / "regular.pdf"
            regular_file.touch()
            
            organizer = FileOrganizer(str(self.temp_dir))
            result = organizer.organize_files(dry_run=False)
            
            # Should only move the regular file, not the symlink
            self.assertEqual(result['moved'], 1)
            self.assertTrue(symlink.exists(), "Symlink should not be moved")
            
        finally:
            shutil.rmtree(target_dir, ignore_errors=True)
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        # Try various path traversal patterns
        dangerous_paths = [
            "../../../etc/passwd",
            "~/../../sensitive",
            "/etc/../etc/passwd",
        ]
        
        for dangerous_path in dangerous_paths:
            with self.subTest(path=dangerous_path):
                # Should either raise an error or resolve safely
                try:
                    result = validate_directory_input(dangerous_path)
                    if result:
                        # If it returns a result, it should be safely resolved
                        self.assertNotIn("..", result)
                except (ValueError, FileNotFoundError, NotADirectoryError):
                    # Expected to raise an error for invalid paths
                    pass
    
    def test_hidden_file_protection(self):
        """Test that hidden files are not moved."""
        # Create various hidden and system files
        hidden_files = [
            ".ssh_key",
            ".git",
            ".env",
            ".gitignore",
            ".DS_Store"
        ]
        
        for filename in hidden_files:
            (self.temp_dir / filename).touch()
        
        # Create regular file
        regular_file = self.temp_dir / "document.pdf"
        regular_file.touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        
        # Use selective organization since .gitignore makes it look like a project
        result = organizer.organize_selective(["Documents"], dry_run=False)
        
        # Should only move the regular file
        self.assertEqual(result['moved'], 1)
        
        # All hidden files should remain
        for filename in hidden_files:
            self.assertTrue((self.temp_dir / filename).exists(), 
                          f"Hidden file {filename} should not be moved")
    
    def test_large_filename_handling(self):
        """Test handling of extremely long filenames."""
        # Create file with very long name (near filesystem limit)
        long_name = "a" * 200 + ".pdf"
        long_file = self.temp_dir / long_name
        long_file.touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        result = organizer.organize_files(dry_run=False)
        
        # Should handle gracefully
        self.assertEqual(result['moved'], 1)
    
    def test_special_characters_in_filenames(self):
        """Test handling of special characters in filenames."""
        special_files = [
            "file with spaces.pdf",
            "file'with'quotes.txt",
            "file\"with\"doublequotes.doc",
            "file&with&ampersand.jpg",
            "file|with|pipe.mp3",
            "file;with;semicolon.zip"
        ]
        
        for filename in special_files:
            try:
                (self.temp_dir / filename).touch()
            except OSError:
                # Some characters might not be allowed on certain filesystems
                continue
        
        organizer = FileOrganizer(str(self.temp_dir))
        result = organizer.organize_files(dry_run=False)
        
        # Should handle all created files
        self.assertGreater(result['moved'], 0)
        self.assertEqual(result['failed'], 0)
    
    def test_concurrent_file_operations(self):
        """Test behavior when files are modified during organization."""
        # Create initial files
        files = []
        for i in range(10):
            f = self.temp_dir / f"file_{i}.pdf"
            f.touch()
            files.append(f)
        
        organizer = FileOrganizer(str(self.temp_dir))
        
        # Start organization in dry-run to test
        result = organizer.organize_files(dry_run=True)
        
        # Delete some files to simulate concurrent modification
        for f in files[:3]:
            f.unlink()
        
        # Actual run should handle missing files gracefully
        result = organizer.organize_files(dry_run=False)
        
        # Should successfully move remaining files
        self.assertGreater(result['moved'], 0)
    
    def test_directory_permissions(self):
        """Test that created directories have appropriate permissions."""
        organizer = FileOrganizer(str(self.temp_dir))
        organized_dir = organizer.create_organized_structure()
        
        # Check permissions of created directories
        for category_dir in organized_dir.iterdir():
            if category_dir.is_dir():
                stat_info = category_dir.stat()
                mode = stat_info.st_mode & 0o777
                
                # Should have reasonable permissions (755 or more restrictive)
                self.assertLessEqual(mode, 0o755, 
                    f"Directory {category_dir.name} has overly permissive permissions: {oct(mode)}")
    
    def test_log_directory_security(self):
        """Test that log directory has secure permissions."""
        log_dir = Path(__file__).parent / "fileorg_logs"
        
        # If log directory exists, check its permissions
        if log_dir.exists():
            stat_info = log_dir.stat()
            mode = stat_info.st_mode & 0o777
            
            # Log directory should be readable only by owner (700)
            self.assertLessEqual(mode, 0o700, 
                f"Log directory has overly permissive permissions: {oct(mode)}")


class TestPerformanceAndStress(unittest.TestCase):
    """Test performance with large numbers of files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_many_files(self):
        """Test handling of many files (stress test)."""
        # Create 100 files of various types
        extensions = ['.pdf', '.jpg', '.mp3', '.zip', '.txt', '.py', '.csv', '.pptx', '.xyz']
        
        for i in range(100):
            ext = extensions[i % len(extensions)]
            (self.temp_dir / f"file_{i}{ext}").touch()
        
        organizer = FileOrganizer(str(self.temp_dir))
        
        # Check if it's detected as having many code files (safety feature)
        safety_issues = organizer.check_directory_safety()
        
        start_time = time.time()
        if safety_issues:
            # Use selective organization for safety
            all_categories = list(organizer.file_types.keys()) + ["Other"]
            result = organizer.organize_selective(all_categories, dry_run=False)
        else:
            result = organizer.organize_files(dry_run=False)
        elapsed_time = time.time() - start_time
        
        # Should complete successfully
        self.assertEqual(result['moved'], 100)
        self.assertEqual(result['failed'], 0)
        
        # Should complete in reasonable time (< 10 seconds for 100 files)
        self.assertLess(elapsed_time, 10, 
            f"Organization took too long: {elapsed_time:.2f} seconds")
    
    def test_duplicate_filename_stress(self):
        """Test handling of many duplicate filenames."""
        # Create 50 files with the same name
        for i in range(50):
            (self.temp_dir / f"temp_{i}.pdf").touch()
        
        # First organization
        organizer = FileOrganizer(str(self.temp_dir))
        result1 = organizer.organize_files(dry_run=False)
        
        # Create 50 more files with same names
        for i in range(50):
            (self.temp_dir / f"temp_{i}.pdf").touch()
        
        # Second organization should handle conflicts
        result2 = organizer.organize_files(dry_run=False)
        
        # All files should be moved with proper renaming
        self.assertEqual(result1['moved'] + result2['moved'], 100)
        
        # Check that files were renamed properly
        organized_dir = self.temp_dir / "Organized" / "Documents"
        pdf_files = list(organized_dir.glob("*.pdf"))
        self.assertEqual(len(pdf_files), 100)


class TestCLIIntegration(unittest.TestCase):
    """Test command-line interface integration."""
    
    def test_script_execution(self):
        """Test that the script can be executed directly."""
        result = subprocess.run(
            [sys.executable, "file_organizer.py"],
            input="3\n",  # Choose exit option
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertEqual(result.returncode, 0, f"Script failed with output: {result.stderr}")
        self.assertIn("File Organizer", result.stdout)
    
    def test_help_output(self):
        """Test that script provides help information."""
        # Run with invalid input to see options
        result = subprocess.run(
            [sys.executable, "file_organizer.py"],
            input="\n3\n",  # Use default directory, then exit
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertIn("Options:", result.stdout)
        self.assertIn("Preview organization", result.stdout)
        self.assertIn("Organize files", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)