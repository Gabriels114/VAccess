# src/visualize.py

import cv2

def show_results(original, cropped, processed, text):
    """
    Muestra por pantalla la imagen original, el recorte, la versión preprocesada
    y el texto reconocido por OCR.
    """
    cv2.imshow("Original", original)
    cv2.imshow("Cropped", cropped)
    cv2.imshow("Processed", processed)
    print("Texto reconocido:", text)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
