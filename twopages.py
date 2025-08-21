# extract_last_two_pages.py
import os
from pypdf import PdfReader, PdfWriter

IN_DIR = input("In_dir?")
OUT_DIR = "last_two_pages"
os.makedirs(OUT_DIR, exist_ok=True)

for name in os.listdir(IN_DIR):
    if not name.lower().endswith(".pdf"):
        continue
    inpath = os.path.join(IN_DIR, name)
    try:
        reader = PdfReader(inpath)
        n = len(reader.pages)
        if n == 0:
            print("empty?", inpath)
            continue
        # pick last two pages (if only 1 page exists, just copy it)
        start = max(0, n-2)
        writer = PdfWriter()
        for i in range(start, n):
            writer.add_page(reader.pages[i])
        outname = os.path.splitext(name)[0] + "_last2.pdf"
        outpath = os.path.join(OUT_DIR, outname)
        with open(outpath, "wb") as f:
            writer.write(f)
        print("Wrote", outpath, "(", n, "->", n-start, "pages )")
    except Exception as e:
        print("ERROR processing", inpath, e)
