package com.memoridocx.controller;

import com.memoridocx.entity.DocumentChunk;
import com.memoridocx.entity.DocumentEntity;
import com.memoridocx.service.DocumentService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private final DocumentService documentService;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @GetMapping
    public List<DocumentEntity> list() {
        return documentService.list();
    }

    @GetMapping("/{id}")
    public DocumentEntity get(@PathVariable Long id) {
        return documentService.get(id);
    }

    @GetMapping("/{id}/chunks")
    public List<DocumentChunk> chunks(@PathVariable Long id) {
        return documentService.chunks(id);
    }

    @PostMapping("/upload")
    public ResponseEntity<DocumentEntity> upload(@RequestParam("file") MultipartFile file) throws Exception {
        DocumentEntity created = documentService.upload(file);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        documentService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
