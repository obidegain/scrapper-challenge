from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from scrapper_vertex_ai import extract_data_ai, init_vertex_ai
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
VERTEX_AI_REGION = os.environ.get("VERTEX_AI_REGION", "")


def init_scrapper(url):
    """
    Initialize the web scrapper with the given URL.

    :param url: The URL to scrape.
    :return: webdriver instance.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")

    try:
        service = ChromeService(ChromeDriverManager().install())
        bot = webdriver.Chrome(service=service, options=options)
        bot.get(url)
        return bot
    except Exception as e:
        print(f"Error durante la inicialización o navegación inicial: {e}")
        return None


def get_only_news_from_all_cls(all_inner_classes: list) -> list:
    """
    Get only news classes from all classes found.

    :param all_inner_classes: Set of all classes found.
    :return: List of news classes.
    """
    news_classes = []
    for cls in all_inner_classes:
        if "noticia" in cls:
            news_classes.append(cls)
    return news_classes


def extract_main_data(new_element: WebElement) -> dict:
    data = {
        'orden': None,
        'kicker': None,
        'title': None,
        'link': None,
        'image_href': None,
        'image_src': None
    }

    if not isinstance(new_element, WebElement):
        print("Error: La entrada debe ser un WebElement de Selenium.")
        return data

    try:
        try:
            data['orden'] = new_element.get_attribute('orden')
        except Exception as e:
            print(f"Error al obtener el atributo orden")

        try:
            kicker_element = new_element.find_element(By.CSS_SELECTOR, '.volanta')
            data['kicker'] = kicker_element.text.strip()
        except Exception as e:
            print(f"Error al obtener el atributo kicker")

        try:
            title_h2 = new_element.find_element(By.CSS_SELECTOR, 'h2.titulo')
            link_a = title_h2.find_element(By.TAG_NAME, 'a')
            data['link'] = link_a.get_attribute('href')
            data['title'] = link_a.text.strip()
        except Exception as e:
            print(f"Error al obtener el atributo title")

        try:
            image_div = new_element.find_element(By.CSS_SELECTOR, 'div.imagen')
            imagen_link_a = image_div.find_element(By.TAG_NAME, 'a')
            data['image_href'] = imagen_link_a.get_attribute('href')
            imagen_img = imagen_link_a.find_element(By.TAG_NAME, 'img')
            data['image_src'] = imagen_img.get_attribute('src')
        except Exception as e:
            print(f"Error al obtener el atributo image_src")

    except Exception as e:
        print(f"Error al extraer datos del elemento: {new_element} ")

    return data


def create_df_and_calculate_columns(all_full_data):
    df = pd.DataFrame(all_full_data)
    df['title_word_count'] = df['title'].str.split().str.len()
    df['title_char_count'] = df['title'].str.len()
    df['title_capitalized_words'] = df['title'].str.split().apply(lambda x: ','.join([word for word in x if word.istitle()]))

    df['title_word_count'].astype(int)
    df['title_char_count'].astype(int)
    df['title_capitalized_words'].astype(str)
    return df


def scrapper(driver, use_ai=False):
    df = None

    if use_ai:
        model = init_vertex_ai(GCP_PROJECT_ID, VERTEX_AI_REGION)

    try:
        if driver:
            print("Esperando a que el contenido principal cargue...")
            timeout = 15
            css_selector_name_main_container = ".contenedor_general_estructura.estructura_home"
            all_full_data = []

            try:
                main_container = WebDriverWait(driver, timeout).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, css_selector_name_main_container)
                    )
                )

                css_selector_slot_and_news = '[class*="slot"][class*="noticia"]'

                all_classes_with_news = main_container.find_elements(By.CSS_SELECTOR, css_selector_slot_and_news)
                if all_classes_with_news:
                    print(f"Se encontraron {len(all_classes_with_news)} elementos con clase 'slot' y 'noticia'.")
                    for element in all_classes_with_news:
                        if use_ai:
                            html_str = element.get_attribute('outerHTML')
                            data = extract_data_ai(html_str, model)
                        else:
                            data = extract_main_data(element)
                        all_full_data.append(data)

                if all_full_data:
                    df = create_df_and_calculate_columns(all_full_data)
                    print("DataFrame creado con éxito.")

            except TimeoutError:
                print(f'Error: El tiempo de espera de {timeout} segundos se ha agotado. El contenido principal no se cargó.')
                return
            except Exception as e:
                print(f'Error: {e}')
                return

    finally:
        if driver:
            print("Cerrando el navegador...")
            driver.quit()
            print("El navegador ha sido cerrado.")
        return df

