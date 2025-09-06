import os
from pypdf import PdfReader, PdfWriter
for i in range(5):
    IN_DIR = f"/workspaces/curriculum-scraper/ordered_text_OS1_{i}/ordered_pdfs"
    OUT_DIR = f"first_page_OS1_{i}"
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
            # extract only the first page
            writer = PdfWriter()
            writer.add_page(reader.pages[0])
            outname = os.path.splitext(name)[0] + ".pdf"
            outpath = os.path.join(OUT_DIR, outname)
            with open(outpath, "wb") as f:
                writer.write(f)
            print("Wrote", outpath, "(1 page)")
        except Exception as e:
            print("ERROR processing", inpath, e)