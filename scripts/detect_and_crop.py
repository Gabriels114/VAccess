import os
import cv2
from ultralytics import YOLO

def detect_plate(image_path, model_path=None, conf_threshold=0.25):
    """
    Detecta la primera matrícula en la imagen y guarda el recorte.

    :param image_path: Ruta a la imagen de entrada (e.g. assets/coche.jpeg)
    :param model_path: Ruta al peso .pt entrenado (por defecto models/yolov8_placas.pt)
    :param conf_threshold: Umbral mínimo de confianza
    :return: Recorte de la matrícula (np.ndarray) o None si no se detecta
    """
    if model_path is None:
        model_path = os.path.join("models", "yolov8_placas.pt")

    model = YOLO(model_path)
    img   = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"No se encontró la imagen: {image_path}")

    results = model.predict(source=img, conf=conf_threshold, save=False)

    # Crea carpeta de salida si no existe
    out_dir = os.path.join("outputs", "predictions")
    os.makedirs(out_dir, exist_ok=True)

    for result in results:
        for i, box in enumerate(result.boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cropped = img[y1:y2, x1:x2]

            # Guarda el recorte
            filename = f"placa_crop_{i}.png"
            out_path = os.path.join(out_dir, filename)
            cv2.imwrite(out_path, cropped)
            print(f"[+] Placa recortada guardada en: {out_path}")

            return cropped

    print("[-] No se detectó ninguna placa.")
    return None

if __name__ == "__main__":
    # Para pruebas rápidas desde línea de comandos
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Ruta a la imagen de entrada (assets/coche.jpeg)")
    parser.add_argument("--model", help="Ruta al peso .pt", default=None)
    parser.add_argument("--conf",  help="Umbral de confianza", type=float, default=0.25)
    args = parser.parse_args()

    detect_plate(args.image, args.model, args.conf)
