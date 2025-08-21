#!/usr/bin/env python3
"""
PDF Text Extraction Script

This script extracts all text from PDF files in a specified directory.
It can process a single PDF or all PDFs in a directory.

Usage:
    python extract_pdf_text.py [input_path] [output_dir]
    
Examples:
    python extract_pdf_text.py file.pdf                    # Extract from single file to console
    python extract_pdf_text.py downloaded_pdfs_new/          # Extract from all PDFs in directory
    python extract_pdf_text.py file.pdf extracted_text/    # Extract to specific output directory
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List
import traceback

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf library not found. Install it with: pip install pypdf")
    sys.exit(1)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    try:
        reader = PdfReader(pdf_path)
        text_content = []
        
        print(f"Processing {os.path.basename(pdf_path)} ({len(reader.pages)} pages)...")
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_content.append(f"--- PAGE {page_num} ---\n{page_text}\n")
                else:
                    text_content.append(f"--- PAGE {page_num} ---\n[No extractable text found]\n")
            except Exception as e:
                text_content.append(f"--- PAGE {page_num} ---\n[Error extracting text: {str(e)}]\n")
                
        return "\n".join(text_content)
        
    except Exception as e:
        return f"Error reading PDF {pdf_path}: {str(e)}"

def save_text_to_file(text: str, output_path: str) -> None:
    """Save extracted text to a file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text saved to: {output_path}")
    except Exception as e:
        print(f"Error saving text to {output_path}: {str(e)}")

def get_pdf_files(directory: str) -> List[str]:
    """Get all PDF files in a directory."""
    pdf_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, filename))
    return sorted(pdf_files)

def process_single_pdf(pdf_path: str, output_dir: Optional[str] = None) -> None:
    """Process a single PDF file."""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        return
        
    print(f"Extracting text from: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_extracted_text.txt")
        save_text_to_file(text, output_path)
    else:
        print("\n" + "="*80)
        print(f"EXTRACTED TEXT FROM: {os.path.basename(pdf_path)}")
        print("="*80)
        print(text)
        print("="*80 + "\n")

def process_directory(input_dir: str, output_dir: Optional[str] = None) -> None:
    """Process all PDF files in a directory."""
    if not os.path.exists(input_dir):
        print(f"Error: Directory '{input_dir}' not found.")
        return
        
    pdf_files = get_pdf_files(input_dir)
    
    if not pdf_files:
        print(f"No PDF files found in directory: {input_dir}")
        return
        
    print(f"Found {len(pdf_files)} PDF files in {input_dir}")
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory: {output_dir}")
    
    successful = 0
    failed = 0
    
    for pdf_path in pdf_files:
        try:
            text = extract_text_from_pdf(pdf_path)
            
            if output_dir:
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}_extracted_text.txt")
                save_text_to_file(text, output_path)
            else:
                print(f"\n{'='*80}")
                print(f"EXTRACTED TEXT FROM: {os.path.basename(pdf_path)}")
                print('='*80)
                print(text[:1000] + "..." if len(text) > 1000 else text)  # Show first 1000 chars
                print('='*80)
                
            successful += 1
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            failed += 1
            
    print(f"\nProcessing complete:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(pdf_files)}")

def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_pdf_text.py file.pdf                    # Extract from single file to console
  python extract_pdf_text.py downloaded_pdfs_new/          # Extract from all PDFs in directory
  python extract_pdf_text.py file.pdf extracted_text/    # Extract to specific output directory
  python extract_pdf_text.py downloaded_pdfs_new/ output/  # Process directory, save to output/
        """
    )
    
    parser.add_argument('input_path', nargs='?', default='downloaded_pdfs_new',
                       help='Path to PDF file or directory containing PDFs (default: downloaded_pdfs_new)')
    parser.add_argument('output_dir', nargs='?', default=None,
                       help='Output directory for extracted text files (default: print to console)')
    parser.add_argument('--encoding', default='utf-8',
                       help='Text encoding for output files (default: utf-8)')
    
    args = parser.parse_args()
    
    input_path = args.input_path
    output_dir = args.output_dir
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("PDF Text Extractor")
        print("=" * 50)
        print("Usage: python extract_pdf_text.py [input_path] [output_dir]")
        print()
        print("Available PDF directories in current workspace:")
        for item in os.listdir('.'):
            if os.path.isdir(item) and any(f.lower().endswith('.pdf') for f in os.listdir(item)):
                pdf_count = len([f for f in os.listdir(item) if f.lower().endswith('.pdf')])
                print(f"  {item}/ ({pdf_count} PDFs)")
        print()
        print("Examples:")
        print("  python extract_pdf_text.py downloaded_pdfs_new/")
        print("  python extract_pdf_text.py downloaded_pdfs_new/ extracted_text/")
        return
    
    if os.path.isfile(input_path):
        print("Processing single PDF file...")
        process_single_pdf(input_path, output_dir)
    elif os.path.isdir(input_path):
        print("Processing directory of PDF files...")
        process_directory(input_path, output_dir)
    else:
        print(f"Error: '{input_path}' is not a valid file or directory.")
        sys.exit(1)

if __name__ == "__main__":
    main()
