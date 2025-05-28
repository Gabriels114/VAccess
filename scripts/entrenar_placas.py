import os
# evita el conflicto de OpenMP
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def main():
    from ultralytics import YOLO

    # -------- Configuración --------
    DATA_YAML  = "sets/data.yaml"
    BASE_MODEL = "yolov8s.pt"
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
        # puedes añadir: workers=0  si lo prefieres
    )

if __name__ == "__main__":
    # necesario en Windows para spawn multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()
    main()
