# -*- coding: utf-8 -*-
"""
Pruebas funcionales del prototipo memoriDocx.
Genera evidencias en la carpeta ../evidencias

Uso:  python scripts/probar_api.py
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE = "http://localhost:8080/api"
EVID = Path(__file__).resolve().parent.parent / "evidencias"
EVID.mkdir(exist_ok=True)


def call(method, path, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def save(name, obj):
    (EVID / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  guardado:", name)


def wait_for(doc_id, timeout=25):
    deadline = time.time() + timeout
    while time.time() < deadline:
        _, doc = call("GET", f"/documents/{doc_id}")
        if doc.get("status") in ("AVAILABLE", "FAILED"):
            return doc
        time.sleep(0.5)
    return doc


def upload(path, filename):
    boundary = "----memoriDocxBoundary"
    raw = Path(path).read_bytes()
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: application/pdf\r\n\r\n'
    ).encode() + raw + f'\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(
        BASE + "/documents/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def make_pdf(path):
    import pymupdf
    doc = pymupdf.open()
    page = doc.new_page()
    text = (
        "Informe de analisis memoriDocx - documento de prueba\n\n"
        "El tiempo de observacion clinica para nivel 2 es de doce horas.\n"
        "La reevaluacion debe realizarse al finalizar el periodo de observacion.\n"
        "Ante dolor toracico, notificar al medico de guardia en cinco minutos.\n"
    )
    page.insert_text((72, 72), text, fontsize=11)
    doc.save(path)
    doc.close()


def main():
    print("Esperando al backend...")
    for _ in range(30):
        try:
            status, health = call("GET", "/health")
            if status == 200:
                print("  backend:", health)
                break
        except Exception:
            time.sleep(1)
    else:
        raise SystemExit("El backend no respondio en /api/health")

    print("\n1. Estado y datos semilla")
    _, documents = call("GET", "/documents")
    save("01_documentos.json", documents)
    _, providers = call("GET", "/providers")
    save("02_proveedores.json", providers)
    _, chunks = call("GET", "/documents/1/chunks")
    save("03_fragmentos.json", chunks)

    print("\n2. Escenario exitoso - pregunta sobre el informe")
    question = "Cual es el tiempo de respuesta en nivel 2?"
    respuestas = {}
    for model in ("MISTRAL", "DEEPSEEK", "GLM"):
        status, body = call("POST", "/chat/query",
                            {"question": question, "documentId": 1, "model": model})
        respuestas[model] = body
        save(f"04_consulta_{model.lower()}.json", body)
        print(f"  {model}: {body['retrievedCount']} fragmentos, {body['responseTimeMs']} ms")

    print("\n3. Escenario complementario - pregunta sin respuesta")
    status, sin_respuesta = call("POST", "/chat/query", {
        "question": "Cual es el presupuesto anual del area clinica?",
        "documentId": 1, "model": "MISTRAL",
    })
    save("05_pregunta_sin_respuesta.json", sin_respuesta)

    print("\n4. Carga real de PDF y consulta")
    pdf_path = EVID / "Informe_Prueba.pdf"
    make_pdf(pdf_path)
    uploaded = upload(pdf_path, "Informe_Prueba.pdf")
    final = wait_for(uploaded["id"])
    save("06_documento_cargado.json", final)
    status, consulta_cargada = call("POST", "/chat/query", {
        "question": "tiempo de respuesta",
        "documentId": uploaded["id"], "model": "MISTRAL",
    })
    save("07_consulta_documento_cargado.json", consulta_cargada)
    _, logs_cargado = call("GET", f"/logs?documentId={uploaded['id']}")
    save("08_logs_documento_cargado.json", logs_cargado)

    print("\n5. Escenario con error controlado")
    fallido = upload(pdf_path, "PDF_danado_prueba.pdf")
    final_fail = wait_for(fallido["id"])
    save("09_documento_error_controlado.json", final_fail)
    _, logs_fail = call("GET", f"/logs?documentId={fallido['id']}")
    save("10_logs_error_controlado.json", logs_fail)
    status, error_query = call("POST", "/chat/query", {
        "question": "tiempo de respuesta",
        "documentId": fallido["id"], "model": "MISTRAL",
    })
    save("11_consulta_documento_fallido.json", error_query)

    print("\n6. Historial de conversaciones")
    _, conversaciones = call("GET", "/conversations")
    save("12_conversaciones.json", conversaciones)
    if conversaciones:
        _, mensajes = call("GET", f"/conversations/{conversaciones[0]['id']}/messages")
        save("13_mensajes.json", mensajes)

    resumen = [
        "# Resultado de las pruebas funcionales",
        "",
        f"- Backend: {health['service']} ({health['status']})",
        f"- Base de datos: {health['database']}",
        f"- Documentos semilla: {len(documents)}",
        f"- Proveedores de IA: {len(providers)}",
        f"- Fragmentos del documento 1: {len(chunks)}",
        "",
        "## Comparacion de modelos (misma pregunta y documento)",
        "",
        "| Modelo | Fragmentos recuperados | Tiempo (ms) |",
        "|---|---:|---:|",
    ]
    for model, body in respuestas.items():
        resumen.append(f"| {model} | {body['retrievedCount']} | {body['responseTimeMs']} |")
    resumen += [
        "",
        "## Escenarios",
        "",
        f"- Exitoso: documento {uploaded['id']} -> {final['status']}, "
        f"{final.get('chunkCount')} fragmentos.",
        f"- Error controlado: documento {fallido['id']} -> {final_fail['status']}, "
        f"{len(logs_fail)} entradas de bitacora con reintentos.",
        f"- Sin respuesta: {sin_respuesta['retrievedCount']} fragmentos recuperados.",
        "",
    ]
    (EVID / "resumen_pruebas.md").write_text("\n".join(resumen), encoding="utf-8")
    print("\nEvidencias guardadas en:", EVID)


if __name__ == "__main__":
    main()
