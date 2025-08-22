import os

SRC_DIR = 'ordered_text_units_named'

def count_unit_names_in_file(file_path):
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('UNIT NAME:'):
                count += 1
    return count

def main():
    results = []
    for fname in os.listdir(SRC_DIR):
        if fname.endswith('.txt'):
            file_path = os.path.join(SRC_DIR, fname)
            count = count_unit_names_in_file(file_path)
            results.append((fname, count))
    # Print results
    for fname, count in results:
        
        if count>1: print(f'{fname}: {count}')

if __name__ == '__main__':
    main()
