import os
import json
from google.cloud import aiplatform
from vertexai.generative_models import (
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    GenerationResponse
)
import traceback
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
VERTEX_AI_REGION = os.environ.get("VERTEX_AI_REGION", "")

PROMPT_TEMPLATE = """
Eres un asistente experto en extraer información estructurada de código HTML.
Te proporcionaré el código HTML correspondiente a un único bloque (<div>) que representa un artículo de noticias del sitio web Yogonet.

Tu tarea es analizar este HTML e identificar semánticamente los siguientes componentes, incluso si las clases CSS o la estructura cambian ligeramente:
1.  El texto principal del **Título** del artículo.
2.  El texto del **Kicker** (la frase corta que a veces aparece justo encima del título). Si no encuentras un kicker claro, devuelve null o una cadena vacía.
3.  La **URL del Enlace** principal del artículo (generalmente el atributo 'href' de la etiqueta <a> asociada al título).
4.  La **URL de la Imagen** principal del artículo (generalmente el atributo 'src' de la etiqueta <img> principal asociada al artículo). Si no hay imagen clara, devuelve null o una cadena vacía.

Consideraciones/Pistas (pero no te limites estrictamente a ellas):
- El Título suele estar dentro de una etiqueta <h2> con clase 'titulo' y contiene un enlace <a>.
- El Kicker suele ser un texto corto en un <div> con clase 'volanta', ubicado cerca y antes del título.
- La Imagen principal suele estar dentro de un <div> con clase 'imagen', contenida a su vez en un enlace <a>. Extrae el 'src' de la <img>.

IMPORTANTE: Devuelve tu respuesta **únicamente** como un objeto JSON válido, utilizando exactamente las siguientes claves: "title_text", "kicker_text", "article_link_url", "image_src_url". No incluyas explicaciones, texto introductorio, ni marques de formato como ```json. Solo el objeto JSON.

HTML del bloque de noticia a analizar:
```html
{HTML}
"""

def init_vertex_ai(project_id: str = GCP_PROJECT_ID, location: str=VERTEX_AI_REGION) -> GenerativeModel | None:
    print(f"Inicializando Vertex AI (Proyecto: {project_id}, Región: {location})...")
    try:
        aiplatform.init(project=project_id, location=location)
        model = GenerativeModel("gemini-1.5-flash")
        print("Modelo Gemini inicializado exitosamente.")
        return model
    except Exception as e:
        print(f"Error CRÍTICO inicializando Vertex AI: {e}")
        print("Verifica que la API de Vertex AI esté habilitada y que tengas credenciales válidas.")
        traceback.print_exc()
        return None


def get_full_prompt(html_content: str, prompt_template: str = PROMPT_TEMPLATE) -> str:
    if "{HTML}" not in prompt_template:
        print("Advertencia: La plantilla del prompt no contiene el placeholder '{HTML}'.")
    return prompt_template.replace("{HTML}", html_content)


def request_to_gemini(prompt_final: str, model: GenerativeModel) -> GenerationResponse | None:

    print("  Llamando a la API de Gemini...")
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    response = model.generate_content(prompt_final, safety_settings=safety_settings)
    print("  Respuesta recibida de Gemini. Parseando...")
    return response


def parse_response(response_text: str) -> dict:
    try:
        data_extracted = {
            'title': None, 'kicker': None, 'link': None, 'image_src': None
        }

        cleaned_response_text = response_text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:-3].strip()
        elif cleaned_response_text.startswith("```"):
            cleaned_response_text = cleaned_response_text[3:-3].strip()

        # Parsear el JSON
        parsed_json = json.loads(cleaned_response_text)

        data_extracted['title'] = parsed_json.get('title_text')
        data_extracted['kicker'] = parsed_json.get('kicker_text')
        data_extracted['link'] = parsed_json.get('article_link_url')
        data_extracted['image_src'] = parsed_json.get('image_src_url')
        data_extracted['image_href'] = data_extracted['link']

        print("  Parseo JSON exitoso.")

        return data_extracted
    except Exception as e:
        print(f"Error al parsear la respuesta JSON: {e}")
        return None


def extract_data_ai(html_content: str, model: GenerativeModel) -> dict | None:
    try:
        prompt_final = get_full_prompt(html_content, PROMPT_TEMPLATE)
        response = request_to_gemini(prompt_final, model)
        data_extracted = parse_response(response.text)

        return data_extracted

    except Exception as e:
        print(f"  Error inesperado durante la llamada a Gemini o parseo: {e}")
        traceback.print_exc()
        return None