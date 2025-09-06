# curriculum-scraper

Data scraper and processor to prepare PDF content from a website for a validation LLM agent.

## Overview

The pipeline downloads raw PDFs, trims them to the usable pages, extracts text, reorganizes files, and groups pages into categories. You will primarily interact with:
- `data/` — working data directory
- `ordered_pdfs/` — optional alternative input (preferably first page only)
- `human.json` — category assignments (some items may remain uncategorized)

## Prerequisites

- Linux (tested on Ubuntu 24.04)
- Python 3.x
- Install dependencies (recommended in a virtual environment):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Quickstart

Run everything with the single entrypoint:
```bash
python3 run_pipeline.py
```

List or select steps:
```bash
python3 run_pipeline.py --list
python3 run_pipeline.py --start twopages --end categorize_files
python3 run_pipeline.py --only scra,extract_pdf_text,onepage
python3 run_pipeline.py --skip onepage --continue-on-error
```

Or run the scripts in order:

1) Scrape PDFs
```bash
python3 scra.py
```

2) Keep only the usable pages
```bash
python3 twopages.py
```

3) Extract text from PDFs
```bash
python3 extract_pdf_text.py
```

4) Reorganize text and PDFs by page number
```bash
python3 reorganize_text-files.py
```

5) Ensure one page per text file
```bash
bash onepage.sh
```

Then categorize:

```bash
python3 extract_units.py
python3 add_unit_name_prefix.py
python3 categorize_files.py
python3 sort_filenames_in_json.py
python3 create_hierarchical_categories.py
python3 group_consecutive_uncategorized.py
python3 fix_chapter_boundaries.py
```

At this point, review uncategorized items in `human.json` and assign them where obvious (some categories may be empty until you do).

## Notes

- `human.json` is usable but contains a few uncategorized entries that still require manual review.

## Roadmap / To do

- Document exact dependencies and versions
- Add example input/output structure
- Add tests and CI