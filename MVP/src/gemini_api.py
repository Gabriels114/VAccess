# src/gemini_api.py

import os
import base64
import requests
import mimetypes

# --- CONFIGURACIÓN DE API KEY ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAf9WKK2FWpmBX4fd7C6o4Ycjs0M5pFCU0")
if not GEMINI_API_KEY or GEMINI_API_KEY == "TU_API_KEY_AQUÍ":
    raise ValueError(
        "Define la variable de entorno GEMINI_API_KEY "
        "o reemplaza el valor en el script (no recomendado)."
    )

# --- ENDPOINT según quickstart ---
GEMINI_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)

HEADERS = {"Content-Type": "application/json"}

def get_license_plate_text(image_path: str) -> str | None:
    """
    Envía una imagen a Gemini Pro Vision embebida dentro del payload de Generative
    Language (modelo gemini-2.0-flash) para extraer el texto de la matrícula.
    Devuelve la cadena de la placa o None.
    """
    if not os.path.exists(image_path):
        print(f"[gemini_api] Archivo no encontrado: {image_path}")
        return None

    # Leer y codificar la imagen en base64
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    b64_img = base64.b64encode(img_bytes).decode("utf-8")

    # Determinar MIME
    mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"

    # Quickstart-style payload: contents → parts
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Encuentra la placa de matrícula en esta imagen "
                            "y devuelve únicamente el texto exacto de la placa. "
                            "Si no la ves, responde 'PLACA NO LEGIBLE'."
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64_img
                        }
                    }
                ]
            }
        ]
    }

    try:
        resp = requests.post(GEMINI_ENDPOINT, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        candidates = data.get("candidates", [])
        if not candidates:
            print("[gemini_api] No se recibieron candidatos.")
            return None

        text = candidates[0]["content"]["parts"][0].get("text", "").strip()
        if "PLACA NO LEGIBLE" in text.upper():
            print("[gemini_api] La placa no es legible.")
            return None

        return text

    except requests.HTTPError as e:
        print(f"[gemini_api] HTTP Error: {e} - {e.response.text}")
    except Exception as e:
        print(f"[gemini_api] Error inesperado al llamar a Gemini: {e}")

    return None
