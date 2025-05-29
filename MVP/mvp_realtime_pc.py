
# mvp_realtime_pc.py

import os
import time
import cv2
import numpy as np
import requests
from ultralytics import YOLO
from src.gemini_api import get_license_plate_text

# ——— CONFIGURACIÓN ———
MODEL_PATH    = "models/yolov8_placas.pt"
CROPS_DIR     = "crops"
FRAME_SKIP    = 5   # procesa 1 de cada 5 frames
LEPOTATO_HOST = "http://192.168.166.202:8002"
if not LEPOTATO_HOST:
    raise RuntimeError("Define la variable de entorno LEPOTATO_HOST antes de ejecutar")
os.makedirs(CROPS_DIR, exist_ok=True)
# =======================

def accionar_servo_real():
    """Abre y cierra la barrera vía HTTP en Le Potato."""
    try:
        r = requests.post(f"{LEPOTATO_HOST}/servo/abrir", timeout=5)
        print("[LEPOTATO] Abrir →", r.status_code, r.json())
    except Exception as e:
        print("[ERROR] Al abrir barrera:", e)
    time.sleep(2)
    try:
        r = requests.post(f"{LEPOTATO_HOST}/servo/cerrar", timeout=5)
        print("[LEPOTATO] Cerrar →", r.status_code, r.json())
    except Exception as e:
        print("[ERROR] Al cerrar barrera:", e)

def imprimir_ticket(plate: str):
    """Envía la placa al endpoint de impresión del Le Potato."""
    try:
        r = requests.post(
            f"{LEPOTATO_HOST}/ticket/print",
            json={"plate": plate},
            timeout=5
        )
        print("[TICKET] →", r.status_code, r.json())
    except Exception as e:
        print("[ERROR] Al imprimir ticket:", e)

def main():
    model   = YOLO(MODEL_PATH)
    cap     = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la cámara.")
        return

    cv2.namedWindow("VAccess - MVP",    cv2.WINDOW_NORMAL)
    cv2.namedWindow("Recorte de Placa", cv2.WINDOW_NORMAL)

    last_crop = np.zeros((200,400,3), dtype=np.uint8)
    last_text = ""
    frame_id  = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_id % FRAME_SKIP == 0:
                results = model.predict(source=frame, conf=0.5, imgsz=640)
                detected = False

                for r in results:
                    for box in r.boxes.xyxy:
                        x1, y1, x2, y2 = map(int, box)
                        cropped = frame[y1:y2, x1:x2]

                        ts   = int(time.time()*1000)
                        path = os.path.join(CROPS_DIR, f"{ts}.jpg")
                        cv2.imwrite(path, cropped)

                        cv2.imshow("Recorte de Placa", cropped)
                        last_crop = cropped.copy()

                        texto = get_license_plate_text(path)
                        if texto:
                            last_text = texto.strip()
                            accionar_servo_real()
                            imprimir_ticket(last_text)
                        else:
                            print("[GEMINI] Placa no legible, no acciono servo/ticket.")
                        detected = True
                        break
                    if detected:
                        break

                if not detected:
                    cv2.imshow("Recorte de Placa", last_crop)
            else:
                # frames intermedios: solo mostrar último recorte
                cv2.imshow("Recorte de Placa", last_crop)

            # dibujar bounding boxes solo en frames procesados
            if frame_id % FRAME_SKIP == 0:
                for r in results:
                    for box in r.boxes.xyxy:
                        x1, y1, x2, y2 = map(int, box)
                        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

            # sobreimprimir último texto
            if last_text:
                cv2.rectangle(frame, (10,10), (300,50), (0,0,0), cv2.FILLED)
                cv2.putText(
                    frame,
                    f"Placa: {last_text}",
                    (15,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0,255,0),
                    2,
                    cv2.LINE_AA
                )

            cv2.imshow("VAccess - MVP", frame)

            frame_id += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Demo finalizada.")

if __name__ == "__main__":
    main()
