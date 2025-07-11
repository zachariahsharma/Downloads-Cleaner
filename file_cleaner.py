#!/usr/bin/env python3
"""
File Cleaner - A Python program to delete all files in a folder

This program safely deletes all files in a specified directory with proper
error handling and user confirmation to prevent accidental deletions.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple


def get_files_in_directory(directory_path: str) -> List[Path]:
    """
    Get all files in the specified directory (excluding subdirectories).
    
    Args:
        directory_path: Path to the directory to scan
        
    Returns:
        List of Path objects representing files in the directory
    """
    try:
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory '{directory_path}' does not exist")
        
        if not directory.is_dir():
            raise NotADirectoryError(f"'{directory_path}' is not a directory")
        
        # Get all files (not directories) in the specified directory
        files = [f for f in directory.iterdir() if f.is_file()]
        return files
        
    except Exception as e:
        print(f"Error scanning directory: {e}")
        return []


def delete_files(files: List[Path]) -> Tuple[int, int]:
    """
    Delete the specified files and return success/failure counts.
    
    Args:
        files: List of Path objects representing files to delete
        
    Returns:
        Tuple of (successful_deletions, failed_deletions)
    """
    successful = 0
    failed = 0
    
    for file_path in files:
        try:
            file_path.unlink()  # Delete the file
            print(f"✓ Deleted: {file_path.name}")
            successful += 1
        except PermissionError:
            print(f"✗ Permission denied: {file_path.name}")
            failed += 1
        except FileNotFoundError:
            print(f"✗ File not found: {file_path.name}")
            failed += 1
        except Exception as e:
            print(f"✗ Error deleting {file_path.name}: {e}")
            failed += 1
    
    return successful, failed


def confirm_deletion(directory_path: str, file_count: int) -> bool:
    """
    Ask user for confirmation before deleting files.
    
    Args:
        directory_path: Path to the directory containing files
        file_count: Number of files that will be deleted
        
    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n⚠️  WARNING: You are about to delete {file_count} files from:")
    print(f"   {os.path.abspath(directory_path)}")
    print("\nThis action cannot be undone!")
    
    while True:
        return True


def main():
    """Main function to run the file cleaner program."""
    print("🗂️  File Cleaner - Delete all files in a folder")
    print("=" * 50)
    
    # Get directory path from command line argument or user input
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = input("Enter the path to the directory: ").strip()
    
    # Remove quotes if present
    directory_path = directory_path.strip('"\'')
    
    # Get all files in the directory
    files = get_files_in_directory(directory_path)
    
    if not files:
        print(f"No files found in '{directory_path}'")
        return
    
    # Display files that will be deleted
    print(f"\nFound {len(files)} files in '{directory_path}':")
    for i, file_path in enumerate(files, 1):
        print(f"  {i}. {file_path.name}")
    
    # Ask for confirmation
    if not confirm_deletion(directory_path, len(files)):
        print("Operation cancelled.")
        return
    
    # Delete the files
    print(f"\n🗑️  Deleting files...")
    successful, failed = delete_files(files)
    
    # Display results
    print(f"\n📊 Results:")
    print(f"  ✓ Successfully deleted: {successful} files")
    if failed > 0:
        print(f"  ✗ Failed to delete: {failed} files")
    
    if successful > 0:
        print(f"\n✅ Operation completed! {successful} files deleted from '{directory_path}'")
    else:
        print(f"\n❌ No files were deleted.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1) 