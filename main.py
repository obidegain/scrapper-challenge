from scrapper import init_scrapper, scrapper
from bigquery import upload_data

URL = "https://www.yogonet.com/international/"

if __name__ == "__main__":
    driver = init_scrapper(URL)
    df = scrapper(driver)
    rows_uploaded = upload_data(df)

    print(f"Se subieron {rows_uploaded} filas a BigQuery.")

