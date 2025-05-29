#!/usr/bin/env python3
"""
register_and_actuate.py

Script para:
1. Guardar placas vistas en una base de datos SQLite simple.
2. Verificar si la placa ya fue vista antes.
   - Si ya existe: enviar orden de apertura a Le Potato.
   - Si no existe: imprimir ticket de registro y guardar la placa.
"""

import os
import sys
import sqlite3
import requests

# --- CONFIGURACIÓN ---
DB_PATH = os.getenv("VACCESS_DB_PATH", "vaccess.db")
# Ajusta la URL a tu endpoint de Le Potato para abrir la barrera
LEPOTATO_ENDPOINT = os.getenv("LEPOTATO_OPEN_URL", "http://<LEPOTATO_IP>:8001/abrir")

# --- FUNCIONES DE BASE DE DATOS ---

def init_db():
    """Inicializa la base de datos SQLite y crea la tabla si no existe."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            plate TEXT PRIMARY KEY,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def is_registered(conn, plate: str) -> bool:
    """Verifica si la placa ya existe en la base de datos."""
    cur = conn.cursor()
    cur.execute("SELECT plate FROM vehicles WHERE plate = ?", (plate,))
    return cur.fetchone() is not None

def register_plate(conn, plate: str):
    """Guarda una nueva placa en la base de datos."""
    cur = conn.cursor()
    cur.execute("INSERT INTO vehicles (plate) VALUES (?)", (plate,))
    conn.commit()

# --- FUNCIONES DE ACTUACIÓN ---

def send_open_command(plate: str):
    """
    Envía la orden de apertura al endpoint de Le Potato.
    Ajusta método HTTP, headers o payload según tu API.
    """
    try:
        payload = {"plate": plate}
        resp = requests.post(LEPOTATO_ENDPOINT, json=payload, timeout=5)
        if resp.ok:
            print(f"[OPEN] Orden de apertura enviada para placa {plate}.")
        else:
            print(f"[OPEN] Error al enviar orden: HTTP {resp.status_code}")
    except Exception as e:
        print(f"[OPEN] No se pudo contactar a Le Potato: {e}")

def print_registration_ticket(plate: str):
    """
    Simula la impresión de un ticket físico invitando al registro.
    Puedes integrar aquí la librería de impresora térmica.
    """
    print(f"[TICKET] ===============================")
    print(f"[TICKET] Tu placa ({plate}) no está registrada.")
    print(f"[TICKET] Escanea este código QR para registrarte:")
    print(f"[TICKET] https://miapp.com/registrar?placa={plate}")
    print(f"[TICKET] ===============================")

# --- LÓGICA PRINCIPAL ---

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python register_and_actuate.py <PLACA>")
        sys.exit(1)

    # Obtener y normalizar la placa
    plate = sys.argv[1].strip().upper()

    # Inicializar DB y verificar
    conn = init_db()

    if is_registered(conn, plate):
        print(f"[INFO] Placa {plate} ya registrada.")
        send_open_command(plate)
    else:
        print(f"[INFO] Placa {plate} no registrada.")
        print_registration_ticket(plate)
        register_plate(conn, plate)
        print(f"[DB] Placa {plate} guardada para próximas veces.")

    conn.close()

if __name__ == "__main__":
    main()
