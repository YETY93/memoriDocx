-- ============================================================
-- memoriDocx - Consultas para capturar evidencias en phpMyAdmin
-- Ejecutar despues de iniciar el backend (schema.sql y seed.sql
-- se ejecutan automaticamente al arrancar la aplicacion).
-- ============================================================
USE memoridocx;

-- Resumen general
SELECT 'documentos' AS entidad, COUNT(*) AS registros FROM documents
UNION ALL SELECT 'fragmentos', COUNT(*) FROM document_chunks
UNION ALL SELECT 'conversaciones', COUNT(*) FROM conversations
UNION ALL SELECT 'mensajes', COUNT(*) FROM messages
UNION ALL SELECT 'logs de procesamiento', COUNT(*) FROM processing_logs
UNION ALL SELECT 'proveedores de IA', COUNT(*) FROM ai_providers;

-- Estado de los documentos
SELECT id, original_name, status, page_count, chunk_count, processed_at
FROM documents ORDER BY id;

-- Trazabilidad del procesamiento (habitual y con error controlado)
SELECT id, document_id, step, status, attempt, message, created_at
FROM processing_logs ORDER BY id;

-- Fragmentos indexados con su pagina de origen
SELECT id, document_id, page_number, chunk_index, LEFT(content, 100) AS fragmento
FROM document_chunks ORDER BY id;

-- Historial de consultas y respuestas con sus fuentes
SELECT id, role, model, LEFT(content, 140) AS contenido, sources, created_at
FROM messages ORDER BY id;

-- Proveedores de IA configurados
SELECT code, display_name, model_id, base_url, enabled, active
FROM ai_providers ORDER BY id;
