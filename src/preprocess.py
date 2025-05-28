# src/preprocess.py

import cv2


def preprocess_plate_image(plate_img):
    """
    Preprocesa una imagen de una placa vehicular para mejorar la precisión del OCR.

    Pasos:
    1. Conversión a escala de grises
    2. Reducción de ruido mediante desenfoque Gaussiano
    3. Umbral adaptativo (ideal para condiciones de iluminación variables)

    Args:
        plate_img (np.ndarray): Imagen BGR recortada de la placa.

    Returns:
        np.ndarray: Imagen binarizada (escala de grises) lista para OCR.
    """
    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

    # 2. Desenfoque Gaussiano para reducir ruido
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Umbral adaptativo (inverso) para resaltar caracteres claros sobre fondo oscuro
    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        19,
        9
    )

    return thresh


if __name__ == "__main__":
    # Prueba rápida de preprocesamiento
    import matplotlib.pyplot as plt
    import os

    test_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'coche.jpeg')
    img = cv2.imread(test_path)
    preprocessed = preprocess_plate_image(img)

    plt.imshow(preprocessed, cmap='gray')
    plt.title("Preprocesamiento de Placa")
    plt.axis("off")
    plt.show()
