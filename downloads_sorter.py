#!/usr/bin/env python3
"""
Downloads Sorter - Automatically sorts files in Downloads folder

This program monitors the Downloads folder and automatically moves new files
into appropriate subdirectories based on their file extensions:
- Images: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp, .svg
- Zip files: .zip, .rar, .7z, .tar, .gz, .bz2
- STEP files: .step, .stp
- PDFs: .pdf
"""

import os
import sys
import time
import shutil
from pathlib import Path
from typing import Dict, List, Set
import logging
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('downloads_sorter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DownloadsSorter:
    """Class to handle automatic sorting of files in Downloads folder."""
    
    def __init__(self, downloads_path: str | None = None):
        """
        Initialize the DownloadsSorter.
        
        Args:
            downloads_path: Path to Downloads folder (defaults to system Downloads)
        """
        if downloads_path:
            self.downloads_path = Path(downloads_path)
        else:
            # Get system Downloads folder
            self.downloads_path = Path.home() / "Downloads"
        
        # Define file categories and their extensions
        self.categories = {
            "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico", ".heic"},
            "Zip_Files": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".lzma", ".cab", ".iso"},
            "STEP_Files": {".step", ".stp", ".stl", ".obj", ".3ds", ".dae", ".fbx"},
            "3MF_Files": {".3mf"},
            "PDFs": {".pdf"}
        }
        
        # Track existing files to avoid processing them again
        self.existing_files: Set[str] = set()
        
        # Create category directories if they don't exist
        self._create_category_directories()
    
    def _create_category_directories(self):
        """Create category subdirectories in Downloads folder."""
        for category in self.categories.keys():
            category_path = self.downloads_path / category
            if not category_path.exists():
                category_path.mkdir(exist_ok=True)
                logger.info(f"Created directory: {category_path}")
        
        # Create Rogue_Folders directory
        rogue_path = self.downloads_path / "Rogue_Folders"
        if not rogue_path.exists():
            rogue_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {rogue_path}")
        
        # Create Others directory
        others_path = self.downloads_path / "Others"
        if not others_path.exists():
            others_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {others_path}")
    
    def _get_file_category(self, file_path: Path) -> str:
        """
        Determine the category of a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Category name or "Other" if no category matches
        """
        extension = file_path.suffix.lower()
        
        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        
        return "Other"
    
    def _move_file(self, file_path: Path, category: str) -> bool:
        """
        Move a file to its appropriate category directory.
        
        Args:
            file_path: Path to the file to move
            category: Category directory name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category == "Other":
                # Move files that don't match any category to Others folder
                category_path = self.downloads_path / "Others"
                destination = category_path / file_path.name
                
                # Handle filename conflicts
                counter = 1
                original_name = file_path.stem
                original_ext = file_path.suffix
                
                while destination.exists():
                    new_name = f"{original_name}_{counter}{original_ext}"
                    destination = category_path / new_name
                    counter += 1
                
                # Move the file
                shutil.move(str(file_path), str(destination))
                logger.info(f"Moved {file_path.name} to Others/")
                return True
            
            category_path = self.downloads_path / category
            destination = category_path / file_path.name
            
            # Handle filename conflicts
            counter = 1
            original_name = file_path.stem
            original_ext = file_path.suffix
            
            while destination.exists():
                new_name = f"{original_name}_{counter}{original_ext}"
                destination = category_path / new_name
                counter += 1
            
            # Move the file
            shutil.move(str(file_path), str(destination))
            logger.info(f"Moved {file_path.name} to {category}/")
            return True
            
        except Exception as e:
            logger.error(f"Error moving {file_path.name}: {e}")
            return False
    
    def _move_folder_to_rogue(self, folder_path: Path) -> bool:
        """
        Move a folder to the Rogue_Folders directory.
        
        Args:
            folder_path: Path to the folder to move
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rogue_path = self.downloads_path / "Rogue_Folders"
            destination = rogue_path / folder_path.name
            
            # Handle folder name conflicts
            counter = 1
            original_name = folder_path.name
            
            while destination.exists():
                new_name = f"{original_name}_{counter}"
                destination = rogue_path / new_name
                counter += 1
            
            # Move the folder
            shutil.move(str(folder_path), str(destination))
            logger.info(f"Moved folder {folder_path.name} to Rogue_Folders/")
            return True
            
        except Exception as e:
            logger.error(f"Error moving folder {folder_path.name}: {e}")
            return False
    
    def _cleanup_redundant_zips(self):
        """
        Check Zip_Files folder for zip files that have corresponding extracted folders
        and delete the zip files if the folders exist.
        """
        zip_folder = self.downloads_path / "Zip_Files"
        if not zip_folder.exists():
            return
        
        try:
            for item in zip_folder.iterdir():
                if item.is_file() and item.suffix.lower() in {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".lzma", ".cab", ".iso"}:
                    # Get the name without extension
                    zip_name_without_ext = item.stem
                    
                    # Check if there's a folder with the same name
                    corresponding_folder = zip_folder / zip_name_without_ext
                    if corresponding_folder.exists() and corresponding_folder.is_dir():
                        # Delete the zip file since we have the extracted folder
                        item.unlink()
                        logger.info(f"Deleted redundant zip file: {item.name} (folder exists)")
                        
        except Exception as e:
            logger.error(f"Error during zip cleanup: {e}")
    
    def _scan_and_sort_existing_files(self):
        """Scan Downloads folder and sort any existing files and folders."""
        logger.info("Scanning for existing files and folders to sort...")
        
        for item_path in self.downloads_path.iterdir():
            if item_path.is_file():
                filename = item_path.name
                if filename not in self.existing_files:
                    category = self._get_file_category(item_path)
                    if category != "Other":
                        self._move_file(item_path, category)
                    self.existing_files.add(filename)
            elif item_path.is_dir():
                # Handle folders - move non-category folders to Rogue_Folders
                folder_name = item_path.name
                # List of folders to ignore (leave in base directory)
                ignored_folders = {"Rogue_Folders", "Others", "gcode drop"}
                if folder_name not in self.categories.keys() and folder_name not in ignored_folders:
                    self._move_folder_to_rogue(item_path)
    
    def _get_current_files(self) -> Set[str]:
        """Get set of current filenames in Downloads folder."""
        return {f.name for f in self.downloads_path.iterdir() if f.is_file()}
    
    def _process_new_files(self, current_files: Set[str]):
        """Process any new files and folders that have been added."""
        new_files = current_files - self.existing_files
        
        for filename in new_files:
            file_path = self.downloads_path / filename
            if file_path.is_file():
                category = self._get_file_category(file_path)
                self._move_file(file_path, category)
                self.existing_files.add(filename)
            elif file_path.is_dir():
                # Handle new folders - move non-category folders to Rogue_Folders
                folder_name = file_path.name
                # List of folders to ignore (leave in base directory)
                ignored_folders = {"Rogue_Folders", "Others", "gcode drop"}
                if folder_name not in self.categories.keys() and folder_name not in ignored_folders:
                    self._move_folder_to_rogue(file_path)
        
        # Check for redundant zip files after processing new items
        self._cleanup_redundant_zips()
    
    def start_monitoring(self, scan_interval: int = 5):
        """
        Start monitoring the Downloads folder for new files.
        
        Args:
            scan_interval: How often to check for new files (in seconds)
        """
        logger.info(f"Starting Downloads folder monitoring...")
        logger.info(f"Monitoring: {self.downloads_path}")
        logger.info(f"Scan interval: {scan_interval} seconds")
        logger.info("Press Ctrl+C to stop monitoring")
        
        # Initial scan of existing files
        self._scan_and_sort_existing_files()
        
        try:
            while True:
                current_files = self._get_current_files()
                self._process_new_files(current_files)
                time.sleep(scan_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")


def main():
    """Main function to run the Downloads sorter."""
    print("📁 Downloads Sorter - Automatic File Organization")
    print("=" * 50)
    
    # Get Downloads path from command line argument or use default
    downloads_path = None
    if len(sys.argv) > 1:
        downloads_path = sys.argv[1]
    
    # Create and start the sorter
    sorter = DownloadsSorter(downloads_path)
    
    # Start monitoring
    sorter.start_monitoring()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program stopped by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        