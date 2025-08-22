import json
import os
from collections import OrderedDict

def get_chapter_hierarchy():
    """
    Extract the hierarchical structure from ordered_unit_files.
    Returns a dictionary with chapter info and their units.
    """
    hierarchy = OrderedDict()
    unit_files = sorted([f for f in os.listdir('ordered_unit_files') if f.endswith('.txt')])
    
    for fname in unit_files:
        with open(os.path.join('ordered_unit_files', fname), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        chapter_line = None
        units = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Glava '):
                chapter_line = line
            elif line.startswith('❖ '):
                unit_name = line[2:].strip()
                if unit_name:
                    units.append(unit_name)
        
        if chapter_line and units:
            hierarchy[chapter_line] = units
    
    return hierarchy

def find_missing_pages():
    """Find pages that exist in data but aren't categorized."""
    # Get all existing pages
    data_files = set()
    for f in os.listdir('data'):
        if f.startswith('page_') and f.endswith('_extracted_text.txt'):
            page_num = int(f.split('_')[1])
            data_files.add(page_num)
    
    # Get all categorized pages
    with open('humancategories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
    
    categorized_files = set()
    for unit_files in categories.values():
        for filename in unit_files:
            if filename.startswith('page_') and filename.endswith('_extracted_text.txt'):
                page_num = int(filename.split('_')[1])
                categorized_files.add(page_num)
    
    # Find missing pages
    missing_pages = []
    for page_num in sorted(data_files):
        if page_num not in categorized_files:
            missing_pages.append(page_num)
    
    return missing_pages

def create_hierarchical_json():
    """Create a new JSON with hierarchical structure and missing pages."""
    
    # Load existing categories
    with open('humancategories.json', 'r', encoding='utf-8') as f:
        flat_categories = json.load(f, object_pairs_hook=OrderedDict)
    
    # Get chapter hierarchy
    chapter_hierarchy = get_chapter_hierarchy()
    print("Chapter hierarchy:")
    for chapter, units in chapter_hierarchy.items():
        print(f"  {chapter}")
        for unit in units:
            print(f"    ❖ {unit}")
        print()
    
    # Find missing pages
    missing_pages = find_missing_pages()
    print(f"Missing pages to be added as 'Uncategorized': {missing_pages}")
    
    # Create hierarchical structure
    hierarchical_json = OrderedDict()
    
    # Track which pages should be inserted where
    all_pages = set()
    for unit_files in flat_categories.values():
        for filename in unit_files:
            if filename.startswith('page_'):
                page_num = int(filename.split('_')[1])
                all_pages.add(page_num)
    
    # Add missing pages to the list
    for page_num in missing_pages:
        all_pages.add(page_num)
    
    all_pages = sorted(all_pages)
    
    # Process each chapter
    for chapter, chapter_units in chapter_hierarchy.items():
        chapter_data = OrderedDict()
        
        # Find the page range for this chapter by looking at unit files
        chapter_pages = []
        for unit_name in chapter_units:
            if unit_name in flat_categories:
                for filename in flat_categories[unit_name]:
                    if filename.startswith('page_'):
                        page_num = int(filename.split('_')[1])
                        chapter_pages.append(page_num)
        
        if chapter_pages:
            chapter_start = min(chapter_pages)
            chapter_end = max(chapter_pages)
            
            # Add all units for this chapter
            for unit_name in chapter_units:
                if unit_name in flat_categories:
                    chapter_data[unit_name] = flat_categories[unit_name]
                else:
                    chapter_data[unit_name] = []
            
            # Find uncategorized pages in this chapter's range
            for page_num in missing_pages:
                if chapter_start <= page_num <= chapter_end:
                    uncategorized_key = f"Uncategorized_{page_num:04d}"
                    filename = f"page_{page_num:04d}_extracted_text.txt"
                    chapter_data[uncategorized_key] = [filename]
        
        hierarchical_json[chapter] = chapter_data
    
    # Handle any remaining uncategorized pages that don't fall in chapter ranges
    remaining_uncategorized = OrderedDict()
    for page_num in missing_pages:
        # Check if this page was already handled
        found = False
        for chapter_data in hierarchical_json.values():
            uncategorized_key = f"Uncategorized_{page_num:04d}"
            if uncategorized_key in chapter_data:
                found = True
                break
        
        if not found:
            uncategorized_key = f"Uncategorized_{page_num:04d}"
            filename = f"page_{page_num:04d}_extracted_text.txt"
            remaining_uncategorized[uncategorized_key] = [filename]
    
    if remaining_uncategorized:
        hierarchical_json["Uncategorized Pages"] = remaining_uncategorized
    
    return hierarchical_json

def main():
    hierarchical_data = create_hierarchical_json()
    
    # Save to new file
    output_file = 'hierarchical_categories.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hierarchical_data, f, ensure_ascii=False, indent=2)
    
    print(f"Hierarchical categories saved to {output_file}")
    
    # Print summary
    total_units = 0
    total_files = 0
    for chapter, chapter_data in hierarchical_data.items():
        unit_count = len(chapter_data)
        file_count = sum(len(files) for files in chapter_data.values())
        total_units += unit_count
        total_files += file_count
        print(f"{chapter}: {unit_count} units, {file_count} files")
    
    print(f"\nTotal: {total_units} units, {total_files} files across {len(hierarchical_data)} chapters")

if __name__ == '__main__':
    main()
