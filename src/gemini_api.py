# src/gemini_api.py

import os
import base64
import requests
import mimetypes  # Para detectar el tipo MIME de la imagen

# --- CONFIGURA ESTO ---
# TU API KEY DE GEMINI (Obtenla desde Google AI Studio: https://aistudio.google.com/app/apikey)
# Es MUY recomendable configurarla como una variable de entorno.
GEMINI_API_KEY = os.getenv("AIzaSyAf9WKK2FWpmBX4fd7C6o4Ycjs0M5pFCU0")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "AIzaSyAf9WKK2FWpmBX4fd7C6o4Ycjs0M5pFCU0"  # REEMPLAZA ESTO
    if GEMINI_API_KEY == "A":
        raise ValueError(
            "Por favor, configura tu GEMINI_API_KEY como variable de entorno "
            "o directamente en el script (no recomendado para producción)."
        )

# Endpoint correcto para Gemini Pro Vision
GEMINI_PRO_VISION_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={GEMINI_API_KEY}"

HEADERS = {
    "Content-Type": "application/json"
}


def get_license_plate_text(image_path: str) -> str | None:
    """
    Envía una imagen a Gemini Pro Vision para detectar la placa y extraer su texto.
    Combina la detección y el OCR en una sola llamada, como es el diseño de Gemini Vision.

    Args:
        image_path (str): Ruta al archivo de imagen.

    Returns:
        str | None: El texto de la placa detectado, o None si hay un error o no se encuentra.
    """
    if not os.path.exists(image_path):
        print(f"Error: El archivo de imagen no se encontró en '{image_path}'")
        return None

    # 1. Leer la imagen y codificarla en base64
    try:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        print(f"Error al leer o codificar la imagen: {e}")
        return None

    # 2. Determinar el tipo MIME de la imagen
    mime_type = mimetypes.guess_type(image_path)[0]
    if not mime_type or not mime_type.startswith("image/"):
        print(
            f"Advertencia: No se pudo determinar un tipo MIME de imagen válido para '{image_path}' (detectado: {mime_type}). Usando image/jpeg por defecto.")
        mime_type = "image/jpeg"  # Un default razonable, pero podría no ser siempre correcto

    # 3. Crear el Prompt para Gemini
    # Este prompt le indica a Gemini qué hacer con la imagen.
    prompt_text = (
        "Analiza esta imagen de un vehículo. "
        "Encuentra la placa de matrícula (license plate, patente, tablilla o chapa). "
        "Luego, extrae y devuelve únicamente el texto alfanumérico exacto que aparece en esa placa de matrícula. "
        "Si no puedes leer claramente el texto de la placa o no hay una placa visible, "
        "responde con la frase 'PLACA NO LEGIBLE'."
    )

    # 4. Construir el Payload para la API de Gemini
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text},  # La instrucción textual
                    {
                        "inline_data": {  # La imagen
                            "mime_type": mime_type,
                            "data": base64_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {  # Opcional, para controlar la salida
            "temperature": 0.1,
            "maxOutputTokens": 50  # Las placas no suelen tener más de 50 caracteres
        }
        # Puedes añadir "safetySettings" si necesitas ajustar los filtros de contenido
    }

    # 5. Realizar la Petición a la API
    try:
        response = requests.post(GEMINI_PRO_VISION_ENDPOINT, headers=HEADERS, json=payload, timeout=60)
        response.raise_for_status()  # Esto lanzará un error para respuestas 4xx/5xx

        data = response.json()

        # 6. Procesar la Respuesta
        if 'promptFeedback' in data and 'blockReason' in data['promptFeedback']:
            reason = data['promptFeedback']['blockReason']
            print(f"Advertencia: La solicitud fue bloqueada por Gemini. Razón: {reason}")
            return None

        if 'candidates' in data and data['candidates']:
            candidate = data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content'] and candidate['content']['parts']:
                plate_text_response = candidate['content']['parts'][0].get('text', "")

                if "PLACA NO LEGIBLE" in plate_text_response.upper():
                    print("Gemini indicó que la placa no es legible.")
                    return None
                # Aquí podrías añadir validaciones adicionales si esperas un formato específico
                return plate_text_response.strip()
            else:
                print("Respuesta de Gemini no contiene la estructura esperada para el texto ('content.parts').")
                print("Respuesta completa:", data)
                return None
        else:
            print("Respuesta de Gemini no contiene 'candidates' o está vacía.")
            print("Respuesta completa:", data)
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        if hasattr(http_err, 'response') and http_err.response is not None:
            print(f"Cuerpo de la respuesta del error: {http_err.response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error en la solicitud a Gemini: {req_err}")
    except Exception as e:
        print(f"Un error inesperado ocurrió: {e}")
        # Podrías querer ver 'data' aquí también si el error ocurre después de data = response.json()
        # pero antes de que se procese completamente.
        # if 'data' in locals():
        #    print("Datos de respuesta parciales (si disponibles):", data)

    return None


# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    # Debes tener una imagen llamada 'test_car.jpg' en el mismo directorio
    # o cambiar la ruta a una imagen existente.
    test_image_path = "test_car.jpg"


    # Crear una imagen de prueba si no existe (requiere Pillow)
    def create_dummy_image_if_not_exists(path):
        if not os.path.exists(path):
            try:
                from PIL import Image, ImageDraw, ImageFont
                print(f"Creando imagen de prueba '{path}'...")
                img = Image.new('RGB', (600, 200), color=(120, 120, 120))
                d = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("arial.ttf", 60)
                except IOError:
                    font = ImageFont.load_default()
                d.text((50, 60), "ABC-123", fill=(255, 255, 0), font=font)
                img.save(path)
                print("Imagen de prueba creada.")
            except ImportError:
                print("Pillow no está instalado. No se pudo crear la imagen de prueba.")
                print(
                    f"Por favor, crea manualmente un archivo '{path}' o instala Pillow (`pip install Pillow`) y re-ejecuta.")
            except Exception as e_img:
                print(f"Error creando imagen de prueba: {e_img}")


    create_dummy_image_if_not_exists(test_image_path)

    if os.path.exists(test_image_path):
        print(f"Intentando reconocer placa desde: {test_image_path}")
        plate_text = get_license_plate_text(test_image_path)

        if plate_text:
            print(f"\nTexto de la placa detectado: '{plate_text}'")
        else:
            print("\nNo se pudo obtener el texto de la placa o no era legible.")
    else:
        print(f"La imagen de prueba '{test_image_path}' no existe. Por favor, créala o proporciona una ruta válida.")