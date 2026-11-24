# -*- coding: utf-8 -*-
"""Usa la clave Mistral real del .env raiz y configura el proveedor MISTRAL.
No imprime la clave."""
from pathlib import Path
import pymysql

root = Path(__file__).resolve().parents[2]          # unidad_3
proyecto = Path(__file__).resolve().parents[1]      # proyecto-codigo


def leer_clave(ruta):
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        s = linea.strip()
        if s.startswith("MISTRAL_API_KEY="):
            return s.split("=", 1)[1].strip().strip('"')
    return None


clave = leer_clave(root / ".env")
if not clave:
    raise SystemExit("No se encontro MISTRAL_API_KEY en el .env raiz")
if not clave.startswith("mstrl"):
    raise SystemExit("La clave del .env raiz no parece de Mistral (prefijo distinto)")

(proyecto / ".env").write_text(
    "# Credencial real de Mistral AI (tomada del .env del workspace)\n"
    f"MISTRAL_API_KEY={clave}\n"
    "# MySQL/XAMPP\n"
    "DB_USER=root\n"
    "DB_PASSWORD=\n",
    encoding="utf-8",
)
print("Clave Mistral copiada a proyecto-codigo/.env | longitud:", len(clave))

conn = pymysql.connect(host="localhost", port=3306, user="root", password="",
                       database="memoridocx", charset="utf8mb4")
cur = conn.cursor()
cur.execute("""
    UPDATE ai_providers
       SET display_name = 'Mistral AI',
           model_id = 'mistral-large-latest',
           base_url = 'https://api.mistral.ai/v1'
     WHERE code = 'MISTRAL'
""")
conn.commit()
cur.execute("SELECT display_name, model_id, base_url FROM ai_providers WHERE code='MISTRAL'")
print("Proveedor actualizado:", cur.fetchone())
conn.close()
