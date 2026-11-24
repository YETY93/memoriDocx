package com.memoridocx.service;

import com.memoridocx.entity.DocumentChunk;
import com.memoridocx.entity.DocumentEntity;
import com.memoridocx.entity.ProcessingLog;
import com.memoridocx.exception.ResourceNotFoundException;
import com.memoridocx.repository.DocumentChunkRepository;
import com.memoridocx.repository.DocumentRepository;
import com.memoridocx.repository.ProcessingLogRepository;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository chunkRepository;
    private final ProcessingLogRepository logRepository;
    private final ProcessingService processingService;

    public DocumentService(DocumentRepository documentRepository,
                           DocumentChunkRepository chunkRepository,
                           ProcessingLogRepository logRepository,
                           ProcessingService processingService) {
        this.documentRepository = documentRepository;
        this.chunkRepository = chunkRepository;
        this.logRepository = logRepository;
        this.processingService = processingService;
    }

    public List<DocumentEntity> list() {
        return documentRepository.findAllByOrderByIdDesc();
    }

    public DocumentEntity get(Long id) {
        return documentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Documento no encontrado: " + id));
    }

    public List<DocumentChunk> chunks(Long id) {
        get(id);
        return chunkRepository.findByDocumentIdOrderByChunkIndexAsc(id);
    }

    public DocumentEntity upload(MultipartFile file) throws IOException {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("El archivo PDF está vacío");
        }
        String original = file.getOriginalFilename() == null ? "documento.pdf" : file.getOriginalFilename();
        String stored = UUID.randomUUID() + "_" + original.replaceAll("[^a-zA-Z0-9._-]", "_");

        Path uploadDir = Paths.get(System.getProperty("user.dir"), "uploads");
        Files.createDirectories(uploadDir);
        Path target = uploadDir.resolve(stored);
        file.transferTo(target);

        DocumentEntity doc = new DocumentEntity();
        doc.setOriginalName(original);
        doc.setStoredName(stored);
        doc.setContentType(file.getContentType());
        doc.setSizeBytes(file.getSize());
        doc.setStatus("PROCESSING");
        doc.setUploadedAt(LocalDateTime.now());
        doc = documentRepository.save(doc);

        log(doc.getId(), "RECEIVED", "SUCCESS", 1,
                "Evento de nuevo documento recibido: " + original);

        processingService.process(doc.getId(), target);
        return doc;
    }

    public void delete(Long id) {
        DocumentEntity doc = get(id);
        if (doc.getStoredName() != null) {
            try {
                Files.deleteIfExists(Paths.get(System.getProperty("user.dir"), "uploads", doc.getStoredName()));
            } catch (IOException ignored) {
                // El archivo fisico es secundario; se elimina el registro aunque falle.
            }
        }
        documentRepository.delete(doc);
    }

    public List<ProcessingLog> logs(Long documentId) {
        if (documentId == null) return logRepository.findAllByOrderByIdDesc();
        get(documentId);
        return logRepository.findByDocumentIdOrderByIdAsc(documentId);
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
}
