#!/usr/bin/env python3
"""
Script to merge PDF files into a single PDF.

Defaults:
    - Input folder: ./first_page
    - Output file: ./merged_document.pdf

Files are merged in natural numerical order like page_0001.pdf, page_0002.pdf, ...
Use CLI flags to override input/output paths.
"""

import os
import glob
import re
import argparse
from pathlib import Path

# Prefer pypdf's PdfMerger for robust streaming merges
try:
        from pypdf import PdfMerger
except Exception:  # Fallback to PyPDF2 if needed
        from PyPDF2 import PdfMerger  # type: ignore

def natural_sort_key(filename):
    """Extract the page number for proper numerical sorting."""
    match = re.search(r'page_(\d+)\.pdf', filename)
    if match:
        return int(match.group(1))
    return 0

def merge_pdfs(input_folder, output_filename):
    """
    Merge all PDF files from input_folder into a single PDF.
    
    Args:
        input_folder (str): Path to folder containing PDF files
        output_filename (str): Name of the output merged PDF file
    """
    # Get all PDF files from the input folder
    pdf_pattern = os.path.join(input_folder, "page_*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        print(f"No PDF files found matching pattern: {pdf_pattern}")
        return
    
    # Sort files numerically by page number
    pdf_files.sort(key=natural_sort_key)
    
    print(f"Found {len(pdf_files)} PDF files to merge")
    print(f"First file: {os.path.basename(pdf_files[0])}")
    print(f"Last file: {os.path.basename(pdf_files[-1])}")
    
    # Create a PdfMerger for efficient appending without holding many file handles
    merger = PdfMerger()

    # Process each PDF file
    for i, pdf_file in enumerate(pdf_files):
        try:
            print(f"Processing {i+1}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
            merger.append(pdf_file)
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")
            continue

    # Write the merged PDF to output file
    try:
        # Ensure output directory exists
        Path(output_filename).parent.mkdir(parents=True, exist_ok=True)
        with open(output_filename, 'wb') as output_file:
            merger.write(output_file)
        merger.close()

        print(f"\nSuccessfully merged {len(pdf_files)} PDFs into: {output_filename}")

        # Get file size for confirmation
        file_size = os.path.getsize(output_filename)
        file_size_mb = file_size / (1024 * 1024)
        print(f"Output file size: {file_size_mb:.2f} MB")

    except Exception as e:
        print(f"Error writing merged PDF: {str(e)}")

if __name__ == "__main__":
    # CLI arguments
    parser = argparse.ArgumentParser(description="Merge PDFs from a folder into one file.")
    default_input = str((Path(__file__).parent / "first_page").resolve())
    default_output = str((Path(__file__).parent / "merged_document.pdf").resolve())
    parser.add_argument("-i", "--input", dest="input_folder", default=default_input, help="Folder containing PDFs (default: %(default)s)")
    parser.add_argument("-o", "--output", dest="output_filename", default=default_output, help="Output merged PDF path (default: %(default)s)")
    args = parser.parse_args()

    input_folder = args.input_folder
    output_filename = args.output_filename

    print("Starting PDF merge process...")
    print(f"Input folder: {input_folder}")
    print(f"Output file: {output_filename}")
    print("-" * 50)

    merge_pdfs(input_folder, output_filename)

    print("-" * 50)
    print("PDF merge process completed!")
