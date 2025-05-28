# pipeline_main.py

import cv2
from yolo_detector import detect_plate
from preprocess import crop_and_preprocess
from ocr_easyocr import recognize_text
from visualize import draw_detection, show_image, save_image

def main():
    image_path = "coche.jpeg"
    model_path = "runs/detect/placas_s3/weights/best.pt"
    save_path = "output_result.jpg"

    # 1. Cargar imagen
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"No se encontró la imagen: {image_path}")

    # 2. Detección de placa
    result = detect_plate(img, model_path, conf_threshold=0.25)
    if result is None:
        print("No se detectaron placas.")
        return

    x1, y1, x2, y2 = result["bbox"]

    # 3. Recorte y preprocesamiento
    plate_region = crop_and_preprocess(img, (x1, y1, x2, y2))

    # 4. Aplicar OCR
    text = recognize_text(plate_region)
    print(f"Texto reconocido: {text}")

    # 5. Visualizar y guardar resultados
    final_img = draw_detection(img.copy(), (x1, y1, x2, y2), label=text)
    show_image(final_img)
    save_image(final_img, save_path)

if __name__ == "__main__":
    main()
