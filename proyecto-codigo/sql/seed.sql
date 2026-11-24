-- ============================================================
-- memoriDocx - Datos semilla para demostracion y evidencias
-- INSERT IGNORE permite reiniciar el backend sin duplicar registros.
-- ============================================================
USE memoridocx;

INSERT IGNORE INTO users (id, username, full_name, role, active) VALUES
 (1, 'yesid', 'Yesid Rangel Orozco', 'INGENIERO_DE_SOFTWARE', TRUE),
 (2, 'leydi', 'Leydi Johana Polo Amador', 'DOCENTE', TRUE);

INSERT IGNORE INTO ai_providers (id, code, display_name, model_id, base_url, enabled, active) VALUES
 (1, 'MISTRAL', 'Mistral AI', 'mistral-large-latest', 'https://api.mistral.ai/v1', TRUE, TRUE),
 (2, 'DEEPSEEK', 'DeepSeek', 'deepseek-chat', 'https://api.deepseek.com/v1', TRUE, FALSE),
 (3, 'GLM', 'Zhipu GLM', 'glm-4', 'https://open.bigmodel.cn/api/paas/v4', TRUE, FALSE);

-- Documento de demostracion: procesado correctamente
INSERT IGNORE INTO documents
 (id, original_name, stored_name, content_type, size_bytes, status, page_count, chunk_count, error_message, uploaded_at, processed_at)
VALUES
 (1, 'Informe_Analisis_Procesos_memoriDocx.pdf', 'demo_informe_procesos.pdf', 'application/pdf', 248312,
  'AVAILABLE', 4, 5, NULL, '2026-11-10 08:15:00', '2026-11-10 08:15:04');

-- Documento con error controlado (simula OCR sin texto tras 3 reintentos)
INSERT IGNORE INTO documents
 (id, original_name, stored_name, content_type, size_bytes, status, page_count, chunk_count, error_message, uploaded_at, processed_at)
VALUES
 (2, 'PDF_danado_prueba.pdf', 'demo_pdf_danado.pdf', 'application/pdf', 18422,
  'FAILED', 1, 0, 'OCR sin texto suficiente tras 3 intentos', '2026-11-10 08:22:00', '2026-11-10 08:22:09');

INSERT IGNORE INTO document_chunks (id, document_id, page_number, chunk_index, content) VALUES
 (1, 1, 1, 0, 'Informe de analisis de procesos. Este documento presenta los hallazgos del diagnostico de gestion documental, los tiempos de respuesta y las responsabilidades del equipo de analisis de informacion.'),
 (2, 1, 2, 1, 'Tiempo de respuesta. El tiempo medio de atencion de una solicitud de informacion de nivel 2 es de doce horas. Para solicitudes de nivel 3 se reduce a seis horas. El equipo debe registrar la hora de recepcion y la hora de cierre en el sistema.'),
 (3, 1, 2, 2, 'Revision de resultados. La revision debe realizarse al finalizar el periodo de respuesta. Si se detectan inconsistencias en los datos, se adelanta el analisis y se notifica al responsable del area.'),
 (4, 1, 3, 3, 'Criterios de escalamiento. Ante discrepancias relevantes, reprocesos o alta demanda de consultas, el caso se escala a nivel 1 y se notifica al coordinador en un plazo no mayor a cinco minutos.'),
 (5, 1, 4, 4, 'Registro y trazabilidad. Toda consulta sobre este informe debe quedar registrada en el historial de la plataforma, indicando la pagina de origen de la informacion consultada.');

INSERT IGNORE INTO conversations (id, title, created_at) VALUES
 (1, 'Consulta de informe de analisis de procesos', '2026-11-10 08:30:00');

INSERT IGNORE INTO messages (id, conversation_id, role, content, model, sources, created_at) VALUES
 (1, 1, 'USER', 'Cual es el tiempo de respuesta en nivel 2?', NULL, NULL, '2026-11-10 08:30:05'),
 (2, 1, 'ASSISTANT',
  'Segun el documento, el tiempo medio de atencion de una solicitud de informacion de nivel 2 es de doce horas (pagina 2).',
  'MISTRAL', 'pagina 2 | El tiempo medio de atencion de una solicitud de informacion de nivel 2 es de doce horas.',
  '2026-11-10 08:30:06');

INSERT IGNORE INTO processing_logs (id, document_id, step, status, attempt, message, created_at) VALUES
 (1, 1, 'RECEIVED', 'SUCCESS', 1, 'Evento de nuevo documento recibido', '2026-11-10 08:15:00'),
 (2, 1, 'OCR', 'SUCCESS', 1, 'Extraccion de texto completada: 4 paginas', '2026-11-10 08:15:02'),
 (3, 1, 'VALIDATION', 'SUCCESS', 1, 'Texto validado: 1180 caracteres', '2026-11-10 08:15:02'),
 (4, 1, 'CHUNKING', 'SUCCESS', 1, '5 fragmentos generados con solapamiento', '2026-11-10 08:15:03'),
 (5, 1, 'INDEXING', 'SUCCESS', 1, '5 fragmentos indexados con numero de pagina', '2026-11-10 08:15:04'),
 (6, 1, 'READY', 'SUCCESS', 1, 'Documento disponible para consulta', '2026-11-10 08:15:04'),
 (7, 2, 'RECEIVED', 'SUCCESS', 1, 'Evento de nuevo documento recibido', '2026-11-10 08:22:00'),
 (8, 2, 'OCR', 'RETRY', 1, 'Texto insuficiente; reintento en 500 ms', '2026-11-10 08:22:02'),
 (9, 2, 'OCR', 'RETRY', 2, 'Texto insuficiente; reintento en 1000 ms', '2026-11-10 08:22:05'),
 (10, 2, 'OCR', 'FAILED', 3, 'OCR sin texto suficiente tras 3 intentos', '2026-11-10 08:22:09');
