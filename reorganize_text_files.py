#!/usr/bin/env python3
"""
Script to reorganize extracted text files and corresponding PDF files based on page numbers.

This script reads text files that contain page numbers in the format " [number]"
and copies them to a new folder with filenames based on the first page number found.
It also copies the corresponding PDF files from which the text was extracted,
maintaining the same page-based naming convention.

Text files: page_XXXX_extracted_text.txt
PDF files: page_XXXX.pdf (in ordered_pdfs/ subdirectory)
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
    print(f"\n=== TEXT FILES SUMMARY ===")
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
    
    return page_to_file

def get_uuid_from_filename(filename):
    """Extract UUID from filename (text or PDF)."""
    if filename.endswith('_last2_extracted_text.txt'):
        return filename.replace('_last2_extracted_text.txt', '')
    elif filename.endswith('_last2.pdf'):
        return filename.replace('_last2.pdf', '')
    return None

def reorganize_pdf_files(input_dir, pdf_dir, output_dir, page_to_file):
    """Reorganize PDF files based on the page mapping from text files."""
    
    # Create output directory if it doesn't exist
    pdf_output_dir = Path(output_dir) / "ordered_pdfs"
    pdf_output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=== PDF REORGANIZATION ===")
    print(f"PDF input directory: {pdf_dir}")
    print(f"PDF output directory: {pdf_output_dir}")
    
    # Get all PDF files from input directory
    pdf_path = Path(pdf_dir)
    pdf_files = list(pdf_path.glob('*.pdf'))
    
    print(f"Found {len(pdf_files)} PDF files to process...")
    
    # Track successful PDF copies
    successful_pdf_copies = 0
    missing_pdfs = []
    
    # Process each page number to filename mapping
    for page_num, original_text_filename in page_to_file.items():
        # Extract UUID from text filename
        uuid = get_uuid_from_filename(original_text_filename)
        
        if uuid:
            # Construct corresponding PDF filename
            pdf_filename = f"{uuid}_last2.pdf"
            pdf_path_full = pdf_path / pdf_filename
            
            if pdf_path_full.exists():
                # Create new PDF filename: page_XXXX.pdf
                new_pdf_filename = f"page_{page_num:04d}.pdf"
                new_pdf_path = pdf_output_dir / new_pdf_filename
                
                try:
                    shutil.copy2(pdf_path_full, new_pdf_path)
                    successful_pdf_copies += 1
                    print(f"Copied: {pdf_filename} -> {new_pdf_filename} (page {page_num})")
                except Exception as e:
                    print(f"Error copying {pdf_filename}: {e}")
            else:
                missing_pdfs.append(pdf_filename)
                print(f"Warning: PDF file not found: {pdf_filename}")
    
    # Report PDF summary
    print(f"\n=== PDF SUMMARY ===")
    print(f"Successfully copied PDFs: {successful_pdf_copies}")
    print(f"Missing PDFs: {len(missing_pdfs)}")
    
    if missing_pdfs:
        print(f"\nMissing PDF files:")
        for pdf_file in missing_pdfs:
            print(f"  - {pdf_file}")
    
    return successful_pdf_copies

def main():
    # Define input and output directories
    input_dir = "/workspaces/oo1-extractor/extracted_text"
    pdf_dir = "/workspaces/oo1-extractor/last_two_pages"
    output_dir = "/workspaces/oo1-extractor/ordered_text"
    
    print("PDF Text File Reorganizer")
    print("=" * 30)
    print(f"Input directory: {input_dir}")
    print(f"PDF directory: {pdf_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Check if input directories exist
    if not Path(input_dir).exists():
        print(f"Error: Input directory '{input_dir}' does not exist!")
        return
    
    if not Path(pdf_dir).exists():
        print(f"Error: PDF directory '{pdf_dir}' does not exist!")
        return
    
    # Reorganize text files first
    page_to_file = reorganize_text_files(input_dir, output_dir)
    
    # Only proceed with PDF reorganization if we have successful text file mappings
    if page_to_file:
        reorganize_pdf_files(input_dir, pdf_dir, output_dir, page_to_file)
    else:
        print("\nSkipping PDF reorganization - no valid page mappings found.")

if __name__ == "__main__":
    main()
