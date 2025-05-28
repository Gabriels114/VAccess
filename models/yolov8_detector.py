import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO
import cv2

class YoloPlateDetector:
    def __init__(self, model_path: str, conf: float = 0.25):
        self.model = YOLO(model_path)
        self.confidence_threshold = conf

    def detect_plate(self, image):
        """
        Realiza detección de placas en una imagen.

        Returns:
            - cropped_plate: Recorte de la placa (si fue detectada)
            - coords: Coordenadas (x1, y1, x2, y2)
        """
        results = self.model.predict(source=image, conf=self.confidence_threshold, save=False)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped = image[y1:y2, x1:x2]
                return cropped, (x1, y1, x2, y2)

        return None, None
