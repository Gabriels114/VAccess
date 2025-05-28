from ultralytics import YOLO
import cv2

# 1) Ruta a la imagen que quieres analizar
imagen_path = "coche.jpeg"
img = cv2.imread(imagen_path)
if img is None:
    raise FileNotFoundError(f"No se encontró la imagen: {imagen_path}")

# 2) Carga tu modelo
#    - Si quieres probar con el nano pre-entrenado en COCO:
#model = YOLO("yolov8n.pt")

#    - O carga tu modelo custom entrenado para placas:
model = YOLO("runs/detect/placas_s3/weights/best.pt")

# 3) Ejecuta la predicción
#    conf=0.25 → umbral mínimo de confianza al 25%
results = model.predict(source=img, conf=0.25, save=False)

# 4) Recorre las detecciones y dibuja las cajas
for result in results:               # Ultraly­tics devuelve una lista de resultados (uno por entrada)
    for box in result.boxes:         # result.boxes es la lista de cajas detectadas
        # Coordenadas xyxy
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        clase = int(box.cls[0])      # índice de la clase
        nombre_clase = model.names[clase]

        # Imprime por consola
        print(f"Detectado: {nombre_clase} en ({x1},{y1})–({x2},{y2}), conf={box.conf[0]:.2f}")

        # Dibuja rectángulo y etiqueta
        cv2.rectangle(img, (x1+5, y1+2), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            img, nombre_clase, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

# 5) Muestra la imagen resultante en ventana OpenCV
cv2.imshow("Detecciones YOLOv8", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
