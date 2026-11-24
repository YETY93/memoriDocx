package com.memoridocx.controller;

import com.memoridocx.entity.AiProvider;
import com.memoridocx.entity.Conversation;
import com.memoridocx.entity.Message;
import com.memoridocx.entity.ProcessingLog;
import com.memoridocx.repository.ConversationRepository;
import com.memoridocx.repository.MessageRepository;
import com.memoridocx.service.AiProviderService;
import com.memoridocx.service.DocumentService;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class MetaController {

    private final DocumentService documentService;
    private final ConversationRepository conversationRepository;
    private final MessageRepository messageRepository;
    private final AiProviderService aiProviderService;

    public MetaController(DocumentService documentService,
                          ConversationRepository conversationRepository,
                          MessageRepository messageRepository,
                          AiProviderService aiProviderService) {
        this.documentService = documentService;
        this.conversationRepository = conversationRepository;
        this.messageRepository = messageRepository;
        this.aiProviderService = aiProviderService;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        Map<String, String> body = new LinkedHashMap<>();
        body.put("status", "UP");
        body.put("database", "memoridocx");
        body.put("service", "memoridocx-backend");
        return body;
    }

    @GetMapping("/logs")
    public List<ProcessingLog> logs(@RequestParam(required = false) Long documentId) {
        return documentService.logs(documentId);
    }

    @GetMapping("/conversations")
    public List<Conversation> conversations() {
        return conversationRepository.findAllByOrderByIdDesc();
    }

    @GetMapping("/conversations/{id}/messages")
    public List<Message> messages(@PathVariable Long id) {
        return messageRepository.findByConversationIdOrderByIdAsc(id);
    }

    @GetMapping("/providers")
    public List<AiProvider> providers() {
        return aiProviderService.list();
    }
}
