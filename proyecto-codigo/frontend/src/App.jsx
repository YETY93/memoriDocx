import { useCallback, useEffect, useRef, useState } from 'react';

const FALLBACK_MODELS = [
  { code: 'MISTRAL', displayName: 'Mistral' },
  { code: 'DEEPSEEK', displayName: 'DeepSeek' },
  { code: 'GLM', displayName: 'GLM' },
];

const STATUS_LABELS = {
  PENDING: 'Pendiente',
  UPLOADED: 'Cargado',
  QUEUED: 'En cola',
  PROCESSING: 'Procesando',
  PROCESSED: 'Procesado',
  COMPLETED: 'Completado',
  READY: 'Listo',
  FAILED: 'Error',
  ERROR: 'Error',
};

async function apiFetch(path, options = {}) {
  let response;
  try {
    response = await fetch(path, options);
  } catch (error) {
    throw new Error(
      `No se pudo conectar con el servidor (${path}). Comprueba que el backend esté activo en http://localhost:8080.`,
    );
  }

  if (!response.ok) {
    let detail = '';
    try {
      const body = await response.json();
      detail = body.message || body.error || body.errorMessage || '';
      if (!detail && typeof body === 'string') detail = body;
      if (!detail) detail = JSON.stringify(body);
    } catch (_) {
      detail = (await response.text().catch(() => '')) || '';
    }
    throw new Error(
      `Error ${response.status} al consultar ${path}${detail ? `: ${detail}` : ''}`,
    );
  }

  if (response.status === 204) return null;
  try {
    return await response.json();
  } catch (_) {
    return null;
  }
}

