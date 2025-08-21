#!/usr/bin/env python3
"""
Script to merge all PDFs from the ordered_pdfs folder into a single PDF file.
The PDFs are merged in numerical order based on their page numbers.
"""

import os
import glob
import re
from PyPDF2 import PdfWriter, PdfReader
from pathlib import Path

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
    
    # Create a PdfWriter object
    pdf_writer = PdfWriter()
    
    # Process each PDF file
    for i, pdf_file in enumerate(pdf_files):
        try:
            print(f"Processing {i+1}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
            
            # Read the PDF file
            with open(pdf_file, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Add all pages from this PDF to the writer
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)
                    
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")
            continue
    
    # Write the merged PDF to output file
    try:
        with open(output_filename, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        print(f"\nSuccessfully merged {len(pdf_files)} PDFs into: {output_filename}")
        
        # Get file size for confirmation
        file_size = os.path.getsize(output_filename)
        file_size_mb = file_size / (1024 * 1024)
        print(f"Output file size: {file_size_mb:.2f} MB")
        
    except Exception as e:
        print(f"Error writing merged PDF: {str(e)}")

if __name__ == "__main__":
    # Configuration
    input_folder = "/workspaces/oo1-extractor/ordered_pdfs"
    output_filename = "/workspaces/oo1-extractor/merged_document.pdf"
    
    print("Starting PDF merge process...")
    print(f"Input folder: {input_folder}")
    print(f"Output file: {output_filename}")
    print("-" * 50)
    
    merge_pdfs(input_folder, output_filename)
    
    print("-" * 50)
    print("PDF merge process completed!")
