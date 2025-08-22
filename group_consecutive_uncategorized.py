import json
from collections import OrderedDict

def group_consecutive_uncategorized():
    """
    Group consecutive uncategorized pages into single categories.
    """
    
    # Load the hierarchical categories
    with open('hierarchical_categories.json', 'r', encoding='utf-8') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
    
    # Process each chapter
    for chapter_name, chapter_data in data.items():
        if chapter_name == "Uncategorized Pages":
            continue  # Handle this separately at the end
            
        # Find all uncategorized entries in this chapter
        uncategorized_keys = [key for key in chapter_data.keys() if key.startswith('Uncategorized_')]
        
        if not uncategorized_keys:
            continue
            
        # Extract page numbers and sort them
        page_numbers = []
        for key in uncategorized_keys:
            page_num = int(key.split('_')[1])
            page_numbers.append(page_num)
        
        page_numbers.sort()
        
        # Group consecutive pages
        groups = []
        current_group = [page_numbers[0]]
        
        for i in range(1, len(page_numbers)):
            if page_numbers[i] == page_numbers[i-1] + 1:
                # Consecutive page
                current_group.append(page_numbers[i])
            else:
                # Gap found, start new group
                groups.append(current_group)
                current_group = [page_numbers[i]]
        
        # Don't forget the last group
        groups.append(current_group)
        
        # Remove old uncategorized entries
        for key in uncategorized_keys:
            del chapter_data[key]
        
        # Create new grouped entries
        for i, group in enumerate(groups):
            if len(group) == 1:
                # Single page
                group_name = f"Uncategorized_{group[0]:04d}"
            else:
                # Range of pages
                group_name = f"Uncategorized_{group[0]:04d}-{group[-1]:04d}"
            
            # Collect all files for this group
            files = []
            for page_num in group:
                files.append(f"page_{page_num:04d}_extracted_text.txt")
            
            chapter_data[group_name] = files
    
    # Handle the "Uncategorized Pages" section similarly
    if "Uncategorized Pages" in data:
        uncategorized_section = data["Uncategorized Pages"]
        
        # Extract page numbers
        page_numbers = []
        for key in uncategorized_section.keys():
            page_num = int(key.split('_')[1])
            page_numbers.append(page_num)
        
        page_numbers.sort()
        
        # Group consecutive pages
        groups = []
        current_group = [page_numbers[0]]
        
        for i in range(1, len(page_numbers)):
            if page_numbers[i] == page_numbers[i-1] + 1:
                current_group.append(page_numbers[i])
            else:
                groups.append(current_group)
                current_group = [page_numbers[i]]
        
        groups.append(current_group)
        
        # Create new grouped structure
        new_uncategorized = OrderedDict()
        for group in groups:
            if len(group) == 1:
                group_name = f"Uncategorized_{group[0]:04d}"
            else:
                group_name = f"Uncategorized_{group[0]:04d}-{group[-1]:04d}"
            
            files = []
            for page_num in group:
                files.append(f"page_{page_num:04d}_extracted_text.txt")
            
            new_uncategorized[group_name] = files
        
        data["Uncategorized Pages"] = new_uncategorized
    
    return data

def main():
    grouped_data = group_consecutive_uncategorized()
    
    # Save to new file
    output_file = 'hierarchical_categories_grouped.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(grouped_data, f, ensure_ascii=False, indent=2)
    
    print(f"Grouped categories saved to {output_file}")
    
    # Print summary of changes
    total_units = 0
    total_files = 0
    uncategorized_count = 0
    
    for chapter, chapter_data in grouped_data.items():
        chapter_uncategorized = 0
        for unit_name in chapter_data.keys():
            if unit_name.startswith('Uncategorized_'):
                chapter_uncategorized += 1
                uncategorized_count += 1
        
        unit_count = len(chapter_data)
        file_count = sum(len(files) for files in chapter_data.values())
        total_units += unit_count
        total_files += file_count
        
        if chapter_uncategorized > 0:
            print(f"{chapter}: {unit_count} units ({chapter_uncategorized} uncategorized groups), {file_count} files")
        else:
            print(f"{chapter}: {unit_count} units, {file_count} files")
    
    print(f"\nTotal: {total_units} units ({uncategorized_count} uncategorized groups), {total_files} files across {len(grouped_data)} chapters")

if __name__ == '__main__':
    main()
