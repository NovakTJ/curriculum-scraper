# oo1-extractor

We build because we can - a data scraper used to prepare data for a validation agent.

## User guide

Only use human.json and the data folder . alternatively, you can use ordered_pdfs (which should be shortened to just the first page) to extract text in a better way.

human.json still has a few uncategorized files, but it's highly usable.

## Data pipeline

The task has been done using a lot of python scripts, instead of a Jupyter notebook. The order of the scripts is the following:

1. scra.py - to scrape raw PDFs. The website and the PDF formats are weird.
2. twopages.py - to get the usable parts of the PDFs
3. extract_pdf-text.py
4. reorganize_text-files.py - to sort the text files and the PDF files based on their page numbers
5. onepage.sh - to have one page in each text file.

At this point, the files are sorted, and the next task is to group them into categories. The following scripts achieve that:

1. extract_units.py
2. add_unit_name_prefix.py
3. categorize_files.py
4. sort_filenames_in_json.py
5. create_hierarchical_categories.py
6. group_consecutive_uncategorized.py
7. fix_chapter_boundaries.py

At this point, you should look at the uncategorized files, because there will be empty categories to which the consecutive files obviously belong.