from ultralytics import YOLO
import os
import cv2

# Ruta al modelo entrenado (ajústala según tu estructura)
MODEL_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'models', 'yolov8_placas.pt')
)

# Carga del modelo una sola vez\ nmodel = YOLO(MODEL_PATH)
model = YOLO(MODEL_PATH)

def detect_license_plate(image_path: str, conf_threshold: float = 0.25):
    """
    Detecta la(s) placa(s) en una imagen y devuelve la imagen original
    junto con el recorte de la primera placa que encuentre.

    Args:
        image_path (str): Ruta a la imagen a procesar.
        conf_threshold (float): Umbral de confianza para detección.

    Returns:
        tuple: (img, cropped) donde img es la imagen original en formato BGR
               y cropped es el recorte de la placa o None si no se detecta nada.
    """
    # Lee la imagen
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {image_path}")

    # Ejecuta la detección
    results = model.predict(source=img, conf=conf_threshold, save=False)

    # Recorre los resultados y devuelve la primera placa detectada
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cropped = img[y1:y2, x1:x2]
            return img, cropped

    # Si no detecta ninguna placa, retorna la imagen original y None
    return img, None
