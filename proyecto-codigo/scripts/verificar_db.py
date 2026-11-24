# -*- coding: utf-8 -*-
"""Verificacion rapida de la base memoridocx (evidencia)."""
import pymysql

conn = pymysql.connect(host="localhost", port=3306, user="root", password="",
                       database="memoridocx", charset="utf8mb4")
cur = conn.cursor()
for tabla in ("documents", "document_chunks", "conversations", "messages",
              "processing_logs", "ai_providers", "users"):
    cur.execute(f"SELECT COUNT(*) FROM {tabla}")
    print(f"{tabla}: {cur.fetchone()[0]}")
cur.execute("SELECT id, original_name, status, page_count, chunk_count FROM documents ORDER BY id")
print("\nDocumentos:")
for row in cur.fetchall():
    print(" ", row)
conn.close()
