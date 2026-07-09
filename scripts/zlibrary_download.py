"""
Z-Library Book Downloader

Search z-library.sk for a book title, download the most popular Chinese translation,
convert non-PDF to PDF via ebook-convert, save to ~/Downloads/books/.

Usage:
    python3 zlibrary_download.py <book-title>
"""

import sys
import os
import json
import re
import subprocess
from urllib.parse import quote, urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Install with: pip install requests beautifulsoup4")
    sys.exit(1)

BASE_URL = "https://z-library.sk"
COOKIE_FILE = os.path.expanduser("~/.zlibrary_cookies.json")
DOWNLOAD_DIR = os.path.expanduser("~/Downloads/books")


def load_cookies():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE) as f:
            return json.load(f)
    return {}


def save_cookies(cookies_dict):
    os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies_dict, f)


def search_book(session, title):
    url = f"{BASE_URL}/s/{quote(title)}/"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    for item in soup.select("table.zBookItem"):  # Z-Library book item selector
        link = item.select_one("a[href*='/book/']")
        if not link:
            continue
        book_url = urljoin(BASE_URL, link.get("href"))
        book_title = link.get("title") or link.text.strip()

        lang_el = item.select_one(".book-lang")
        lang = (lang_el.text.strip() if lang_el else "").lower()

        downloads_el = item.select_one(".book-dl-count")
        downloads = 0
        if downloads_el:
            m = re.search(r"(\d+)", downloads_el.text)
            if m:
                downloads = int(m.group(1))

        results.append({
            "title": book_title,
            "url": book_url,
            "lang": lang,
            "downloads": downloads,
        })
    return results


def get_download_link(session, book_url):
    resp = session.get(book_url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    dl_link = soup.select_one("a.downloadLink")
    if not dl_link:
        dl_link = soup.select_one("a[href*='/download/']")
    if not dl_link:
        return None

    return urljoin(BASE_URL, dl_link.get("href"))


def convert_to_pdf(filepath):
    """Convert non-PDF file to PDF using Calibre's ebook-convert."""
    if filepath.lower().endswith(".pdf"):
        return filepath

    pdf_path = os.path.splitext(filepath)[0] + ".pdf"
    try:
        result = subprocess.run(
            ["ebook-convert", filepath, pdf_path],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0 and os.path.exists(pdf_path):
            os.remove(filepath)
            return pdf_path
        else:
            print(f"Conversion warning: {result.stderr.strip()}")
            return filepath
    except FileNotFoundError:
        print("Warning: ebook-convert not found. Install Calibre or add it to PATH.")
        return filepath
    except subprocess.TimeoutExpired:
        print("Warning: conversion timed out after 120s.")
        return filepath


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 zlibrary_download.py <book-title>")
        sys.exit(1)

    book_title = " ".join(sys.argv[1:])
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    cookies = load_cookies()
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    if cookies:
        session.cookies.update(cookies)

    print(f"Searching: {book_title}")
    results = search_book(session, book_title)

    # Filter to Chinese results, sort by downloads
    chinese = [r for r in results if "chinese" in r["lang"] or "zh" in r["lang"] or any(c in r["title"] for c in "的中文")]
    if not chinese:
        print("No Chinese translation found for this title.")
        sys.exit(1)

    chinese.sort(key=lambda r: r["downloads"], reverse=True)
    best = chinese[0]
    print(f"Best match: {best['title']} ({best['downloads']} downloads)")

    dl_url = get_download_link(session, best["url"])
    if not dl_url:
        print("Failed to get download link.")
        sys.exit(1)

    print("Downloading...")
    resp = session.get(dl_url, stream=True, timeout=60)
    resp.raise_for_status()

    filename = resp.headers.get("Content-Disposition", "")
    name_match = re.search(r'filename[^;=\n]*=((["\']).*?\2|[^;\n]*)', filename)
    if name_match:
        raw_name = name_match.group(1).strip("\"'")
    else:
        raw_name = f"{book_title[:50].replace(' ', '_')}.pdf"

    filepath = os.path.join(DOWNLOAD_DIR, raw_name)
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"Downloaded: {filepath} ({file_size_mb:.1f} MB)")

    # Convert to PDF if needed
    final_path = convert_to_pdf(filepath)
    if final_path != filepath:
        print(f"Converted to PDF: {final_path}")

    print(f"\nDone! Saved to: {final_path}")


if __name__ == "__main__":
    main()
