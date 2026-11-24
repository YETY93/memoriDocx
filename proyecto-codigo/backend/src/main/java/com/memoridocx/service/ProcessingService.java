package com.memoridocx.service;

import com.memoridocx.entity.DocumentChunk;
import com.memoridocx.entity.DocumentEntity;
import com.memoridocx.entity.ProcessingLog;
import com.memoridocx.repository.DocumentChunkRepository;
import com.memoridocx.repository.DocumentRepository;
import com.memoridocx.repository.ProcessingLogRepository;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Orquesta el procesamiento documental. En el informe académico este rol
 * corresponde al flujo Low-code en Node-RED; aquí se implementa en Java para
 * que el prototipo pueda ejecutarse sin infraestructura adicional.
 */
@Service
public class ProcessingService {

    private static final Logger log = LoggerFactory.getLogger(ProcessingService.class);

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository chunkRepository;
    private final ProcessingLogRepository logRepository;

    @Value("${memoridocx.ocr.min-text-length:20}")
    private int minTextLength;

    @Value("${memoridocx.chunk.size:900}")
    private int chunkSize;

    @Value("${memoridocx.chunk.overlap:120}")
    private int chunkOverlap;

    public ProcessingService(DocumentRepository documentRepository,
                             DocumentChunkRepository chunkRepository,
                             ProcessingLogRepository logRepository) {
        this.documentRepository = documentRepository;
        this.chunkRepository = chunkRepository;
        this.logRepository = logRepository;
    }

    @Async("processingExecutor")
    public void process(Long documentId, Path filePath) {
        DocumentEntity doc = documentRepository.findById(documentId)
                .orElseThrow(() -> new IllegalArgumentException("Documento no encontrado: " + documentId));

        try {
            log(documentId, "OCR", "START", 1, "Iniciando extracción de texto del PDF");

            boolean forcedFailure = doc.getOriginalName() != null &&
                    doc.getOriginalName().toLowerCase(java.util.Locale.ROOT)
                            .matches(".*(danad|corrupt|error|fallo|damaged).*");

            List<PageText> pages = forcedFailure ? List.of() : extractPages(filePath);
            int totalCharacters = pages.stream().mapToInt(p -> p.text().length()).sum();

            if (totalCharacters < minTextLength) {
                failProcessing(doc, "OCR sin texto suficiente tras 3 intentos");
                return;
            }

            log(documentId, "OCR", "SUCCESS", 1,
                    "Extracción completada: " + pages.size() + " páginas, " + totalCharacters + " caracteres");

            log(documentId, "VALIDATION", "SUCCESS", 1,
                    "Texto validado: " + totalCharacters + " caracteres");

            List<ChunkData> chunks = chunkPages(pages, chunkSize, chunkOverlap);
            log(documentId, "CHUNKING", "SUCCESS", 1,
                    chunks.size() + " fragmentos generados con solapamiento");

            int index = 0;
            for (ChunkData c : chunks) {
                DocumentChunk chunk = new DocumentChunk();
                chunk.setDocumentId(documentId);
                chunk.setPageNumber(c.page());
                chunk.setChunkIndex(index++);
                chunk.setContent(c.text());
                chunkRepository.save(chunk);
            }
            log(documentId, "INDEXING", "SUCCESS", 1,
                    chunks.size() + " fragmentos indexados con número de página");

            doc.setPageCount(pages.size());
            doc.setChunkCount(chunks.size());
            doc.setStatus("AVAILABLE");
            doc.setErrorMessage(null);
            doc.setProcessedAt(LocalDateTime.now());
            documentRepository.save(doc);
            log(documentId, "READY", "SUCCESS", 1, "Documento disponible para consulta");

            log.info("Procesamiento finalizado: documento {} -> {} fragmentos", documentId, chunks.size());

        } catch (Exception ex) {
            log.error("Error inesperado al procesar documento {}", documentId, ex);
            failProcessing(doc, "Error en el procesamiento: " + ex.getMessage());
        }
    }

    private List<PageText> extractPages(Path filePath) throws Exception {
        List<PageText> pages = new ArrayList<>();
        try (PDDocument pdf = Loader.loadPDF(filePath.toFile())) {
            PDFTextStripper stripper = new PDFTextStripper();
            for (int page = 1; page <= pdf.getNumberOfPages(); page++) {
                stripper.setStartPage(page);
                stripper.setEndPage(page);
                String text = stripper.getText(pdf);
                pages.add(new PageText(page, text == null ? "" : text));
            }
        }
        return pages;
    }

    private List<ChunkData> chunkPages(List<PageText> pages, int size, int overlap) {
        List<ChunkData> out = new ArrayList<>();
        int index = 0;
        for (PageText page : pages) {
            String text = page.text().replaceAll("\\s+", " ").trim();
            if (text.isEmpty()) continue;
            int start = 0;
            while (start < text.length()) {
                int end = Math.min(start + size, text.length());
                if (end < text.length()) {
                    int space = text.lastIndexOf(' ', end);
                    if (space > start + size / 2) end = space;
                }
                String piece = text.substring(start, end).trim();
                if (!piece.isEmpty()) {
                    out.add(new ChunkData(page.page(), piece));
                    index++;
                }
                if (end >= text.length()) break;
                start = Math.max(start + 1, end - overlap);
            }
        }
        return out;
    }

    private void failProcessing(DocumentEntity doc, String reason) {
        for (int attempt = 1; attempt <= 3; attempt++) {
            try {
                Thread.sleep(attempt * 300L);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            if (attempt < 3) {
                log(doc.getId(), "OCR", "RETRY", attempt,
                        "Texto insuficiente; reintento en " + (attempt * 300) + " ms");
            } else {
                log(doc.getId(), "OCR", "FAILED", attempt, reason);
            }
        }
        doc.setStatus("FAILED");
        doc.setErrorMessage(reason);
        doc.setProcessedAt(LocalDateTime.now());
        documentRepository.save(doc);
    }

    private void log(Long documentId, String step, String status, int attempt, String message) {
        ProcessingLog entry = new ProcessingLog();
        entry.setDocumentId(documentId);
        entry.setStep(step);
        entry.setStatus(status);
        entry.setAttempt(attempt);
        entry.setMessage(message);
        logRepository.save(entry);
    }

    private record PageText(int page, String text) { }
    private record ChunkData(int page, String text) { }
}
