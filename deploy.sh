#!/bin/bash

set -e
set -u
set -o pipefail

# --- CONFIG ---
GCP_PROJECT_ID="YOUR_GCP_PROJECT_ID"
GCP_REGION="YOUR_GCP_REGION"
ARTIFACT_REGISTRY_REPO="YOUR_ARTIFACT_REGISTRY_REPO"
DOCKER_IMAGE_NAME="YOUR_DOCKER_IMAGE_NAME"
CLOUD_RUN_JOB_NAME="YOUR_CLOUD_RUN_JOB_NAME"
BQ_DATASET="YOUR_BQ_DATASET_ID"
BQ_TABLE="YOUR_BQ_TABLE_ID"

# Image name for Artifact Registry
IMAGE_TAG="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${DOCKER_IMAGE_NAME}:latest"


# --- 2. Grant APIs needed ---
echo "\n>>> Habilitando APIs necesarias..."
gcloud services enable run.googleapis.com \
                       artifactregistry.googleapis.com \
                       bigquery.googleapis.com \
                       --project="${GCP_PROJECT_ID}"

# --- 3. Create repo in Artifact Registry (if doesn't exists) ---
echo "\n>>> Verificando/Creando Repositorio en Artifact Registry..."
if ! gcloud artifacts repositories describe "${ARTIFACT_REGISTRY_REPO}" --location="${GCP_REGION}" --project="${GCP_PROJECT_ID}" > /dev/null 2>&1; then
  echo "Creando repositorio '${ARTIFACT_REGISTRY_REPO}' en '${GCP_REGION}'..."
  gcloud artifacts repositories create "${ARTIFACT_REGISTRY_REPO}" \
    --repository-format=docker \
    --location="${GCP_REGION}" \
    --description="Repositorio para el scraper de Yogonet" \
    --project="${GCP_PROJECT_ID}"
else
  echo "Repositorio '${ARTIFACT_REGISTRY_REPO}' ya existe."
fi

# --- 4. Config Docker to authenticate in Artifact Registry ---
echo "\n>>> Configurando autenticación de Docker..."
gcloud auth configure-docker "${GCP_REGION}-docker.pkg.dev" --quiet


# --- 5. Build the Docker Image ---
echo "\n>>> Construyendo la imagen Docker: ${IMAGE_TAG}"
docker build -t "${IMAGE_TAG}" .


# --- 6. Upload the Docker Image to Artifact Registry ---
echo "\n>>> Subiendo la imagen a Artifact Registry..."
docker push "${IMAGE_TAG}"


# --- 7. Deploy (or update) the Job in Cloud Run ---
echo "\n>>> Desplegando/Actualizando el Job en Cloud Run: ${CLOUD_RUN_JOB_NAME}"

# Args to deploy the Cloud Run job
deploy_args=(
  "${CLOUD_RUN_JOB_NAME}"
  "--image=${IMAGE_TAG}"
  "--region=${GCP_REGION}"
  "--project=${GCP_PROJECT_ID}"
  # bigquery variables
  "--set-env-vars=GCP_PROJECT=${GCP_PROJECT_ID},BQ_DATASET=${BQ_DATASET},BQ_TABLE=${BQ_TABLE}"
  # timeout
  "--task-timeout=15m"
  # retries if fail the job
  "--max-retries=1"
)

# Run the deploy command
gcloud run jobs deploy "${deploy_args[@]}"

echo "\n--- ¡Despliegue completado! ---"
echo "Job '${CLOUD_RUN_JOB_NAME}' desplegado/actualizado en la región '${GCP_REGION}'."
echo "Puedes ejecutarlo manualmente con:"
echo "gcloud run jobs execute ${CLOUD_RUN_JOB_NAME} --region ${GCP_REGION} --project ${GCP_PROJECT_ID} --wait"