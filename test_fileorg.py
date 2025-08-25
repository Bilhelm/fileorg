#!/usr/bin/env python3
"""
Unit tests for File Organizer
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_organizer import FileOrganizer, validate_directory_input, get_user_choice


class TestFileOrganizer(unittest.TestCase):
    """Test cases for File Organizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.organizer = FileOrganizer(str(self.temp_dir))
        
        # Create test files
        self.test_files = {
            'document.pdf': 'Documents',
            'image.jpg': 'Images',
            'video.mp4': 'Videos',
            'music.mp3': 'Audio',
            'archive.zip': 'Archives',
            'script.py': 'Code',
            'data.csv': 'Spreadsheets',
            'presentation.pptx': 'Presentations',
            'unknown.xyz': 'Other'
        }
        
        for filename in self.test_files:
            (self.temp_dir / filename).touch()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_categorization(self):
        """Test that files are categorized correctly."""
        for filename, expected_category in self.test_files.items():
            file_path = self.temp_dir / filename
            actual_category = self.organizer.get_file_category(file_path)
            self.assertEqual(actual_category, expected_category,
                           f"File {filename} should be in {expected_category}, got {actual_category}")
    
    def test_organized_structure_creation(self):
        """Test that organized folder structure is created."""
        organized_dir = self.organizer.create_organized_structure()
        
        # Check that organized directory exists
        self.assertTrue(organized_dir.exists())
        self.assertTrue(organized_dir.is_dir())
        
        # Check all category folders exist
        expected_categories = list(self.organizer.file_types.keys()) + ['Other']
        for category in expected_categories:
            category_dir = organized_dir / category
            self.assertTrue(category_dir.exists(), f"Category folder {category} should exist")
            self.assertTrue(category_dir.is_dir(), f"Category folder {category} should be a directory")
    
    def test_dry_run_mode(self):
        """Test dry run mode doesn't move files."""
        result = self.organizer.organize_files(dry_run=True)
        
        # Files should still be in original location
        current_files = [f for f in self.temp_dir.iterdir() if f.is_file()]
        self.assertEqual(len(current_files), len(self.test_files))
        
        # Check result structure
        self.assertIn('moved', result)
        self.assertIn('failed', result)
        self.assertIn('total', result)
        self.assertEqual(result['total'], len(self.test_files))
    
    def test_actual_file_organization(self):
        """Test that files are actually moved."""
        result = self.organizer.organize_files(dry_run=False)
        
        # Check that files were moved
        self.assertEqual(result['moved'], len(self.test_files))
        self.assertEqual(result['failed'], 0)
        
        # Verify organized structure exists
        organized_dir = self.temp_dir / "Organized"
        self.assertTrue(organized_dir.exists())
        
        # Verify files are in correct categories
        for filename, expected_category in self.test_files.items():
            category_dir = organized_dir / expected_category
            moved_file = category_dir / filename
            self.assertTrue(moved_file.exists(), 
                          f"File {filename} should exist in {expected_category} folder")
    
    def test_filename_conflict_resolution(self):
        """Test handling of filename conflicts."""
        # Create a conflict scenario
        organized_dir = self.organizer.create_organized_structure()
        conflict_file = organized_dir / "Documents" / "document.pdf"
        conflict_file.touch()  # Create existing file
        
        result = self.organizer.organize_files(dry_run=False)
        
        # Should still succeed
        self.assertGreater(result['moved'], 0)
        
        # Check that conflict was resolved with numbered suffix
        expected_renamed = organized_dir / "Documents" / "document_1.pdf"
        self.assertTrue(expected_renamed.exists(), "Conflicting file should be renamed")
    
    def test_empty_directory(self):
        """Test behavior with empty directory."""
        empty_dir = Path(tempfile.mkdtemp())
        try:
            organizer = FileOrganizer(str(empty_dir))
            result = organizer.organize_files(dry_run=False)
            
            self.assertEqual(result['moved'], 0)
            self.assertEqual(result['failed'], 0)
            self.assertEqual(result['total'], 0)
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)
    
    def test_permission_errors(self):
        """Test handling of permission errors."""
        # Create a read-only directory
        readonly_dir = Path(tempfile.mkdtemp())
        test_file = readonly_dir / "test.txt"
        test_file.touch()
        
        try:
            # Make directory read-only
            os.chmod(readonly_dir, 0o444)
            
            organizer = FileOrganizer(str(readonly_dir))
            
            # Should raise PermissionError for actual organization
            with self.assertRaises(PermissionError):
                organizer.organize_files(dry_run=False)
                
            # But dry run should work
            result = organizer.organize_files(dry_run=True)
            self.assertEqual(result['total'], 1)
            
        finally:
            # Restore permissions and cleanup
            os.chmod(readonly_dir, 0o644)
            shutil.rmtree(readonly_dir, ignore_errors=True)
    
    def test_nonexistent_directory(self):
        """Test behavior with non-existent directory."""
        fake_dir = "/path/that/does/not/exist"
        
        # Should not raise error on init, but on organize_files call
        organizer = FileOrganizer(fake_dir)
        with self.assertRaises(FileNotFoundError):
            organizer.organize_files(dry_run=False)
    
    def test_file_report_generation(self):
        """Test report generation."""
        report = self.organizer.generate_report()
        
        self.assertIn("File Organization Report", report)
        self.assertIn(f"Total files: {len(self.test_files)}", report)
        
        # Should contain category counts
        for category in set(self.test_files.values()):
            self.assertIn(category, report)
    
    def test_special_files_ignored(self):
        """Test that special files are ignored."""
        # Create special files
        (self.temp_dir / ".DS_Store").touch()
        (self.temp_dir / "Thumbs.db").touch()
        (self.temp_dir / ".gitignore").touch()
        
        result = self.organizer.organize_files(dry_run=True)
        
        # Should only process our test files, not special files
        self.assertEqual(result['total'], len(self.test_files))


