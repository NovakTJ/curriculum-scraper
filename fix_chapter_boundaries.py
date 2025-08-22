import json
import os
from collections import OrderedDict

def get_chapter_boundaries():
    """
    Get the page numbers where each chapter starts by examining ordered_unit_files.
    """
    chapter_pages = []
    unit_files = sorted([f for f in os.listdir('ordered_unit_files') if f.endswith('.txt')])
    
    for fname in unit_files:
        page_num = int(fname.split('_')[1])
        chapter_pages.append(page_num)
    
    return sorted(chapter_pages)

def fix_chapter_boundaries():
    """
    Fix the hierarchical JSON to include all pages in chapter boundary gaps.
    """
    
    # Load the current hierarchical categories
    with open('hierarchical_categories_grouped.json', 'r', encoding='utf-8') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)
    
    # Get chapter boundary pages
    chapter_pages = get_chapter_boundaries()
    print("Chapter boundary pages:", chapter_pages)
    
    # Get all pages that exist in data
    all_existing_pages = set()
    for f in os.listdir('data'):
        if f.startswith('page_') and f.endswith('_extracted_text.txt'):
            page_num = int(f.split('_')[1])
            all_existing_pages.add(page_num)
    
    # Get all pages that are currently categorized
    categorized_pages = set()
    for chapter_data in data.values():
        for unit_files in chapter_data.values():
            for filename in unit_files:
                if filename.startswith('page_') and filename.endswith('_extracted_text.txt'):
                    page_num = int(filename.split('_')[1])
                    categorized_pages.add(page_num)
    
    print(f"Total existing pages: {len(all_existing_pages)}")
    print(f"Currently categorized pages: {len(categorized_pages)}")
    
    # Find all missing pages
    missing_pages = sorted(all_existing_pages - categorized_pages)
    print(f"Missing pages: {missing_pages}")
    
    # Group missing pages by which chapter gap they belong to
    chapter_gaps = []
    
    for i in range(len(chapter_pages)):
        # Define the range for this chapter
        chapter_start = chapter_pages[i]
        
        if i < len(chapter_pages) - 1:
            # Not the last chapter - find pages between this chapter start and next chapter start
            next_chapter_start = chapter_pages[i + 1]
            
            # Find the last categorized page in current chapter
            chapter_name = list(data.keys())[i] if i < len(data) - 1 else None
            if chapter_name and chapter_name != "Uncategorized Pages":
                chapter_data = data[chapter_name]
                chapter_categorized_pages = []
                
                for unit_files in chapter_data.values():
                    if not isinstance(unit_files, list):
                        continue
                    for filename in unit_files:
                        if filename.startswith('page_') and filename.endswith('_extracted_text.txt'):
                            page_num = int(filename.split('_')[1])
                            chapter_categorized_pages.append(page_num)
                
                if chapter_categorized_pages:
                    chapter_end = max(chapter_categorized_pages)
                    
                    # Find gap pages between chapter_end and next_chapter_start
                    gap_pages = []
                    for page in range(chapter_end + 1, next_chapter_start):
                        if page in all_existing_pages:
                            gap_pages.append(page)
                    
                    if gap_pages:
                        chapter_gaps.append({
                            'chapter_index': i,
                            'chapter_name': chapter_name,
                            'gap_pages': gap_pages,
                            'next_chapter_start': next_chapter_start
                        })
        else:
            # Last chapter - find any remaining missing pages after the last categorized page
            last_chapter_name = list(data.keys())[-2] if "Uncategorized Pages" in data else list(data.keys())[-1]
            if last_chapter_name != "Uncategorized Pages":
                chapter_data = data[last_chapter_name]
                chapter_categorized_pages = []
                
                for unit_files in chapter_data.values():
                    if not isinstance(unit_files, list):
                        continue
                    for filename in unit_files:
                        if filename.startswith('page_') and filename.endswith('_extracted_text.txt'):
                            page_num = int(filename.split('_')[1])
                            chapter_categorized_pages.append(page_num)
                
                if chapter_categorized_pages:
                    chapter_end = max(chapter_categorized_pages)
                    gap_pages = [p for p in missing_pages if p > chapter_end]
                    
                    if gap_pages:
                        chapter_gaps.append({
                            'chapter_index': i,
                            'chapter_name': last_chapter_name,
                            'gap_pages': gap_pages,
                            'next_chapter_start': None
                        })
    
    print("\nChapter gaps found:")
    for gap in chapter_gaps:
        print(f"  {gap['chapter_name']}: pages {gap['gap_pages']}")
    
    # Add gap pages to appropriate chapters
    for gap in chapter_gaps:
        chapter_name = gap['chapter_name']
        gap_pages = gap['gap_pages']
        
        if chapter_name in data and chapter_name != "Uncategorized Pages":
            # Group consecutive pages in the gap
            groups = []
            current_group = [gap_pages[0]] if gap_pages else []
            
            for i in range(1, len(gap_pages)):
                if gap_pages[i] == gap_pages[i-1] + 1:
                    current_group.append(gap_pages[i])
                else:
                    groups.append(current_group)
                    current_group = [gap_pages[i]]
            
            if current_group:
                groups.append(current_group)
            
            # Add grouped pages to the chapter
            for group in groups:
                if len(group) == 1:
                    group_name = f"Uncategorized_{group[0]:04d}"
                else:
                    group_name = f"Uncategorized_{group[0]:04d}-{group[-1]:04d}"
                
                files = [f"page_{page:04d}_extracted_text.txt" for page in group]
                data[chapter_name][group_name] = files
    
    # Remove the old "Uncategorized Pages" section and add remaining uncategorized pages
    remaining_missing = set(missing_pages)
    for gap in chapter_gaps:
        for page in gap['gap_pages']:
            remaining_missing.discard(page)
    
    if "Uncategorized Pages" in data:
        del data["Uncategorized Pages"]
    
    if remaining_missing:
        remaining_pages = sorted(remaining_missing)
        # Group consecutive remaining pages
        groups = []
        current_group = [remaining_pages[0]]
        
        for i in range(1, len(remaining_pages)):
            if remaining_pages[i] == remaining_pages[i-1] + 1:
                current_group.append(remaining_pages[i])
            else:
                groups.append(current_group)
                current_group = [remaining_pages[i]]
        
        groups.append(current_group)
        
        uncategorized_section = OrderedDict()
        for group in groups:
            if len(group) == 1:
                group_name = f"Uncategorized_{group[0]:04d}"
            else:
                group_name = f"Uncategorized_{group[0]:04d}-{group[-1]:04d}"
            
            files = [f"page_{page:04d}_extracted_text.txt" for page in group]
            uncategorized_section[group_name] = files
        
        data["Uncategorized Pages"] = uncategorized_section
    
    return data

def main():
    fixed_data = fix_chapter_boundaries()
    
    # Save to new file
    output_file = 'hierarchical_categories_fixed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nFixed categories saved to {output_file}")
    
    # Print summary
    total_units = 0
    total_files = 0
    for chapter, chapter_data in fixed_data.items():
        unit_count = len(chapter_data)
        file_count = sum(len(files) for files in chapter_data.values())
        total_units += unit_count
        total_files += file_count
        print(f"{chapter}: {unit_count} units, {file_count} files")
    
    print(f"\nTotal: {total_units} units, {total_files} files across {len(fixed_data)} chapters")

if __name__ == '__main__':
    main()
