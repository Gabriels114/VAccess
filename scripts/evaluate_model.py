import os
# evita el error de OpenMP en Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

def main():
    # Ajusta rutas si es necesario
    MODEL_PATH = "runs/detect/placas_s3/weights/best.pt"
    DATA_YAML  = "sets/data.yaml"
    SPLIT      = "test"   # 'train', 'val' o 'test'

    # 1) Carga el modelo entrenado
    model = YOLO(MODEL_PATH)

    # 2) Evalúa en test (plots=True para que genere y guarde la conf matrix)
    res = model.val(data=DATA_YAML, split=SPLIT, plots=True)

    # 3) Extrae las métricas y conviértelas a float
    precision = float(res.box.p.item())
    recall    = float(res.box.r.item())
    map50     = float(res.box.map50.item())
    map50_95  = float(res.box.map.item())

    print(f"Precision:  {precision:.4f}")
    print(f"Recall:     {recall:.4f}")
    print(f"mAP50:      {map50:.4f}")
    print(f"mAP50-95:   {map50_95:.4f}")

    # 4) Bar‐chart de métricas
    names  = ["Precision", "Recall", "mAP50", "mAP50-95"]
    values = [precision, recall, map50, map50_95]
    plt.figure(figsize=(8, 4))
    plt.bar(names, values)
    plt.ylim(0, 1)
    plt.title(f"Métricas en split='{SPLIT}'")
    plt.ylabel("Score")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("test_metrics.png")
    plt.show()

    # 5) Carga y muestra la matriz de confusión guardada
    # res.save_dir es el Path donde Ultraly­tics guardó los plots
    cm_path = Path(res.save_dir) / "confusion_matrix.png"
    if cm_path.exists():
        img = mpimg.imread(cm_path)
        plt.figure(figsize=(6, 6))
        plt.imshow(img)
        plt.axis('off')
        plt.title("Matriz de Confusión")
        plt.show()
    else:
        print(f"No se encontró la matriz de confusión en {cm_path}")




if __name__ == "__main__":
    # necesario en Windows para spawn multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()
    main()