class TestInputValidation(unittest.TestCase):
    """Test input validation functions."""
    
    def test_validate_directory_input_valid(self):
        """Test validation with valid directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = validate_directory_input(temp_dir)
            self.assertEqual(Path(result).resolve(), Path(temp_dir).resolve())
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_validate_directory_input_empty(self):
        """Test validation with empty input."""
        self.assertIsNone(validate_directory_input(""))
    
    def test_validate_directory_input_nonexistent(self):
        """Test validation with non-existent path."""
        with self.assertRaises(FileNotFoundError):
            validate_directory_input("/path/that/does/not/exist")
    
    def test_validate_directory_input_file(self):
        """Test validation when path is a file, not directory."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            with self.assertRaises(NotADirectoryError):
                validate_directory_input(temp_file.name)
        finally:
            os.unlink(temp_file.name)
    
    def test_validate_directory_input_quotes(self):
        """Test validation handles quoted paths."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Test with various quote combinations
            for quoted_path in [f'"{temp_dir}"', f"'{temp_dir}'", f" '{temp_dir}' "]:
                result = validate_directory_input(quoted_path)
                self.assertEqual(Path(result).resolve(), Path(temp_dir).resolve())
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @patch('builtins.input', side_effect=['2', '1'])
    def test_get_user_choice_valid(self, mock_input):
        """Test get_user_choice with valid input."""
        result = get_user_choice("Choose: ", ['1', '2', '3'])
        self.assertEqual(result, '2')
    
    @patch('builtins.input', side_effect=['invalid', '4', '2'])
    def test_get_user_choice_retry(self, mock_input):
        """Test get_user_choice retries invalid input."""
        result = get_user_choice("Choose: ", ['1', '2', '3'])
        self.assertEqual(result, '2')
    
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_get_user_choice_keyboard_interrupt(self, mock_input):
        """Test get_user_choice handles keyboard interrupt."""
        result = get_user_choice("Choose: ", ['1', '2', '3'])
        self.assertIsNone(result)


class TestFileOrganizerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_disappears_during_processing(self):
        """Test handling when file disappears during processing."""
        organizer = FileOrganizer(str(self.temp_dir))
        
        # Create a file
        test_file = self.temp_dir / "test.txt"
        test_file.touch()
        
        # Mock the file to disappear during processing
        with patch.object(Path, 'exists') as mock_exists:
            # File exists during initial scan, disappears during processing
            mock_exists.side_effect = lambda: False if 'test.txt' in str(mock_exists.call_args) else True
            
            result = organizer.organize_files(dry_run=False)
            # Should handle gracefully
            self.assertIsInstance(result, dict)
    
    def test_infinite_conflict_prevention(self):
        """Test prevention of infinite loops in conflict resolution."""
        organizer = FileOrganizer(str(self.temp_dir))
        
        # Create test file
        test_file = self.temp_dir / "test.txt"
        test_file.touch()
        
        # Create organized structure with many conflicts
        organized_dir = organizer.create_organized_structure()
        other_dir = organized_dir / "Other"
        
        # Create many conflicting files
        for i in range(1005):  # More than the 1000 limit
            conflict_file = other_dir / f"test_{i}.txt" if i > 0 else other_dir / "test.txt"
            conflict_file.touch()
        
        # Should handle this gracefully without infinite loop
        result = organizer.organize_files(dry_run=False)
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)