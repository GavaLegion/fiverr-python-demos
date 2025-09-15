#!/usr/bin/env python3
"""Simple scraper
Usage examples:
python main.py --input urls.txt --output results.csv --selector "h1" --delay 1
python main.py --url https://example.com --output single.csv --selector "h1"
"""
import argparse
import csv
import logging
import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FiverrDemo/1.0)"}

def fetch(url: str, timeout: int = 10) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logging.warning(f"Failed to fetch {url}: {e}")
        return None

def extract(html: str, selector: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Попробуем CSS selector, иначе как tag name
    element = None
    try:
        element = soup.select_one(selector)
    except Exception:
        element = None
    if not element:
        element = soup.find(selector)
    if not element:
        return ""
    return element.get_text(strip=True)

def read_urls_from_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="file with URLs (one per line)")
    group.add_argument("--url", help="single URL to scrape")
    parser.add_argument("--output", required=True, help="output CSV file")
    parser.add_argument("--selector", default="h1", help="CSS selector or tag to extract (default: h1)")
    parser.add_argument("--delay", type=float, default=1.0, help="delay between requests in seconds")
    parser.add_argument("--timeout", type=int, default=10, help="request timeout")
    args = parser.parse_args()

    if args.input:
        urls = read_urls_from_file(args.input)
    else:
        urls = [args.url]

    results = []
    for url in urls:
        html = fetch(url, timeout=args.timeout)
        if html:
            text = extract(html, args.selector)
        else:
            text = ""
        results.append({"url": url, "text": text})
        time.sleep(args.delay)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "text"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    main()