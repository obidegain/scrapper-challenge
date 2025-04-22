# Scrapper Home Challenge

## Description

This project implements an automatic pipeline that run a web scraping of Yogonet web (`https://www.yogonet.com/international/`), extracts the main data, process the extracted data with some metrics and save the results in Google BigQuery. The extract process have two ways: one of them static (with fixed references) and the second dynamic (with ai help to extract data from specifics html elements).

## Main Features

* **Web Scraping:** Through Selenium and WebDriver-Manager, the script extract Title, Kicker, URL article and URL image of each Yogonet New.
* **Dynamic Extraction:** Though Gemini AI, the script extract Title, Kicker, URL article and URL image of each Yogonet New.
* **Data Processing:** Calculate additional metrics with Pandas:
  * Words count.
  * Chars count.
  * List of Title Words.
* **Bigquery integrataion:** Upload the processed data to BigQuery Table.
* **Dockerization:** Python, libraries, system dependencies and Google Chrome handless in one DockerFile.

## Main Technologies

* **Language Code:** Python 3.10+
* **Web scraping:** Selenium, WebDriver-Manager
* **Data Processing:** Pandas
* **Dynamic Extraction**: Vertex AI (Gemini 1.5 Flash), google-cloud-aiplatform
* **Cloud:** Google Cloud Platform (GCP)
  * **Storage Data:** BigQuery
  * **Container Register:** Google Artifact Registry
  * **Serverless:** Google Cloud Run (jobs)
* **Container:** Docker



## Config and Requirements

### 1. Google Cloud Platform (GCP) - Setup

* **Create a new project:** Get your `"GCP_PROJECT_ID"`
* **Grant API:** 
  * Go to "API and services" -> "Library"
  * Search `BigQuery API`
  * GRANT or "HABILITAR
  * `Vertex AI API`
  * `Artifact Registry API`
  * `Cloud Run Admin API`
* **Create a ServiceAccount (SA)** (Recommended to local tries)
  * Go to IAM -> Service Account -> Create service account
  * Create a name (example: `scrapper-challenge-sa`)
  * Grant IAM Roles to service account:
    * `Vertex AI User`
    * `BigQuery Data Editor`
* **Create your dataset and table:**
  * Go to BigQuery
  * Create a Dataset -> Get your `"BQ_DATASET_ID"`
  * Create a table -> Get your `"BQ_TABLE_ID"`

If you want to run your scrip locally, you must download the gcp_key to your local environment.
* Go to your service account -> keys -> add key -> Create new Key -> JSON
* DON'T PUSH THIS .JSON FILE TO GITHUB.
* Rename the file to `gcp_key.json`


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
VERTEX_AI_REGION=your_vertex_ai_region
```

* **Authenticate `gcloud` CLI**

```bash
gcloud auth login
gcloud config set project TU_PROJECT_ID
gcloud auth application-default login
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

## Execute the project with Docker
* **Build the image:** You must do it only once or after any code change. You can put any name, in this example the image name is: "scrapper-challenge-image"
```bash
docker build -t scrapper-challenge-image .
```

* **Execute the container without GCP access:** Only Scraping and Process Data
```bash
docker run -rm -it scrapper-challenge-image
```

* **Execute the container with GCP access:** Scrapping + Procces Data (static or dynamic) + Storage in BigQuery
```bash
docker run --rm -it \
  -e GCP_PROJECT_ID="YOUR_PROJECT_ID_" \
  -e VERTEX_AI_REGION="YOUR_VERTEX_AI_REGION" \
  -e BQ_DATASET_ID="YOUR_BQ_DATASET_ID" \
  -e BQ_TABLE_ID="YOUR_BQ_DATASET_ID" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/gcp_key.json" \
  -v /path/to/your/project/gcp_key.json:/app/gcp_key.json:ro \
  scrapper-challenge-image
```
(Note: to use the AI option (use_ai=True), it's necessary modify main.py and build the image again or pass the arg as env arg to the container to control this flag. ie: -e USE_AI=True).


## Cloud Run Deploy

The script `deploy.sh` automatize this process.

### 1. Config `deploy.sh`:
Open the file and edit the variables that appears in `CONFIG` section with your IDs.

### 2. Give execution file permission
```bash
chmod +x deploy.sh
```

### 3. Execute the deployment
The script will build the image, upload it to Artifact Registry and deploy the Job in Cloud Run 
```bash
./deploy.sh
```

### 4. Execute the Job in the Cloud Run
After the deployment, you could execute the job manually from GCP console (Cloud Run -> Jobs -> Select your job -> Run) or using `gcloud`:
```bash
gcloud run jobs execute your-job-name --region your_regin_name --project your_project_name --wait
```

ie:
```bash
gcloud run jobs execute scrapper-challenge--job --region us-central1 --project scrapperchallenge --wait
```