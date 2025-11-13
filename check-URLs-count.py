#!/usr/bin/env python3
"""
This script:
- takes as input a list of URLs,
- uses pywb's CDX Server API to query nettarkivet's index
- counts the number of indexed captures for each URL
- outputs a CSV with the URL and the number of captures

Input format:
.txt with one URL per line.

Run the script:
`python3 check_urls_count.py urls.txt -o cdx_counts.csv`

"""

import argparse
import csv
from urllib.parse import urlencode
import requests


CDX_BASE = "https://nettarkivet.nb.no/search/cdx"


def build_cdx_url(original_url: str) -> str:
    """
    Take URL as input and builds a CDX query URL asking for json formatted responses.
    """
    params = {"url": original_url, "output": "json"}
    return f"{CDX_BASE}?{urlencode(params)}"

def count_cdx_hits(cdx_url: str) -> int:
    """
    Query pywb's CDX Server API and, for each JSON response, counts the number of indexed captures.
    """
    resp = requests.get(cdx_url, timeout=30)
    resp.raise_for_status()

    # NDJSON: one record per line
    return sum(1 for line in resp.text.splitlines() if line.strip())

def read_urls(path: str):
    """Read URLs from file, strip any leading or trailing whitespace."""
    cleaned = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            cleaned.append(url)
    return cleaned

def write_csv(path: str, rows: list[tuple]) -> None:
    """
    Write rows to CSV with two 'columns' (url, count)
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "count"])
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Tekstfil med én URL per linje")
    parser.add_argument("-o", "--output", default="cdx_counts.csv")
    args = parser.parse_args()

    urls = read_urls(args.input)
    results = []

    for url in urls:
        cdx_url = build_cdx_url(url)
        try:
            count = count_cdx_hits(cdx_url)
        except Exception as e:
            print(f"Error on {cdx_url}: {e}")
            count = 0

        results.append((url, count))

    write_csv(args.output, results)
    print(f"Ferdig. Skrev {len(results)} rader til {args.output}")


if __name__ == "__main__":
    main()