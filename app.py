#!/usr/bin/env python3
"""
This app:
- takes as input a list of URLs,
- uses pywb's CDX Server API to query nettarkivet's index,
- check if each URL is indexed,
- counts the number of indexed captures for each URL,
- creates a link to replay of each URL,
- outputs results as an Excel file

Input format:
- pasted text with one URL per line, or
- .txt with one URL per line.
"""

import argparse
import csv
from urllib.parse import urlencode
import requests
import io
import pandas as pd
import streamlit as st


CDX_BASE = "https://nettarkivet.nb.no/search/cdx"
REPLAY_BASE = "https://nettarkivet.nb.no/search/*/"


def build_cdx_url(original_url: str) -> str:
    """
    Take URL as input and builds a CDX query URL asking for json formatted responses.
    """
    params = {"url": original_url, "output": "json"}
    return f"{CDX_BASE}?{urlencode(params)}"


def build_replay_url(original_url: str) -> str:
    """
    Takes URL as input and constructs a replay URL.
    """
    return f"{REPLAY_BASE}{original_url}"


def count_cdx_hits(cdx_url: str) -> int:
    """
    Query pywb's CDX Server API and, for each JSON response, counts the number of indexed captures.
    """
    resp = requests.get(cdx_url, timeout=30)
    resp.raise_for_status()

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
        writer.writerow(["url", "indexed", "versions", "replay_url"])
        writer.writerows(rows)


# Old code for CLI interface

def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Tekstfil med én URL per linje")
    parser.add_argument("-o", "--output", default="cdx_counts.csv")
    args = parser.parse_args()

    urls = read_urls(args.input)
    results = []

    for url in urls:
        cdx_url = build_cdx_url(url)
        replay_url = build_replay_url(url)
        try:
            count = count_cdx_hits(cdx_url)
        except Exception as e:
            print(f"Error on {cdx_url}: {e}")
            count = 0

        indexed = "YES" if count > 0 else "NO"
        # url, indexed, versions, replay_url
        results.append((url, indexed, count, replay_url))

    write_csv(args.output, results)
    print(f"Ferdig. Skrev {len(results)} rader til {args.output}")


def main():
    # --- Streamlit UI ---
    st.set_page_config(
        page_title="Slå opp i nettarkivet",
        page_icon="🔎",
        layout="wide",
    )

    st.title("Slå opp URLer i Nettarkivets indeks")

    st.markdown(
        """
        Last opp en tekstfil med én URL per linje **eller** lim inn URLer i tekstfeltet under.
        Trykk på **«Slå opp URLer»** for å se om adressen finnes i indeks for offentlig visning,
        og evt. hvor mange versjoner som finnes i URLene mot Nettarkivets CDX-tjeneste.
        """
    )

    uploaded_file = st.file_uploader(
        "Last opp tekstfil (.txt) med én URL per linje",
        type=["txt"],
    )

    pasted_urls_text = st.text_area(
        "Lim inn URLer (én URL per linje)",
        height=200,
    )

    start = st.button("Slå opp URLer")

    if not start:
        return

    # --- Samle URLer fra fil og tekstfelt ---
    urls: list[str] = []

    # Fra opplastet fil
    if uploaded_file is not None:
        for raw_line in uploaded_file:
            line = raw_line.decode("utf-8", errors="ignore").strip()
            if line:
                urls.append(line)

    # Fra tekstfelt
    if pasted_urls_text.strip():
        for line in pasted_urls_text.splitlines():
            url = line.strip()
            if url:
                urls.append(url)

    if not urls:
        st.warning("Ingen URLer funnet. Last opp en fil eller lim inn URLer.")
        return

    max_rows_to_display = 800

    st.info(f"Fant {len(urls)} URLer. Slår opp i indeksen ...")

    progress_bar = st.progress(0, text="Starter ...")
    results = []

    total = len(urls)

    for i, url in enumerate(urls, start=1):
        cdx_url = build_cdx_url(url)
        replay_url = build_replay_url(url)

        try:
            count = count_cdx_hits(cdx_url)
        except Exception:
            count = 0

        indexed = "YES" if count > 0 else "NO"

        # Order: URL, Indexed, Versions, Replay
        results.append(
            {
                "URL": url,
                "Indexed": indexed,
                "Versions": count,
                "Replay": replay_url,
            }
        )

        progress = i / total
        progress_bar.progress(
            progress,
            text=f"{i} / {total} URLer slått opp",
        )

    st.success(f"Ferdig! Slått opp {total} URLer.")

    # --- Lag DataFrame og vis tabell (opptil 800 rader) ---
    df = pd.DataFrame(results, columns=["URL", "Indexed", "Versions", "Replay"])

    if len(df) > max_rows_to_display:
        st.info(
            f"Viser de første {max_rows_to_display} radene i tabellen. "
            f"Du kan laste ned en Excel-fil med alle {len(df)} radene."
        )
        df_to_show = df.head(max_rows_to_display)
    else:
        df_to_show = df

    st.subheader("Resultat")
    st.dataframe(
        df_to_show,
        use_container_width=True,
        column_config={
            "Replay": st.column_config.LinkColumn(
                "Replay",  # column label
                display_text="Åpne i nettarkivet",  # link text in the table
                    )
                },
            )

    # --- Excel-nedlasting ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="CDX counts")

    output.seek(0)

    st.download_button(
        label="Last ned som Excel",
        data=output,
        file_name="indekserte_urler.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


if __name__ == "__main__":
    # For å starte appen lokalt, åpne en terminal, gå til lokasjonen for fila og kjør kommandoen:
    #   `streamlit run app.py``
    #
    # Hvis du fortsatt vil bruke CLI-versjonen i terminalen,
    # kan du bytte til cli_main() her i stedet.
    main()
    # Eller, for CLI:
    # cli_main()
