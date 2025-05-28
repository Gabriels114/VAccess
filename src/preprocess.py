# preprocess.py

import cv2
import numpy as np


def preprocess_plate(plate_img):
    """
    Preprocesa una imagen de una placa vehicular para mejorar el OCR.

    Pasos:
    1. Escala a grises
    2. Reducción de ruido (blur)
    3. Umbral adaptativo
    4. (Opcional) Alineación futura

    :param plate_img: Imagen de la placa (recortada)
    :return: Imagen binarizada preprocesada
    """
    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

    # 2. Desenfoque Gaussiano para reducir ruido
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Umbral adaptativo (mejor para condiciones de luz variables)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        19, 9
    )

    return thresh


# Para pruebas unitarias rápidas
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    test_path = "recorte.jpg"
    img = cv2.imread(test_path)
    preprocessed = preprocess_plate(img)

    plt.imshow(preprocessed, cmap='gray')
    plt.title("Preprocesamiento de Placa")
    plt.axis("off")
    plt.show()
