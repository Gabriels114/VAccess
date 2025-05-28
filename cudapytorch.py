import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch, platform, os
print("PyTorch:", torch.__version__)
print("CUDA visible:", torch.cuda.is_available(), "| GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")

