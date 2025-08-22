import os
import re

SRC_DIR = 'ordered_text_page1_only'
DST_DIR = 'ordered_text_units'

os.makedirs(DST_DIR, exist_ok=True)

def extract_units_from_file(src_path, dst_path):
    with open(src_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f]
    
    units = []
    i = 0
    # Find the line with 'Glava'
    while i < len(lines) and not re.match(r'^Glava \d+', lines[i]):
        i += 1
    if i == len(lines):
        return  # No 'Glava' found
    units.append(lines[i])
    i += 1
    # Collect curriculum units
    current_unit = []
    while i < len(lines):
        line = lines[i]
        if re.match(r'^\d+$', line):
            break  # Page number, stop
        if line.startswith('❖'):
            if current_unit:
                # Write previous unit
                units.append(' '.join(current_unit))
                current_unit = []
            current_unit.append(line)
        elif current_unit:
            # Continuation of previous unit
            current_unit.append(line)
        i += 1
    if current_unit:
        units.append(' '.join(current_unit))
    # Write to new file
    with open(dst_path, 'w', encoding='utf-8') as f:
        for unit in units:
            f.write(unit.strip() + '\n')

def main():
    for fname in os.listdir(SRC_DIR):
        if fname.endswith('.txt'):
            src_path = os.path.join(SRC_DIR, fname)
            dst_path = os.path.join(DST_DIR, fname)
            extract_units_from_file(src_path, dst_path)

if __name__ == '__main__':
    main()
