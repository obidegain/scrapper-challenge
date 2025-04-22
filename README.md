# Scrapper Home Challenge

## Description

This project implements an automatic pipeline that run a web scraping of Yogonet web (`https://www.yogonet.com/international/`), extracts the main data and process the extracted data with some metrics. 

## Main Features

* **Web Scraping:** Throught Selenium and WebDriver-Manager, the script extract Title, Kicker, URL article and URL image of each Yogonet New.
* **Data Processing:** Calculate additional metrics with Pandas:
  * Words count.
  * Chars count.
  * List of Title Words.

## Main Technologies

* **Language Code:** Python 3.10+
* **Web scraping:** Selenium, WebDriver-Manager


## Config and Requirements

### 1. Local Config
* **Create a Virtual Environment**

```bash
    python -m venv .venv
    source .venv/bin/activate
```

* **Install dependencies**

```bash
    pip install -r requirements.txt
```

## Local Execution

* **Activate venv**

In your local folder, run:
```bash
    source .venv/bin/activate
```

Run your static scrapper:
```bash
    python main.py
```