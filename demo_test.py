#!/usr/bin/env python3
"""
Demo test to show safety features in action
"""

import tempfile
from pathlib import Path
import shutil
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from file_organizer import FileOrganizer

def demo_unsafe_directory():
    """Demonstrate safety checks on a directory that looks like a project."""
    print("🧪 DEMO: Testing unsafe directory (simulated project directory)")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create a directory that looks like a project
        (temp_dir / "package.json").write_text('{"name": "my-project"}')
        (temp_dir / "app.js").write_text('console.log("Hello World");')
        (temp_dir / "README.md").write_text("# My Project")
        (temp_dir / ".gitignore").write_text("node_modules/\n*.log")
        (temp_dir / "config.json").write_text('{"port": 3000}')
        
        # Also add some "safe" files that user might want to organize
        (temp_dir / "vacation_photo.jpg").touch()
        (temp_dir / "important_doc.pdf").touch()
        (temp_dir / "backup.zip").touch()
        
        print(f"📁 Created test directory: {temp_dir}")
        print("📋 Files created:")
        for f in sorted(temp_dir.iterdir()):
            print(f"   - {f.name}")
        
        organizer = FileOrganizer(str(temp_dir))
        
        # Show safety report
        print("\n🛡️ SAFETY REPORT:")
        safety_report = organizer.get_safety_report()
        print(safety_report)
        
        # Show what would be moved in dry-run
        print("\n👀 DRY RUN PREVIEW:")
        try:
            result = organizer.organize_files(dry_run=True)
            print(f"   ✅ Would move {result['moved']} files safely")
            print(f"   ❌ {result['failed']} files would fail")
        except Exception as e:
            print(f"   🚫 Dry run blocked: {e}")
        
        # Try actual organization (should be blocked)
        print("\n🚨 ATTEMPTING ACTUAL ORGANIZATION:")
        try:
            organizer.organize_files(dry_run=False)
            print("   ❌ UNEXPECTED: Organization proceeded (this shouldn't happen!)")
        except ValueError as e:
            print(f"   ✅ BLOCKED as expected: {e}")
        
        # Test selective organization
        print("\n🎯 TESTING SELECTIVE ORGANIZATION:")
        try:
            result = organizer.organize_selective(["Images", "Documents", "Archives"], dry_run=False)
            print("   ✅ Selective organization succeeded!")
            print(f"   📊 Moved {result['moved']} files, {result['failed']} failed")
            
            # Show what was actually moved
            organized_dir = temp_dir / "Organized"
            if organized_dir.exists():
                print("   📁 Files successfully organized:")
                for category_dir in organized_dir.iterdir():
                    if category_dir.is_dir():
                        files = list(category_dir.iterdir())
                        if files:
                            print(f"      {category_dir.name}: {[f.name for f in files]}")
        except Exception as e:
            print(f"   ❌ Selective organization failed: {e}")
        
        print("\n✅ Demo completed successfully! Safety features working.")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def demo_safe_directory():
    """Demonstrate normal operation on a safe directory."""
    print("\n🧪 DEMO: Testing safe directory (regular downloads folder)")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create a safe directory with only media/document files
        files = [
            "vacation_hawaii.jpg", "family_reunion.png", "sunset.gif",
            "report_2023.pdf", "invoice_march.docx", "notes.txt",
            "song_favorite.mp3", "podcast_episode.wav",
            "movie_trailer.mp4", "presentation.pptx",
            "data_backup.zip", "photos_archive.tar.gz"
        ]
        
        for filename in files:
            (temp_dir / filename).touch()
        
        print(f"📁 Created safe test directory: {temp_dir}")
        print("📋 Files created:")
        for f in sorted(temp_dir.iterdir()):
            print(f"   - {f.name}")
        
        organizer = FileOrganizer(str(temp_dir))
        
        # Show safety report
        print("\n🛡️ SAFETY REPORT:")
        safety_report = organizer.get_safety_report()
        print(safety_report)
        
        # Organize files
        print("\n📦 ORGANIZING FILES:")
        result = organizer.organize_files(dry_run=False)
        print("   ✅ Organization completed successfully!")
        print(f"   📊 Moved {result['moved']} files, {result['failed']} failed")
        
        # Show organized structure
        organized_dir = temp_dir / "Organized"
        print("\n📁 ORGANIZED STRUCTURE:")
        for category_dir in sorted(organized_dir.iterdir()):
            if category_dir.is_dir():
                files = sorted(f.name for f in category_dir.iterdir())
                if files:
                    print(f"   {category_dir.name}:")
                    for file in files:
                        print(f"      - {file}")
        
        print("\n✅ Safe directory demo completed successfully!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("🔒 FILE ORGANIZER SAFETY FEATURES DEMONSTRATION")
    print("=" * 60)
    print("This demo shows how the enhanced safety features protect your projects")
    print("while still allowing safe file organization.\n")
    
    demo_unsafe_directory()
    demo_safe_directory()
    
    print("\n🎉 ALL DEMOS COMPLETED!")
    print("The File Organizer is now much safer for use on any directory!")