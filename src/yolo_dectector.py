# yolo_detector.py

from ultralytics import YOLO
import numpy as np

def detect_plate(img, model_path="runs/detect/placas_s3/weights/best.pt", conf_threshold=0.25):
    """
    Detecta una placa en la imagen usando un modelo YOLOv8.

    Args:
        img (np.ndarray): Imagen en formato OpenCV.
        model_path (str): Ruta al modelo YOLOv8 entrenado.
        conf_threshold (float): Umbral mínimo de confianza para detección.

    Returns:
        dict or None: Diccionario con 'bbox' (x1, y1, x2, y2) y 'conf', o None si no se detecta nada.
    """
    model = YOLO(model_path)
    results = model.predict(source=img, conf=conf_threshold, save=False)

    # Solo usamos la primera imagen y la primera detección
    if not results or not results[0].boxes:
        return None

    # Seleccionar la caja con mayor confianza
    best_box = max(results[0].boxes, key=lambda b: float(b.conf[0]))

    x1, y1, x2, y2 = map(int, best_box.xyxy[0])
    conf = float(best_box.conf[0])

    return {
        "bbox": (x1, y1, x2, y2),
        "conf": conf
    }
