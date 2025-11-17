#!/usr/bin/env python3

import io
import json
from urllib.parse import urlencode
import pandas as pd
import requests
import streamlit as st


CDX_BASE = "https://nettarkivet.nb.no/search/cdx"
REPLAY_BASE = "https://nettarkivet.nb.no/search/"


def build_cdx_url(original_url: str) -> str:
    """
    Takes a URL as input and
    returns a CDX query URL that will request a JSON response from nettarkivet's CDX Server API.
    """
    params = {"url": original_url, "output": "json"}
    return f"{CDX_BASE}?{urlencode(params)}"


def query_cdx(original_url: str) -> tuple[int, str | None]:
    """
    Takes a CDX query URL, sends a request to nettarkivets CDX Server API, then
    extracts information from the JSON response and
    returns the number of indexed versions and the value of the earliest timestamp (if any).
    """
    cdx_url = build_cdx_url(original_url)
    resp = requests.get(cdx_url, timeout=30)
    resp.raise_for_status()

    timestamps: list[str] = []

    for line in resp.text.splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue

        if isinstance(rec, dict):
            ts = rec.get("timestamp")
            if ts:
                timestamps.append(str(ts))

    if not timestamps:
        return 0, None

    return len(timestamps), min(timestamps)


def build_replay_url(original_url: str, timestamp: str | None) -> str | None:
    """
    Takes a URL and timestamp, combines them with the replay base URL, then
    returns a valid link to view URL in replay.
    """
    if not timestamp:
        return None
    return f"{REPLAY_BASE}{timestamp}/{original_url}"


def main():
    # Streamlit UI
    st.set_page_config(
        page_title="Slå opp i nettarkivet",
        page_icon="⚙️",
        # layout="wide",
    )

    st.title("Slå opp URLer i nettarkivets indeks")

    st.markdown(
        """
        Denne webappen lar deg sjekke om en URL er indeksert til visning i nettarkivet.
        
        Du kan både:

        a) Laste opp en tekstfil (.txt) med én URL per linje,

        b) Lime inn URLer i tekstfeltet under, men én URL per linje.
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


    # Collect URLs from file and text input
    urls: list[str] = []

    # From uploaded file
    if uploaded_file is not None:
        for raw_line in uploaded_file:
            line = raw_line.decode("utf-8", errors="ignore").strip()
            if line:
                urls.append(line)

    # From text input
    if pasted_urls_text.strip():
        for line in pasted_urls_text.splitlines():
            url = line.strip()
            if url:
                urls.append(url)

    if not urls:
        st.warning("Ingen URLer funnet. Last opp en fil eller lim inn URLer.")
        return

    max_rows_to_display = 200

    st.info(f"Fant {len(urls)} URLer. Slår opp i indeksen ...")

    progress_bar = st.progress(0, text="Starter ...")
    results = []

    total = len(urls)

    for i, url in enumerate(urls, start=1):
        try:
            count, earliest_ts = query_cdx(url)
        except Exception:
            count, earliest_ts = 0, None

        replay_url = build_replay_url(url, earliest_ts)
        indexed = "JA" if count > 0 else "NEI"

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

    # Generate DataFrame and show table
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
                "Replay",
                display_text="Åpne i visning",
            )
        },
    )

    # Excel download
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
    main()
