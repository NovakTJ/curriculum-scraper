import json
from collections import OrderedDict

def sort_filenames_in_categories(input_file='categories.json', output_file='categories.json'):
    """
    Sort the filenames within each unit category in the JSON file.
    Filenames are sorted by their page number (extracted from the filename).
    """
    
    # Read the existing JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
    
    # Sort filenames within each category
    for unit_name, filenames in data.items():
        if filenames:  # Only sort if there are files
            # Sort by extracting the page number from filename
            # e.g., "page_0021_extracted_text.txt" -> 21
            sorted_filenames = sorted(filenames, key=lambda x: int(x.split('_')[1]))
            data[unit_name] = sorted_filenames
    
    # Write the sorted data back to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Filenames sorted successfully in {output_file}")
    
    # Show example of sorted filenames
    for unit_name, filenames in list(data.items())[:3]:  # Show first 3 units
        if filenames:
            print(f"\n{unit_name}:")
            for filename in filenames:
                page_num = int(filename.split('_')[1])
                print(f"  {filename} (page {page_num})")

def main():
    sort_filenames_in_categories()

if __name__ == '__main__':
    main()