function formatBytes(bytes) {
  if (bytes === null || bytes === undefined || Number.isNaN(Number(bytes))) return '—';
  const value = Number(bytes);
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString('es-ES', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
}

function statusLabel(status) {
  if (!status) return 'Desconocido';
  return STATUS_LABELS[String(status).toUpperCase()] || status;
}

function statusVariant(status) {
  const value = String(status || '').toUpperCase();
  if (value.includes('FAIL') || value.includes('ERROR')) return 'error';
  if (
    value.includes('PROCESS') ||
    value.includes('PENDING') ||
    value.includes('QUEUE') ||
    value.includes('UPLOAD')
  ) {
    return 'warning';
  }
  if (
    value.includes('PROCESSED') ||
    value.includes('COMPLETED') ||
    value.includes('READY') ||
    value.includes('SUCCESS')
  ) {
    return 'success';
  }
  return 'neutral';
}

function Alert({ message, type = 'error' }) {
  if (!message) return null;
  return (
    <div className={`alert alert-${type}`} role="alert">
      {message}
    </div>
  );
}

export default function App() {
  const [health, setHealth] = useState(null);
  const [healthError, setHealthError] = useState('');

  const [documents, setDocuments] = useState([]);
  const [documentsError, setDocumentsError] = useState('');
  const [loadingDocuments, setLoadingDocuments] = useState(true);

  const [selectedDocumentId, setSelectedDocumentId] = useState('');
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadNotice, setUploadNotice] = useState(null);
  const fileInputRef = useRef(null);

  const [chunks, setChunks] = useState([]);
  const [chunksDocName, setChunksDocName] = useState('');
  const [chunksError, setChunksError] = useState('');
  const [loadingChunks, setLoadingChunks] = useState(false);

  const [providers, setProviders] = useState(FALLBACK_MODELS);
  const [model, setModel] = useState('MISTRAL');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [queryError, setQueryError] = useState('');
  const [querying, setQuerying] = useState(false);

  const [logs, setLogs] = useState([]);
  const [logsError, setLogsError] = useState('');
  const [loadingLogs, setLoadingLogs] = useState(false);

  const loadDocuments = useCallback(async () => {
    setLoadingDocuments(true);
    setDocumentsError('');
    try {
      const data = await apiFetch('/api/documents');
      setDocuments(Array.isArray(data) ? data : []);
    } catch (error) {
      setDocumentsError(error.message);
      setDocuments([]);
    } finally {
      setLoadingDocuments(false);
    }
  }, []);

  const loadHealth = useCallback(async () => {
    setHealthError('');
    try {
      const data = await apiFetch('/api/health');
      setHealth(data);
    } catch (error) {
      setHealth(null);
      setHealthError(error.message);
    }
  }, []);

  const loadProviders = useCallback(async () => {
    try {
      const data = await apiFetch('/api/providers');
      const list = Array.isArray(data) ? data : [];
      setProviders(list.length ? list : FALLBACK_MODELS);
    } catch (_) {
      setProviders(FALLBACK_MODELS);
    }
  }, []);

  useEffect(() => {
    loadHealth();
    loadDocuments();
    loadProviders();
  }, [loadHealth, loadDocuments, loadProviders]);

  useEffect(() => {
    if (!selectedDocumentId) {
      setLogs([]);
      setLogsError('');
      return;
    }
    let cancelled = false;
    setLoadingLogs(true);
    setLogsError('');
    apiFetch(`/api/logs?documentId=${encodeURIComponent(selectedDocumentId)}`)
      .then((data) => {
        if (!cancelled) setLogs(Array.isArray(data) ? data : []);
      })
      .catch((error) => {
        if (!cancelled) {
          setLogsError(error.message);
          setLogs([]);
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingLogs(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedDocumentId]);

  const selectedDocument = documents.find(
    (document) => String(document.id) === String(selectedDocumentId),
  );
  const queryDocumentId = selectedDocument ? selectedDocument.id : selectedDocumentId;

  async function handleUpload(event) {
    event.preventDefault();
    if (!uploadFile) {
      setUploadNotice({ type: 'error', text: 'Selecciona un archivo PDF antes de subirlo.' });
      return;
    }
    setUploading(true);
    setUploadNotice(null);
    const formData = new FormData();
    formData.append('file', uploadFile);
    try {
      const created = await apiFetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });
      setUploadNotice({
        type: 'success',
        text: `Documento "${created?.originalName || uploadFile.name}" cargado correctamente.`,
      });
      setUploadFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      await loadDocuments();
    } catch (error) {
      setUploadNotice({ type: 'error', text: error.message });
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(document) {
    const name = document.originalName || `documento ${document.id}`;
    if (!window.confirm(`¿Eliminar el documento "${name}"? Esta acción no se puede deshacer.`)) {
      return;
    }
    try {
      await apiFetch(`/api/documents/${encodeURIComponent(document.id)}`, { method: 'DELETE' });
      setDocumentsError('');
      if (String(selectedDocumentId) === String(document.id)) setSelectedDocumentId('');
      if (chunksDocName && String(chunksDocName.id) === String(document.id)) {
        setChunksDocName('');
        setChunks([]);
      }
      await loadDocuments();
    } catch (error) {
      setDocumentsError(error.message);
    }
  }

  async function handleViewChunks(document) {
    setChunksError('');
    setLoadingChunks(true);
    setChunksDocName(document);
    setChunks([]);
    try {
      const data = await apiFetch(
        `/api/documents/${encodeURIComponent(document.id)}/chunks`,
      );
      setChunks(Array.isArray(data) ? data : []);
    } catch (error) {
      setChunksError(error.message);
    } finally {
      setLoadingChunks(false);
    }
  }

  async function handleQuery(event) {
    event.preventDefault();
    setQueryError('');
    if (!selectedDocumentId) {
      setQueryError('Selecciona un documento para realizar la consulta.');
      return;
    }
    if (!question.trim()) {
      setQueryError('Escribe una pregunta antes de consultar.');
      return;
    }
    setQuerying(true);
    setAnswer(null);
    try {
      const data = await apiFetch('/api/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          documentId: queryDocumentId,
          model,
        }),
      });
      setAnswer(data);
    } catch (error) {
      setQueryError(error.message);
    } finally {
      setQuerying(false);
    }
  }

  const healthStatus = health?.status
    ? String(health.status).toUpperCase()
    : null;
  const healthVariant =
    healthStatus && /UP|OK|HEALTHY|CONNECTED/.test(healthStatus) ? 'success' : 'warning';

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>memoriDocx</h1>
          <p className="subtitle">
            Gestión de documentos, asistente inteligente y trazabilidad del procesamiento
          </p>
        </div>
        <div className="connection-status">
          {healthError ? (
            <span className="status-badge error" title={healthError}>
              Sin conexión con el backend
            </span>
          ) : health ? (
            <>
              <span className={`status-badge ${healthVariant}`}>
                Backend: {health.status}
              </span>
              {health.database && (
                <span className="muted small">BD: {health.database}</span>
              )}
            </>
          ) : (
            <span className="muted small">Comprobando conexión…</span>
          )}
        </div>
      </header>
      {healthError && <Alert message={healthError} />}

      <main className="panels">
        {/* Panel 1: Documentos */}
        <section className="panel" aria-labelledby="documentos-title">
          <div className="panel-header">
            <h2 id="documentos-title">Documentos</h2>
            <span className="count-badge">{documents.length}</span>
          </div>

          <form className="upload-form" onSubmit={handleUpload}>
            <label className="field-label" htmlFor="pdf-file">
              Cargar PDF
            </label>
            <input
              id="pdf-file"
              ref={fileInputRef}
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setUploadFile(event.target.files?.[0] || null)}
            />
            <button type="submit" disabled={uploading || !uploadFile}>
              {uploading ? 'Subiendo…' : 'Subir documento'}
            </button>
          </form>
          {uploadNotice && (
            <Alert message={uploadNotice.text} type={uploadNotice.type} />
          )}
          <Alert message={documentsError} />

          <div className="document-list">
            {loadingDocuments ? (
              <p className="muted">Cargando documentos…</p>
            ) : documents.length === 0 ? (
              <p className="muted">No hay documentos registrados.</p>
            ) : (
              documents.map((document) => (
                <article
                  key={document.id}
                  className={`document-card ${
                    String(selectedDocumentId) === String(document.id) ? 'selected' : ''
                  }`}
                >
                  <div className="document-card-head">
                    <strong title={document.originalName}>
                      {document.originalName || `Documento #${document.id}`}
                    </strong>
                    <span className={`status-badge ${statusVariant(document.status)}`}>
                      {statusLabel(document.status)}
                    </span>
                  </div>
                  <dl className="document-meta">
                    <div>
                      <dt>Páginas</dt>
                      <dd>{document.pageCount ?? '—'}</dd>
                    </div>
                    <div>
                      <dt>Fragmentos</dt>
                      <dd>{document.chunkCount ?? '—'}</dd>
                    </div>
                    <div>
                      <dt>Tamaño</dt>
                      <dd>{formatBytes(document.sizeBytes)}</dd>
                    </div>
                    <div>
                      <dt>Subido</dt>
                      <dd>{formatDate(document.uploadedAt)}</dd>
                    </div>
                    <div>
                      <dt>Procesado</dt>
                      <dd>{formatDate(document.processedAt)}</dd>
                    </div>
                  </dl>
                  {document.errorMessage && (
                    <p className="error-text">{document.errorMessage}</p>
                  )}
                  <div className="button-row">
                    <label className="select-inline">
                      <input
                        type="radio"
                        name="documento-activo"
                        checked={String(selectedDocumentId) === String(document.id)}
                        onChange={() => setSelectedDocumentId(String(document.id))}
                      />
                      Seleccionar
                    </label>
                    <button
                      type="button"
                      className="button-secondary"
                      onClick={() => handleViewChunks(document)}
                    >
                      Ver fragmentos
                    </button>
                    <button
                      type="button"
                      className="button-danger"
                      onClick={() => handleDelete(document)}
                    >
                      Eliminar
                    </button>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        {/* Panel 2: Asistente */}
        <section className="panel" aria-labelledby="asistente-title">
          <div className="panel-header">
            <h2 id="asistente-title">Asistente</h2>
          </div>

          <form className="query-form" onSubmit={handleQuery}>
            <label className="field-label" htmlFor="query-document">
              Documento
            </label>
            <select
              id="query-document"
              value={selectedDocumentId}
              onChange={(event) => setSelectedDocumentId(event.target.value)}
            >
              <option value="">Selecciona un documento…</option>
              {documents.map((document) => (
                <option key={document.id} value={document.id}>
                  {document.originalName || `Documento #${document.id}`}
                </option>
              ))}
            </select>

            <label className="field-label" htmlFor="query-model">
              Modelo
            </label>
            <select
              id="query-model"
              value={model}
              onChange={(event) => setModel(event.target.value)}
            >
              {providers.map((provider) => (
                <option key={provider.code || provider.id} value={provider.code}>
                  {provider.displayName || provider.code}
                  {provider.active === false ? ' (inactivo)' : ''}
                </option>
              ))}
            </select>

            <label className="field-label" htmlFor="query-question">
              Pregunta
            </label>
            <textarea
              id="query-question"
              rows={4}
              placeholder="¿Qué información necesitas del documento?"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />

            <button type="submit" disabled={querying}>
              {querying ? 'Consultando…' : 'Consultar'}
            </button>
          </form>
          <Alert message={queryError} />

          {answer && (
            <div className="answer-box">
              <h3>Respuesta</h3>
              <p className="answer-text">{answer.answer || 'Sin respuesta.'}</p>
              <div className="metrics">
                <span>
                  Modelo: <strong>{answer.model || model}</strong>
                </span>
                <span>
                  Tiempo: <strong>{answer.responseTimeMs ?? '—'} ms</strong>
                </span>
                <span>
                  Fragmentos recuperados: <strong>{answer.retrievedCount ?? 0}</strong>
                </span>
              </div>

              <h4>Fuentes</h4>
              {Array.isArray(answer.sources) && answer.sources.length > 0 ? (
                <ol className="sources-list">
                  {answer.sources.map((source, index) => (
                    <li key={`${source.page}-${index}`}>
                      <span className="source-page">Página {source.page ?? '—'}</span>
                      <p>{source.excerpt || 'Sin extracto.'}</p>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="muted">No se registraron fuentes para esta respuesta.</p>
              )}
            </div>
          )}
        </section>

        {/* Panel 3: Trazabilidad */}
        <section className="panel" aria-labelledby="trazabilidad-title">
          <div className="panel-header">
            <h2 id="trazabilidad-title">Trazabilidad</h2>
            {selectedDocument && (
              <span className="muted small" title={selectedDocument.originalName}>
                {selectedDocument.originalName || `Documento #${selectedDocument.id}`}
              </span>
            )}
          </div>

          <h3>Registros de procesamiento</h3>
          <Alert message={logsError} />
          {!selectedDocumentId ? (
            <p className="muted">Selecciona un documento para ver sus registros.</p>
          ) : loadingLogs ? (
            <p className="muted">Cargando registros…</p>
          ) : logs.length === 0 ? (
            <p className="muted">No hay registros para este documento.</p>
          ) : (
            <div className="table-scroll">
              <table className="logs-table">
                <thead>
                  <tr>
                    <th>Paso</th>
                    <th>Estado</th>
                    <th>Intento</th>
                    <th>Mensaje</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td>{log.step ?? '—'}</td>
                      <td>
                        <span className={`status-badge ${statusVariant(log.status)}`}>
                          {statusLabel(log.status)}
                        </span>
                      </td>
                      <td>{log.attempt ?? '—'}</td>
                      <td>{log.message || '—'}</td>
                      <td className="nowrap">{formatDate(log.createdAt)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <h3 className="section-gap">Proveedores de IA</h3>
          <ul className="provider-list">
            {providers.map((provider) => (
              <li key={provider.id || provider.code}>
                <div>
                  <strong>{provider.displayName || provider.code}</strong>
                  <span className="muted small">
                    {' '}
                    · {provider.code} · {provider.modelId || 'modelo no indicado'}
                  </span>
                </div>
                <div className="provider-flags">
                  <span className={`status-badge ${provider.enabled === false ? 'neutral' : 'success'}`}>
                    {provider.enabled === false ? 'Deshabilitado' : 'Habilitado'}
                  </span>
                  {provider.active && <span className="status-badge success">Activo</span>}
                </div>
              </li>
            ))}
          </ul>
        </section>
      </main>

      {/* Modal de fragmentos */}
      {chunksDocName && (
        <div className="modal-backdrop" onClick={() => setChunksDocName('')}>
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="chunks-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <h2 id="chunks-title">
                Fragmentos de {chunksDocName.originalName || `documento #${chunksDocName.id}`}
              </h2>
              <button
                type="button"
                className="button-secondary"
                onClick={() => setChunksDocName('')}
              >
                Cerrar
              </button>
            </div>
            <Alert message={chunksError} />
            {loadingChunks ? (
              <p className="muted">Cargando fragmentos…</p>
            ) : chunks.length === 0 && !chunksError ? (
              <p className="muted">Este documento todavía no tiene fragmentos.</p>
            ) : (
              <div className="chunk-list">
                {chunks.map((chunk) => (
                  <article key={chunk.id} className="chunk-card">
                    <div className="chunk-head">
                      <span>Página {chunk.pageNumber ?? '—'}</span>
                      <span>Fragmento {chunk.chunkIndex ?? '—'}</span>
                    </div>
                    <p>{chunk.content}</p>
                  </article>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
