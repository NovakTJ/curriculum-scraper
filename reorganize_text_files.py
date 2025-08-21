#!/usr/bin/env python3
"""
Script to reorganize extracted text files based on page numbers.

This script reads text files that contain page numbers in the format " [number]"
and copies them to a new folder with filenames based on the first page number found.
"""

import os
import re
import shutil
from pathlib import Path

def extract_first_page_number(file_path):
    """Extract the first page number from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all lines that match the pattern: space followed by a number
        matches = re.findall(r'^ (\d+)$', content, re.MULTILINE)
        
        if matches:
            return int(matches[0])  # Return the first page number found
        else:
            print(f"Warning: No page number found in {file_path}")
            return None
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def reorganize_text_files(input_dir, output_dir):
    """Reorganize text files based on their first page number."""
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get all text files from input directory
    input_path = Path(input_dir)
    text_files = list(input_path.glob('*.txt'))
    
    print(f"Found {len(text_files)} text files to process...")
    
    # Dictionary to store page number to filename mapping
    page_to_file = {}
    files_without_pages = []
    
    # Process each file
    for file_path in text_files:
        page_num = extract_first_page_number(file_path)
        
        if page_num is not None:
            if page_num in page_to_file:
                print(f"Warning: Page {page_num} found in multiple files:")
                print(f"  - {page_to_file[page_num]}")
                print(f"  - {file_path.name}")
            page_to_file[page_num] = file_path.name
        else:
            files_without_pages.append(file_path.name)
    
    # Copy files to output directory with new names
    successful_copies = 0
    
    for page_num, original_filename in page_to_file.items():
        original_path = input_path / original_filename
        
        # Create new filename: page_XXXX_extracted_text.txt
        new_filename = f"page_{page_num:04d}_extracted_text.txt"
        new_path = Path(output_dir) / new_filename
        
        try:
            shutil.copy2(original_path, new_path)
            successful_copies += 1
            print(f"Copied: {original_filename} -> {new_filename} (page {page_num})")
        except Exception as e:
            print(f"Error copying {original_filename}: {e}")
    
    # Report summary
    print(f"\n=== SUMMARY ===")
    print(f"Total files processed: {len(text_files)}")
    print(f"Successfully copied: {successful_copies}")
    print(f"Files without page numbers: {len(files_without_pages)}")
    
    if files_without_pages:
        print(f"\nFiles without page numbers:")
        for filename in files_without_pages:
            print(f"  - {filename}")
    
    # Show page range
    if page_to_file:
        min_page = min(page_to_file.keys())
        max_page = max(page_to_file.keys())
        print(f"\nPage range: {min_page} to {max_page}")
        
        # Check for missing pages
        missing_pages = []
        for page in range(min_page, max_page + 1):
            if page not in page_to_file:
                missing_pages.append(page)
        
        if missing_pages:
            print(f"Missing pages: {missing_pages}")
        else:
            print("No missing pages in the range!")

def main():
    # Define input and output directories
    input_dir = "/workspaces/oo1-extractor/extracted_text"
    output_dir = "/workspaces/oo1-extractor/ordered_text"
    
    print("PDF Text File Reorganizer")
    print("=" * 30)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Check if input directory exists
    if not Path(input_dir).exists():
        print(f"Error: Input directory '{input_dir}' does not exist!")
        return
    
    # Reorganize files
    reorganize_text_files(input_dir, output_dir)

if __name__ == "__main__":
    main()
