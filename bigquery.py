import os
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
BQ_DATASET_ID = os.environ.get("BQ_DATASET_ID", "")
BQ_TABLE_ID = os.environ.get("BQ_TABLE_ID", "")


def init_client():
    client = bigquery.Client(project=GCP_PROJECT_ID)
    table_ref = client.dataset(BQ_DATASET_ID).table(BQ_TABLE_ID)

    return client, table_ref


def create_table_if_not_exists(client, table_ref):
    try:
        client.get_table(table_ref)
        print(f"La tabla {BQ_TABLE_ID} ya existe.")
    except NotFound:
        print(f"La tabla {BQ_TABLE_ID} no existe. Creando...")
        schema = [
            bigquery.SchemaField("orden", "STRING"),
            bigquery.SchemaField("kicker", "STRING"),
            bigquery.SchemaField("title", "STRING"),
            bigquery.SchemaField("link", "STRING"),
            bigquery.SchemaField("image_href", "STRING"),
            bigquery.SchemaField("image_src", "STRING"),
            bigquery.SchemaField("title_word_count", "INTEGER"),
            bigquery.SchemaField("title_char_count", "INTEGER"),
            bigquery.SchemaField("title_capitalized_words", "STRING"),
            bigquery.SchemaField("scraped_timestamp", "TIMESTAMP")
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        print(f"Tabla {BQ_TABLE_ID} creada.")


def upload_data_to_bigquery(df, table_ref, client):
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = client.load_table_from_dataframe(
        df, table_ref, job_config=job_config
    )

    return load_job


def upload_data(df):
    try:
        client, table_ref = init_client()
        load_job = upload_data_to_bigquery(df, table_ref, client)
        load_job.result()

        print("Job finalizado.")

        if load_job.errors:
            print("Errores:")
            for error in load_job.errors:
                print(error)
        elif load_job.state == 'DONE':
            print(f"¡Listo! Cargadas {load_job.output_rows} fila(s) en la tabla '{BQ_TABLE_ID}'.")
        else:
             print(f"El job finalizo con el siguiente estado: {load_job.state}.")

        return load_job.output_rows

    except NotFound:
        print(f"--- ERROR ---")
        print(f"No se encontró el Dataset '{BQ_DATASET_ID}' o la tabla'{BQ_TABLE_ID}'.")
        return
    except Exception as e:
        print(f"--- ERROR INESPERADO ---")
        print(f"Error: {e}")
        return