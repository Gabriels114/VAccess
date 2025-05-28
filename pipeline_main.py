from src.yolo_dectector import detect_license_plate
from src.preprocess import preprocess_plate_image
from src.ocr_easyocr import perform_ocr
from src.visualize import show_results

# Ruta de la imagen a procesar
#IMAGE_PATH = "assets/coche.jpeg"

def main():
    # Paso 1: Detección y recorte
    img, cropped = detect_license_plate(IMAGE_PATH)
    if cropped is None:
        print("No se detectó ninguna placa.")
        return

    # Paso 2: Preprocesamiento
    processed = preprocess_plate_image(cropped)

    # Paso 3: OCR
    text = perform_ocr(processed)
    print("Texto reconocido:", text)

    # Paso 4: Visualización
    show_results(img, cropped, processed, text)

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # Necesario en Windows
    main()
