# Check Multiple URLs with Nettarkivet

This repository contains the necessary code to run a web-app that will take a list of URLs, and check if they are indexed in Nettarkivet's replay service.

## Basic functionality
The app in principle allows you to:
- upload or paste multiple URLs
- get results in form of a table with information about each URL's index status, number of versions and link to replay

## Usage
The app is hosted [online at Streamlit](https://nlnwa-check-urls.streamlit.app/). However, this service is very slow. You will have a far quicker and better experience if you download and run the app locally.

### Download
1. Download the latest [release version](https://www.github.com/joncto/ibsen-cdx-app/release/...).
2. Unzip the downloaded file.

### Run app
3. First, you need to install dependencies. In your terminal, type:
```python3
pip install requirements.txt
```

4. Now, run the app by typing:
```python3
streamlit run app.py
```

A new window should open in your browser.

### Use the app
To enter URLs you want to look up in Nettarkivet, you can either:
a) upload a .txt file with one URL per line, or
b) paste URLs in the text input field.

Make sure that you only have one URL per line, and not to add any commas in the end of the URL.

When you are ready, press the button **"Slå opp URLer".**

3. Open your terminal and navigate to the app's location
    