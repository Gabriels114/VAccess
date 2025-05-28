#!/bin/bash
# setup_full.sh — Script completo, idempotente y con verificaciones
# Le Potato AML‑S905X‑CC · Proyecto Control Vehicular Inteligente
# Autor: Gabriels · Actualizado: 2025‑04‑17 (migrado a libgpiod)

###############################################################################
# 0 · Salvaguardas generales                                                  #
###############################################################################

# Abortamos si no somos root
if [[ $EUID -ne 0 ]]; then
  echo "❌  Debes ejecutar este script con sudo o como root."; exit 1;
fi

set -euo pipefail

LOGFILE="/var/log/setup_lepotato_full.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "=== Instalación completa (verificable) — Le Potato ==="

aut_ping(){ ping -c1 -W2 1.1.1.1 > /dev/null 2>&1; }  # helper

USERNAME="gabriels"
USER_HOME="/home/$USERNAME"
PROJECT_DIR="$USER_HOME/proyecto-control"
VENV_DIR="$PROJECT_DIR/venv"
DB_PATH="$PROJECT_DIR/data/log.db"

###############################################################################
# 1 ·  Expansión de partición raíz                                            #
###############################################################################
ROOT_PART="/dev/mmcblk0p1"; ROOT_DISK="/dev/mmcblk0"
if ! grep -q "100%" <(parted -s $ROOT_DISK print | grep $ROOT_PART); then
  echo "[1] Expandiendo partición raíz…";
  parted -s $ROOT_DISK resizepart 1 100% && resize2fs $ROOT_PART;
else  echo "[1] Partición raíz ya al 100 %."; fi

###############################################################################
# 2 ·  SWAP (4 GB)                                                            #
###############################################################################
SWAP_FILE="/swapfile"
if ! swapon --summary | grep -q "$SWAP_FILE"; then
  echo "[2] Creando/activando SWAP…";
  [[ -f $SWAP_FILE ]] || fallocate -l 4G $SWAP_FILE || dd if=/dev/zero of=$SWAP_FILE bs=1M count=4096;
  chmod 600 $SWAP_FILE; mkswap $SWAP_FILE; swapon $SWAP_FILE;
  grep -q "$SWAP_FILE" /etc/fstab || echo -e "$SWAP_FILE none swap sw 0 0" >> /etc/fstab;
  grep -q "vm.swappiness" /etc/sysctl.conf || echo "vm.swappiness=10" >> /etc/sysctl.conf;
  grep -q "vm.vfs_cache_pressure" /etc/sysctl.conf || echo "vm.vfs_cache_pressure=50" >> /etc/sysctl.conf;
else  echo "[2] SWAP ya configurado."; fi

###############################################################################
# 3 ·  Actualizar sistema (solo si hay red)                                   #
###############################################################################
if aut_ping; then
  echo "[3] Actualizando paquetes…"; apt update && apt upgrade -y;
else
  echo "[3] Sin conexión: se omite apt update/upgrade.";
fi

###############################################################################
# 4 ·  Paquetes del sistema (instalación condicional)                         #
###############################################################################
SYSTEM_PACKAGES=(
  build-essential python3-dev          # tool‑chain para wheels nativos
  python3-full python3-venv git curl unzip ufw net-tools wireless-tools
  wpasupplicant network-manager sqlite3 cron tmux htop lsof
  i2c-tools libi2c-dev python3-libgpiod  # LCD I²C + GPIO moderno
  cups printer-driver-escpr
  libjpeg-dev zlib1g-dev libpng-dev libtiff-dev
  libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
  libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev
  v4l-utils ffmpeg )

for pkg in "${SYSTEM_PACKAGES[@]}"; do
  dpkg -s "$pkg" &>/dev/null && echo "[4] $pkg ✓" || {
    echo "[4] Instalando $pkg…"; apt install -y "$pkg"; }
done

###############################################################################
# 5 ·  Carpeta proyecto + venv                                                #
###############################################################################
mkdir -p "$PROJECT_DIR/app" "$PROJECT_DIR/data" "$PROJECT_DIR/scripts"
chown -R "$USERNAME:$USERNAME" "$PROJECT_DIR"
[[ -f $DB_PATH ]] || touch "$DB_PATH"

if [[ ! -f $VENV_DIR/bin/activate ]]; then
  echo "[5] Creando entorno virtual…"; python3 -m venv "$VENV_DIR";
fi

###############################################################################
# 6 ·  Paquetes Python (condicional)                                          #
###############################################################################
source "$VENV_DIR/bin/activate"
pip install --upgrade pip

PY_PKGS=(opencv-python opencv-contrib-python numpy aiofiles fastapi
         python-escpos smbus2 adafruit-circuitpython-charlcd httpx)

for pkg in "${PY_PKGS[@]}"; do
  pip show "$pkg" &>/dev/null && echo "[6] $pkg ✓" || {
    echo "[6] Instalando $pkg…"; pip install "$pkg"; }
done

deactivate

###############################################################################
# 7 ·  Base de datos SQLite                                                   #
###############################################################################
if [[ ! -s $DB_PATH ]]; then
  echo "[7] Creando esquema en log.db…";
  sqlite3 "$DB_PATH" <<'SQL'
CREATE TABLE IF NOT EXISTS registros (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  datetime TEXT NOT NULL,
  placa TEXT,
  frontal_path TEXT,
  trasera_path TEXT,
  registrado INTEGER,
  ticket_digital_enviado INTEGER,
  ticket_impreso INTEGER
);
SQL
else  echo "[7] log.db ya existe."; fi

###############################################################################
# 8 ·  Cron job limpieza                                                      #
###############################################################################
CRON_CMD="sqlite3 $DB_PATH \"DELETE FROM registros WHERE datetime < datetime('now', '-14 days');\""
CRON_JOB="0 3 * * * $CRON_CMD"
crontab -u "$USERNAME" -l 2>/dev/null | grep -F "$CRON_CMD" >/dev/null || {
  (crontab -u "$USERNAME" -l 2>/dev/null; echo "$CRON_JOB") | crontab -u "$USERNAME" -;
  echo "[8] Cronjob añadido."; }

###############################################################################
# 9 ·  Servicios y firewall                                                   #
###############################################################################
for svc in ssh cups; do
  systemctl enable "$svc"; systemctl start "$svc"; echo "[9] Servicio $svc activo.";
done

ufw allow OpenSSH; ufw allow 8000/tcp; ufw --force enable

###############################################################################
# 10 ·  Limpieza final y reinicio                                             #
###############################################################################
apt autoremove -y && apt clean

echo "✅ Instalación finalizada. Reinicio en 5 s…"; sleep 5; reboot
