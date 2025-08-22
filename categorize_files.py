import os
import json
from collections import OrderedDict

SRC_UNITS_DIR = 'ordered_unit_files'
SRC_ORIG_DIR = 'data'
DST_FILE = 'categories.json'

def get_unit_names_ordered():
    unit_names = []
    # Sort files by name to ensure chronological order
    unit_files = sorted([f for f in os.listdir(SRC_UNITS_DIR) if f.endswith('.txt')])
    
    for fname in unit_files:
        with open(os.path.join(SRC_UNITS_DIR, fname), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('❖ '):
                    unit_name = line[2:].strip()
                    if unit_name and unit_name not in unit_names:
                        unit_names.append(unit_name)
    return unit_names

def categorize_files():
    # Get all unit names in chronological order
    unit_names = get_unit_names_ordered()
    
    # Initialize the result dictionary with OrderedDict to maintain order
    unit_to_files = OrderedDict((unit_name, []) for unit_name in unit_names)
    
    # Process each file in the data directory
    for fname in os.listdir(SRC_ORIG_DIR):
        if fname.endswith('.txt'):
            file_path = os.path.join(SRC_ORIG_DIR, fname)
            
            # Read the file and look for "UNIT NAME:" line
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('UNIT NAME: '):
                            unit_name = line[11:].strip()  # Remove "UNIT NAME: " prefix
                            if unit_name in unit_to_files:
                                unit_to_files[unit_name].append(fname)
                            break  # Only look for the first occurrence
            except Exception as e:
                print(f"Error processing file {fname}: {e}")
    
    return unit_to_files

def main():
    unit_to_files = categorize_files()
    
    # Write the result to JSON file
    with open(DST_FILE, 'w', encoding='utf-8') as f:
        json.dump(unit_to_files, f, ensure_ascii=False, indent=2)
    
    print(f"Categorization complete. Results saved to {DST_FILE}")
    
    # Print summary
    total_files = sum(len(files) for files in unit_to_files.values())
    print(f"Found {len(unit_to_files)} units with {total_files} total files")
    
    # Show units with their file counts
    for unit_name, files in unit_to_files.items():
        print(f"  {unit_name}: {len(files)} files")

if __name__ == '__main__':
    main()
