from scrapper import init_scrapper, scrapper

URL = "https://www.yogonet.com/international/"

if __name__ == "__main__":
    driver = init_scrapper(URL)
    df = scrapper(driver)


