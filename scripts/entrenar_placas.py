import os

# Evita el conflicto de OpenMP en Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO

def main():
    # -------- Configuración --------
    DATA_YAML  = os.path.join("datasets", "data.yaml")
    BASE_MODEL = os.path.join("models", "yolov8s.pt")   # peso base YOLOv8s
    RUN_NAME   = "placas_s"

    model = YOLO(BASE_MODEL)
    model.train(
        data=DATA_YAML,
        epochs=60,
        imgsz=640,
        batch=16,
        device=0,
        name=RUN_NAME,
        lr0=0.003,
        patience=10,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
        degrees=5, translate=0.05, scale=0.1, shear=2,
        fliplr=0.5
    )

if __name__ == "__main__":
    # Necesario en Windows para multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()
    main()
