import os
import cv2
from ultralytics import YOLO

def main():
    # 1) Ruta a la imagen
    img_path = os.path.join("assets", "coche.jpeg")
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"No se encontró la imagen: {img_path}")

    # 2) Carga tu modelo custom (entrenado) desde la carpeta models/
    model = YOLO(os.path.join("models", "yolov8_placas.pt"))

    # 3) Ejecuta la predicción (umbral 25%)
    results = model.predict(source=img, conf=0.25, save=False)

    # 4) Dibuja cajas y muestra información
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            name = model.names[cls_id]
            conf  = float(box.conf[0])

            print(f"Detectado: {name} en ({x1},{y1})–({x2},{y2}), conf={conf:.2f}")
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                img,
                f"{name} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    # 5) Muestra la imagen con detecciones
    cv2.imshow("Detecciones YOLOv8", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
