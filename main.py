from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from pymongo import MongoClient
import easyocr
from datetime import datetime
import os

app = FastAPI()

# Archivos estáticos e interfaz
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Conexión a MongoDB
mongo_uri = "mongodb+srv://dato:1234@cluster.wc2cdhl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"
client = MongoClient(mongo_uri)
db = client['baseDatos']
vehiculos = db['vehiculo']
eventos = db['eventos']

reader = easyocr.Reader(['en'])

# Leer imagen desde archivo
def read_image(file):
    img_bytes = np.frombuffer(file.file.read(), np.uint8)
    return cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

# Preprocesamiento de imagen
def procesar_imagen(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(blur, 30, 200)
    return edged

# Limpieza de placas en la base de datos (opcional, ejecutar solo una vez si quieres limpiar)
def limpiar_placas_bd():
    for doc in vehiculos.find():
        placa_limpia = doc['placa'].strip().replace(" ", "").upper()
        if doc['placa'] != placa_limpia:
            vehiculos.update_one({"_id": doc['_id']}, {"$set": {"placa": placa_limpia}})
            print(f"Placa limpiada: {repr(doc['placa'])} -> {repr(placa_limpia)}")


def detectar_placa_y_verificar(img_procesada):
    try:
        resultados = reader.readtext(img_procesada)
        print("Resultados OCR:")

        print("Placas registradas en la base:")
        for v in vehiculos.find({}, {"_id": 0, "placa": 1}):
            print("-", repr(v.get('placa', 'SIN PLACA')))

        for (bbox, texto, conf) in resultados:
            print(f"Texto crudo detectado: {repr(texto)}, Confianza: {conf:.2f}")
            placa = texto.strip().replace(" ", "").upper()
            print(f"Placa candidata: {placa}")

            vehiculo = vehiculos.find_one({"placa": {"$regex": f"^{placa}$", "$options": "i"}})
            print(f"Resultado búsqueda en BD para placa '{placa}': {vehiculo}")

            if vehiculo:
                print(f"Placa {placa} encontrada en BD, registrando evento.")
                eventos.insert_one({
                    "placa_detectada": placa,
                    "fecha": datetime.now()
                })
                return 1

        print("No se detectó placa válida.")
        return 0

    except Exception as e:
        print(f"Error en detectar_placa_y_verificar: {e}")
        return 0

# Endpoint principal
@app.post("/procesar_entrada/")
async def procesar_entrada(imagen_frontal: UploadFile = File(...), imagen_trasera: UploadFile = File(...)):
    try:
        img1 = read_image(imagen_frontal)
        img2 = read_image(imagen_trasera)

        proc1 = procesar_imagen(img1)
        proc2 = procesar_imagen(img2)

        resultado1 = detectar_placa_y_verificar(proc1)
        resultado2 = detectar_placa_y_verificar(proc2)

        if resultado1 or resultado2:
            return JSONResponse(content={"acceso": 1})
        else:
            return JSONResponse(content={"acceso": 0})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)