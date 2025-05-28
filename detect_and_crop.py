# detect_and_crop.py
from ultralytics import YOLO
import cv2
import os

def detect_plate(image_path, model_path="runs/detect/placas_s3/weights/best.pt"):
    model = YOLO(model_path)
    img = cv2.imread(image_path)
    results = model.predict(source=img, conf=0.25, save=False)

    for result in results:
        for i, box in enumerate(result.boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cropped = img[y1:y2, x1:x2]
            filename = f"placa_crop_{i}.png"
            cv2.imwrite(filename, cropped)
            print(f"Placa recortada guardada en: {filename}")
            return cropped  # Solo la primera placa detectada

# preprocess.py
import cv2
import numpy as np

def preprocess_plate(cropped_img):
    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    return thresh

# ocr_easyocr.py
import easyocr

def recognize_text(preprocessed_img):
    reader = easyocr.Reader(['es', 'en'])
    result = reader.readtext(preprocessed_img)
    for (bbox, text, prob) in result:
        print(f"Texto detectado: {text} con confianza {prob:.2f}")
    return result

# visualize.py
import cv2

def show_result(image, result):
    for (bbox, text, prob) in result:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, text, (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Resultado OCR", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# pipeline_main.py
from detect_and_crop import detect_plate
from preprocess import preprocess_plate
from ocr_easyocr import recognize_text
from visualize import show_result

if __name__ == "__main__":
    IMAGE_PATH = "coche.jpeg"

    # Paso 1: Detección y recorte
    cropped = detect_plate(IMAGE_PATH)

    # Paso 2: Preprocesamiento
    processed = preprocess_plate(cropped)

    # Paso 3: OCR
    ocr_result = recognize_text(processed)

    # Paso 4: Mostrar
    show_result(cropped, ocr_result)
