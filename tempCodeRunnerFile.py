from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from pymongo import MongoClient
import easyocr
from datetime import datetime

app = FastAPI()

# Conexión a MongoDB
mongo_uri = "mongodb+srv://ana123:1234@cluster0.abcd.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client['baseDatos']  # nombre que aparece en Atlas
vehiculos = db['vehiculo']
eventos = db['eventos']

reader = easyocr.Reader(['en'], gpu=False)  # OCR básico

# Función para decodificar imagen a partir de bytes
def read_image_from_bytes(image_bytes: bytes):
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img

# Procesar imagen (recorte y filtros simples)
def procesar_imagen(img):
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(blur, 30, 200)
    return edged

# OCR y verificación de placa
def detectar_placa_y_verificar(img_procesada):
    if img_procesada is None:
        return 0
    resultados = reader.readtext(img_procesada)
    for (bbox, texto, conf) in resultados:
        placa = texto.strip().replace(" ", "").upper()
        if 5 <= len(placa) <= 8:  # Validación básica
            vehiculo = vehiculos.find_one({"placa": placa})
            if vehiculo:
                eventos.insert_one({
                    "placa_detectada": placa,
                    "fecha": datetime.now()
                })
                return 1
    return 0

# Endpoint principal
@app.post("/procesar_entrada/")
async def procesar_entrada(imagen_frontal: UploadFile = File(...), imagen_trasera: UploadFile = File(...)):
    try:
        # Leer bytes de las imágenes
        img1_bytes = await imagen_frontal.read()
        img2_bytes = await imagen_trasera.read()

        # Decodificar imágenes
        img1 = read_image_from_bytes(img1_bytes)
        img2 = read_image_from_bytes(img2_bytes)

        # Procesar imágenes
        proc1 = procesar_imagen(img1)
        proc2 = procesar_imagen(img2)

        resultado1 = detectar_placa_y_verificar(proc1)
        resultado2 = detectar_placa_y_verificar(proc2)

        if resultado1 or resultado2:
            return JSONResponse(content={"acceso": 1})  # Acceso permitido
        else:
            return JSONResponse(content={"acceso": 0})  # Acceso denegado
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
