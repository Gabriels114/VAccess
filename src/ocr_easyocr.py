# ocr_easyocr.py
# src/ocr_easyocr.py

import os
import cv2
import torch
import easyocr

# Detectar si hay GPU disponible
_GPU = torch.cuda.is_available()

# Inicializar el lector EasyOCR solo una vez, con soporte para español e inglés
_reader = easyocr.Reader(['es', 'en'], gpu=_GPU)

def perform_ocr(image):
    """
    Aplica OCR a una imagen preprocesada (binaria o en escala de grises).

    Args:
        image (np.ndarray): Imagen preprocesada (escala de grises o BGR).

    Returns:
        str: Texto reconocido (la línea con mayor confianza).
    """
    # Si viene en BGR, convertimos a escala de grises
    if image.ndim == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Ejecutar OCR
    results = _reader.readtext(image, detail=1, paragraph=False)

    # Buscar el texto con mayor confianza
    best_text = ""
    best_conf = 0.0
    for bbox, text, conf in results:
        if conf > best_conf:
            best_conf = conf
            best_text = text

    return best_text.strip()


if __name__ == "__main__":
    # Prueba rápida (asegúrate de tener este archivo en la raíz del proyecto)
    test_img_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'coche.jpeg')
    img = cv2.imread(test_img_path, cv2.IMREAD_GRAYSCALE)
    texto = perform_ocr(img)
    print("Texto reconocido:", texto)
