---
name: zlibrary-downloader
description: Search and download books from Z-Library (z-library.sk) by title, preferring Chinese translations with highest popularity. Auto-convert non-PDF files to PDF via Calibre ebook-convert. Saves to ~/Downloads/books/.
---

# Z-Library Downloader

从 Z-Library 按书名搜索和下载书籍，自动选择中文翻译中热度最高的版本，下载为 PDF。

## Workflow

1. **Receive book title** from user
2. **Search** z-library.sk with the title, filter by language (Chinese)
3. **Select** the most popular (highest downloads/rating) Chinese translation result
4. **Download** the file to `~/Downloads/books/`
5. **Convert to PDF** if downloaded file is not already PDF (via `ebook-convert`)
6. **Report** result (path, original format, PDF path)

## Prerequisites

- `python3` with `requests`, `beautifulsoup4`
- `calibre` (for `ebook-convert`), install: `pip install calibre` or system package

## First Use (Login)

Run the login helper once to save session cookies:
```
python3 scripts/zlibrary_login.py
```
This will prompt for Z-Library credentials via browser or token. Cookies saved to `~/.zlibrary_cookies.json`. Subsequent runs reuse this file automatically.

## Exclusion Rules

- Skip if no Chinese translation found
- Skip if download fails after 3 retries
- Do NOT handle DOI/ISBN-only searches
- Do NOT handle期刊论文下载

## Output Contract

After download, report to user:
```
Title: {书名}
Format: {原始格式} → PDF
Path: ~/Downloads/books/{filename}.pdf
```
