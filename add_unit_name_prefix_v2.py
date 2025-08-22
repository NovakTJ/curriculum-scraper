import os

SRC_UNITS_DIR = 'ordered_text_units'
SRC_ORIG_DIR = 'ordered_text_page1_only'
DST_DIR = 'ordered_text_units_named'

os.makedirs(DST_DIR, exist_ok=True)

def get_unit_names():
    unit_names = set()
    for fname in os.listdir(SRC_UNITS_DIR):
        if fname.endswith('.txt'):
            with open(os.path.join(SRC_UNITS_DIR, fname), 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('❖ '):
                        unit_name = line[2:].strip()
                        if unit_name:
                            unit_names.add(unit_name)
    return unit_names

def process_file(src_path, dst_path, unit_names):
    with open(src_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f]
    new_lines = []
    for line in lines:
        if line.strip() in unit_names:
            new_lines.append(f'UNIT NAME: {line.strip()}')
        else:
            new_lines.append(line)
    with open(dst_path, 'w', encoding='utf-8') as f:
        for line in new_lines:
            f.write(line + '\n')

def main():
    unit_names = get_unit_names()
    for fname in os.listdir(SRC_ORIG_DIR):
        if fname.endswith('.txt'):
            src_path = os.path.join(SRC_ORIG_DIR, fname)
            dst_path = os.path.join(DST_DIR, fname)
            process_file(src_path, dst_path, unit_names)

if __name__ == '__main__':
    main()
