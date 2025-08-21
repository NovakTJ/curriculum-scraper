# crawl_and_download.py
import os
import re
import sys
import time
import json
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

START_URL = "https://afrodita.rcub.bg.ac.rs/~dmilicev/publishing/OOP%20predavanja%202024/assets/"  # <- change if needed
OUT_DIR = "downloaded_pdfs_new"
MAX_PAGES = 24000  # safety

session = requests.Session()
os.makedirs(OUT_DIR, exist_ok=True)

seen = set()
to_visit = [START_URL]
downloaded = 0

# regex to find base64 PDF in text (JVBERi0x... typical)
b64_pdf_re = re.compile(r'([A-Za-z0-9+/=]{100,})')  # will be filtered by PDF header check

def save_bytes_as_pdf(data: bytes, filename: str):
    with open(filename, "wb") as f:
        f.write(data)

def try_extract_base64_and_save(text, out_path_prefix):
    # attempt to find a PDF base64 block inside text
    # often it's inside local_pdf({... "pdf": "JVBERi0x..." })
    # search for "JVBERi0" start
    hits = re.findall(r'JVBERi0[^\"]{20,}', text)  # find likely base64 starts
    for i, hit in enumerate(hits):
        # cut to contiguous base64 characters
        b64 = re.match(r'(JVBERi0[A-Za-z0-9+/=]+)', hit)
        if b64:
            s = b64.group(1)
            try:
                import base64
                raw = base64.b64decode(s + "===")  # pad just in case
                if raw.startswith(b'%PDF'):
                    out = f"{out_path_prefix}_embedded_{i}.pdf"
                    save_bytes_as_pdf(raw, out)
                    print("Saved embedded pdf:", out)
                    return True
            except Exception:
                pass
    # fallback: search for "pdf" : "..." style JSON
    js_matches = re.findall(r'"pdf"\s*:\s*"([A-Za-z0-9+/=]+)"', text)
    for i, s in enumerate(js_matches):
        try:
            import base64
            raw = base64.b64decode(s + "===")
            if raw.startswith(b'%PDF'):
                out = f"{out_path_prefix}_embedded_json_{i}.pdf"
                save_bytes_as_pdf(raw, out)
                print("Saved embedded pdf (json):", out)
                return True
        except Exception:
            pass
    return False

def download_url(url):
    global downloaded
    try:
        r = session.get(url, timeout=20)
    except Exception as e:
        print("failed", url, e)
        return
    content_type = r.headers.get("content-type","").lower()
    basename = os.path.basename(urlparse(url).path) or "index"
    if content_type.startswith("application/pdf") or r.content.startswith(b"%PDF"):
        # save pdf
        filename = os.path.join(OUT_DIR, basename if basename.endswith(".pdf") else basename + ".pdf")
        save_bytes_as_pdf(r.content, filename)
        downloaded += 1
        print("Downloaded PDF:", filename)
        return
    text = r.text
    # try to extract embedded base64 PDF from text
    if try_extract_base64_and_save(text, os.path.join(OUT_DIR, basename)):
        downloaded += 1
    else:
        # parse html for links to follow
        soup = BeautifulSoup(text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # only follow links inside same folder / site
            joined = urljoin(url, href)
            if ';' in joined or 'w' in joined:
                continue
            # keep same netloc and starting path prefix
            if urlparse(joined).netloc == urlparse(START_URL).netloc and joined not in seen:
                if len(to_visit) + len(seen) < MAX_PAGES:
                    to_visit.append(joined)

# DFS crawl
while to_visit and len(seen) < MAX_PAGES:
    url = to_visit.pop(-1)
    if url in seen: 
        continue
    seen.add(url)
    print("Visiting:", url)
    
    download_url(url)
    time.sleep(0.2)  # be polite

print("Done. PDFs saved in", OUT_DIR)
