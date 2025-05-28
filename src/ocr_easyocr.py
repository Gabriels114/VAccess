# ocr_easyocr.py

import easyocr
import cv2

# Inicializa el lector de EasyOCR una sola vez
reader = easyocr.Reader(['en'], gpu=True)  # usa gpu=True si tienes CUDA, si no usa False

def ocr_from_image(image):
    """
    Aplica OCR a una imagen preprocesada de una placa vehicular.

    :param image: Imagen preprocesada (binaria o en escala de grises)
    :return: Texto reconocido (str)
    """
    # EasyOCR requiere imagen en formato RGB o escala de grises
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    results = reader.readtext(image)

    # Extrae el texto más probable con mayor confianza
    text_detected = ""
    highest_confidence = 0
    for (bbox, text, conf) in results:
        if conf > highest_confidence:
            highest_confidence = conf
            text_detected = text

    return text_detected.strip()

# Para pruebas rápidas
if __name__ == "__main__":
    img_path = "placa_binaria.jpg"
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    texto = ocr_from_image(img)
    print("Texto reconocido:", texto)
