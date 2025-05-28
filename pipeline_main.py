# pipeline_main.py


import os
import cv2
import multiprocessing
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from src.yolo_dectector import detect_license_plate
from src.preprocess import preprocess_plate_image
from src.ocr_easyocr import perform_ocr
from src.visualize import show_results
from src.gemini_api import get_license_plate_text



# Ruta de la imagen a procesar
IMAGE_PATH = "assets/coche.jpeg"

def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"[ERROR] No se encontró la imagen: {IMAGE_PATH}")
        return

    img = cv2.imread(IMAGE_PATH)

    # Paso 1: Detección con YOLO
    detection = detect_license_plate(img)
    if detection:
        x1, y1, x2, y2 = detection['bbox']
        cropped = img[y1:y2, x1:x2]
    else:
        print("[INFO] YOLO no detectó placa. Usando respaldo con Gemini...")
        gemini_text = get_license_plate_text(IMAGE_PATH)
        if gemini_text:
            print(f"[GEMINI] Texto detectado desde imagen completa: {gemini_text}")
        else:
            print("[GEMINI] No se pudo detectar placa con Gemini.")
        return  # No hay más que hacer si Gemini tampoco la detectó

    # Paso 2: Preprocesamiento
    processed = preprocess_plate_image(cropped)

    # Paso 3: OCR (antes y después del preprocesamiento)
    text_raw = perform_ocr(cropped)
    text_processed = perform_ocr(processed)

    # Elegir el resultado más confiable
    final_text = max([text_raw, text_processed], key=len)

    if not final_text or len(final_text) < 4 or not any(c.isdigit() for c in final_text):
        print("[INFO] OCR local falló. Usando respaldo con Gemini...")
        final_text = get_license_plate_text(IMAGE_PATH)

    # Mostrar resultados
    if final_text:
        print("[RESULTADO FINAL] Texto reconocido:", final_text)
    else:
        print("[ERROR] No se pudo reconocer el texto de la placa.")

    show_results(img, cropped, processed, final_text)

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # Necesario en Windows
    main()
