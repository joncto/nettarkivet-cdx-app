# Query Index for multiple URLs

This repository provides tooling to check if a list of URLs are indexed in the Norwegian Web Archive (Nettarkivet) using pywb's CDX Server API. For all URLs that are indexed, it also returns the number of versions and a link to replay.

## Basic functionality
The web-app and CLI tool:
- takes a list of URLs as input,
- uses pywb's CDX Server API to query the Norwegian Web Archive's index,
- checks if each URL is indexed,
- counts the number of versions/captures for each URL,
- creates a link to replay of each URL,
- outputs the result as an Excel file

## Easy-to-use web-app
For an easy-to-use interface, you can use a Streamlit web app (`app.py`).
It is deployed at <url>, but can also be run locally from a terminal using python.

## Command-Line Interface (CLI)
Advanced users who prefers to use a command-line interface (CLI) can do the same in a terminal.

First, make sure that the necessary packages are installed, by running:
`pip install argparse csv urllib.parse urlencode requests`

Then, run the following line in their terminal:
`python3 check-URLs-count.py urls.txt -o output.csv`

`urls.txt` are used as input, containing one URL per line.
`-o output.csv` specifies the name of the output CSV file.