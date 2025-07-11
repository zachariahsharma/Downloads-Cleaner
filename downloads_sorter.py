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
    
    def __init__(self, downloads_path: str = None):
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
                # Don't move files that don't match any category
                logger.info(f"Keeping {file_path.name} in Downloads (no category match)")
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
    
    def _scan_and_sort_existing_files(self):
        """Scan Downloads folder and sort any existing files."""
        logger.info("Scanning for existing files to sort...")
        
        for file_path in self.downloads_path.iterdir():
            if file_path.is_file():
                filename = file_path.name
                if filename not in self.existing_files:
                    category = self._get_file_category(file_path)
                    if category != "Other":
                        self._move_file(file_path, category)
                    self.existing_files.add(filename)
    
    def _get_current_files(self) -> Set[str]:
        """Get set of current filenames in Downloads folder."""
        return {f.name for f in self.downloads_path.iterdir() if f.is_file()}
    
    def _process_new_files(self, current_files: Set[str]):
        """Process any new files that have been added."""
        new_files = current_files - self.existing_files
        
        for filename in new_files:
            file_path = self.downloads_path / filename
            if file_path.is_file():
                category = self._get_file_category(file_path)
                self._move_file(file_path, category)
                self.existing_files.add(filename)
    
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
    main() 