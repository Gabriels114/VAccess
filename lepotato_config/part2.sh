#!/bin/bash
# final_setup.sh — Fase final con validaciones
# Autor: Gabriels

set -e
set -o pipefail

LOGFILE="/var/log/final_setup_lepotato.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "=== [Fase Final] Configuración Le Potato ==="

USERNAME="gabriels"
USER_HOME="/home/$USERNAME"
PROJECT_DIR="$USER_HOME/proyecto-control"
VENV_DIR="$PROJECT_DIR/venv"
DB_PATH="$PROJECT_DIR/data/log.db"

# 1. Verificar entorno virtual
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "❌ ERROR: El entorno virtual no existe en $VENV_DIR"
  exit 1
fi

echo "[1] Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

echo "[1.1] Verificando entorno virtual..."
which python
which pip

# 2. Verificar conexión a Internet antes de instalar paquetes
echo "[2] Verificando conexión a Internet..."
ping -c 2 1.1.1.1 > /dev/null || {
  echo "❌ ERROR: No hay conexión a internet. Abortando..."
  exit 1
}

# 3. Instalar paquetes Python
echo "[3] Instalando paquetes en venv..."
pip install --upgrade pip
pip install \
  opencv-python opencv-contrib-python \
  numpy aiofiles fastapi \
  python-escpos RPi.GPIO \
  smbus2 adafruit-circuitpython-charlcd \
  httpx

# 4. Verificar o crear archivo SQLite
echo "[4] Verificando archivo SQLite..."
mkdir -p "$PROJECT_DIR/data"
if [ ! -f "$DB_PATH" ]; then
  echo "Creando log.db y tabla registros..."
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
else
  echo "log.db ya existe."
fi

# 5. Cronjob de limpieza (evita duplicados)
echo "[5] Configurando cronjob..."
CRON_CMD="sqlite3 $DB_PATH \"DELETE FROM registros WHERE datetime < datetime('now', '-14 days');\""
CRON_JOB="0 3 * * * $CRON_CMD"

# Verificar si ya existe
crontab -u "$USERNAME" -l 2>/dev/null | grep -F "$CRON_CMD" >/dev/null || (
  (crontab -u "$USERNAME" -l 2>/dev/null; echo "$CRON_JOB") | crontab -u "$USERNAME" -
  echo "Cronjob agregado."
)

# 6. Servicios y firewall
echo "[6] Activando servicios..."
systemctl enable ssh
systemctl enable cups
systemctl start  cups

ufw allow OpenSSH
ufw allow 8000/tcp
ufw --force enable

# 7. Limpieza final
echo "[7] Limpiando sistema..."
apt autoremove -y
apt clean

echo "✅ [Fase Final] Configuración completada con éxito."
echo "♻️ Reiniciando en 5 segundos..."
sleep 5
reboot
