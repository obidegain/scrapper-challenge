# Scrapper Home Challenge

## Description

This project implements an automatic pipeline that run a web scraping of Yogonet web (`https://www.yogonet.com/international/`), extracts the main data, process the extracted data with some metrics and save the results in Google BigQuery. 

## Main Features

* **Web Scraping:** Throught Selenium and WebDriver-Manager, the script extract Title, Kicker, URL article and URL image of each Yogonet New.
* **Data Processing:** Calculate additional metrics with Pandas:
  * Words count.
  * Chars count.
  * List of Title Words.
* **Bigquery integrataion:** Upload the processed data to BigQuery Table.

## Main Technologies

* **Language Code:** Python 3.10+
* **Web scraping:** Selenium, WebDriver-Manager
* **Data Processing: ** Pandas
* **Cloud:** Google Cloud Platform (GCP)
  * **Storage Data:** BigQuery


## Config and Requirements

### 1. Google Cloud Platform (GCP)

* **Create a new project:** Get your **"GCP_PROJECT_ID"**
* **Grant API:** 
  * Go to "API and services" -> "Library"
  * Search "BigQuery API"
  * GRANT or "HABILITAR
* **Create your dataset and table:**
  * Go to BigQuery
  * Create a Dataset -> Get your **"BQ_DATASET_ID"**
  * Create a table -> Get your **"BQ_TABLE_ID"**

### 2. Local Config
* **Create a Virtual Environment**

```bash
    python -m venv .venv
    source .venv/bin/activate
```

* **Install dependencies**

```bash
    pip install -r requirements.txt
```

* **Create a .env file with your credentials**
If you want to run the project local, it's necessary that provides your credentials.

You could create a .env file with the follow variables. (Verify that .env is included in .gitignore file to don't push a critical data)
```bash
GCP_PROJECT_ID=your_project_id
BQ_DATASET_ID=your_dataset_id
BQ_TABLE_ID=your_table_id
```

* **Run BigQuery Connection from local**
If you want to connect to BigQuery it's necessary local auth. That's allows you, use your GCP credentials as secutiry way.

```bash
gcloud auth application-default login
```

### 3. Local Execution

* **Activate venv**

In your local folder, run:
```bash
    source .venv/bin/activate
```

Run your static scrapper:
```bash
    python main.py
```