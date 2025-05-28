# VAccess
VAccess es una plataforma inteligente, modular y de bajo costo diseñada para  automatizar el acceso vehicular es moduelar y utilizar visión por computadora que permite detectar automáticamente placas vehiculares y extraer sus caracteres mediante técnicas de OCR. Está diseñado para su integración en sistemas de control vehicular embebido o para análisis por lotes.



---

## 📁 Estructura del Proyecto

placas-detector/
├── pipeline_main.py # Script principal
├── data/ # Configuración del dataset (data.yaml)
├── datasets/ # Imágenes de entrenamiento, validación y prueba
├── outputs/ # Resultados y métricas generadas
├── scripts/ # Entrenamiento y evaluación del modelo
├── src/ # Módulos funcionales (detección, OCR, visualización)
├── assets/ # Ejemplos visuales y documentación
└── requirements.txt # Dependencias del proyecto

---
## ⚙️ Requisitos

Instala las dependencias con:

```bash
conda create -n placas python=3.10 -y
conda activate placas
pip install -r requirements.txt
```
---

