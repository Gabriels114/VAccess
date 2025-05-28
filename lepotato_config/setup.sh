#!/bin/bash
# Script de configuración para Le Potato – Sistema de Control Vehicular Inteligente
# Autor: Gabriels
# Última actualización: 2025‑04‑17

set -e              # Detiene el script si un comando devuelve error
set -o pipefail      # Hace que los errores en tuberías también aborten el script

LOGFILE="/var/log/setup_lepotato.log"
exec > >(tee -a "$LOGFILE") 2>&1    # Todo lo que se imprime se envía al log

echo "=== Iniciando configuración del sistema Le Potato ==="

# ------------------------------------------------------------------
# 1. Expansión de la partición raíz
# ------------------------------------------------------------------
ROOT_PART="/dev/mmcblk0p1"
ROOT_DISK="/dev/mmcblk0"

if ! grep -q "100%" <(parted $ROOT_DISK print | grep $ROOT_PART); then
  echo "[1] Expandiendo partición raíz a todo el tamaño de la micro‑SD…"
  parted $ROOT_DISK resizepart 1 100%
  resize2fs $ROOT_PART
else
  echo "[1] La partición raíz ya ocupa el 100 % del disco."
fi

# ------------------------------------------------------------------
# 2. Creación y activación de archivo SWAP (4 GB)
# ------------------------------------------------------------------
SWAP_FILE="/swapfile"
if [ ! -f "$SWAP_FILE" ]; then
  echo "[2] Creando archivo SWAP de 4 GB…"
  fallocate -l 4G $SWAP_FILE || dd if=/dev/zero of=$SWAP_FILE bs=1M count=4096
  chmod 600 $SWAP_FILE
  mkswap  $SWAP_FILE
  swapon  $SWAP_FILE
  echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab
  echo "vm.swappiness=10"        >> /etc/sysctl.conf   # Evita uso excesivo de SWAP
  echo "vm.vfs_cache_pressure=50" >> /etc/sysctl.conf   # Mejora caché de inodos
else
  echo "[2] Archivo SWAP ya existente, se omite."
fi

# ------------------------------------------------------------------
# 3. Actualización del sistema operativo
# ------------------------------------------------------------------
echo "[3] Actualizando paquetes del sistema…"
apt update && apt upgrade -y

# ------------------------------------------------------------------
# 4. Instalación de herramientas y utilidades esenciales
# ------------------------------------------------------------------
echo "[4] Instalando utilidades básicas…"
apt install -y \
  python3 python3-pip python3-venv git curl unzip \
  ufw net-tools wireless-tools wpasupplicant network-manager \
  sqlite3 cron tmux htop lsof \
  i2c-tools libi2c-dev          # Soporte a bus I²C (LCD)

# ------------------------------------------------------------------
# 5. Librerías para captura de vídeo e imagen (OpenCV y V4L2)
# ------------------------------------------------------------------
echo "[5] Instalando dependencias de cámara / vídeo…"
apt install -y \
  libjpeg-dev zlib1g-dev libpng-dev libtiff-dev \
  libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
  libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev \
  v4l-utils ffmpeg

# ------------------------------------------------------------------
# 6. Soporte para impresora térmica (EC‑5890X)
# ------------------------------------------------------------------
echo "[6] Instalando CUPS y driver ESC/P‑R…"
apt install -y cups printer-driver-escpr

# ------------------------------------------------------------------
# 7. Paquetes Python del proyecto
#    (solo lo necesario para el SBC: captura, preproceso, HW, API)
# ------------------------------------------------------------------
echo "[7] Instalando paquetes Python…"
pip3 install --upgrade pip
pip3 install \
  opencv-python opencv-contrib-python aiofiles numpy \
  python-escpos           \ # control impresora
  RPi.GPIO                \ # GPIO para sensor IR / servo
  smbus2 adafruit-circuitpython-charlcd  # LCD I²C
  httpx                   \ # cliente HTTP asíncrono (envío de imágenes)
  fastapi                 # opcional si publicas una ruta local para pruebas

# ------------------------------------------------------------------
# 8. Habilitación de servicios y firewall
# ------------------------------------------------------------------
echo "[8] Activando servicios SSH y CUPS, configurando UFW…"
systemctl enable ssh
systemctl enable cups
systemctl start  cups

ufw allow OpenSSH
ufw allow 8000/tcp      # puerto que usará FastAPI cliente/servidor
ufw --force enable

# ------------------------------------------------------------------
# 9. Creación de estructura de proyecto y base de datos SQLite
# ------------------------------------------------------------------
USERNAME="gabriels"                   # Cambia si tu usuario es otro
USER_HOME="/home/$USERNAME"
PROJECT_DIR="$USER_HOME/proyecto-control"

echo "[9] Creando estructura en $PROJECT_DIR…"
mkdir -p "$PROJECT_DIR/app" "$PROJECT_DIR/data" "$PROJECT_DIR/scripts"
touch     "$PROJECT_DIR/data/log.db"            # DB SQLite vacía
chown -R "$USERNAME:$USERNAME" "$PROJECT_DIR"

# ------------------------------------------------------------------
# 10. Limpieza final de paquetes
# ------------------------------------------------------------------
echo "[11] Eliminando paquetes no necesarios…"
apt autoremove -y
apt clean

echo "=== Configuración completada con éxito ==="
echo "Reiniciando en 5 s…"
sleep 5
reboot
