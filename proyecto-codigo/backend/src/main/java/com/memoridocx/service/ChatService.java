package com.memoridocx.service;

import com.memoridocx.dto.ChatRequest;
import com.memoridocx.dto.ChatResponse;
import com.memoridocx.dto.SourceRef;
import com.memoridocx.entity.Conversation;
import com.memoridocx.entity.DocumentChunk;
import com.memoridocx.entity.DocumentEntity;
import com.memoridocx.entity.Message;
import com.memoridocx.exception.ResourceNotFoundException;
import com.memoridocx.repository.ConversationRepository;
import com.memoridocx.repository.DocumentChunkRepository;
import com.memoridocx.repository.DocumentRepository;
import com.memoridocx.repository.MessageRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.stream.Collectors;

@Service
public class ChatService {

    private static final Logger log = LoggerFactory.getLogger(ChatService.class);

    private static final Set<String> STOPWORDS = Set.of(
            "el", "la", "los", "las", "de", "del", "un", "una", "unos", "unas", "en", "es", "son",
            "se", "su", "sus", "al", "lo", "por", "para", "con", "y", "o", "que", "cual", "como",
            "cuando", "donde", "porque", "esta", "este", "esto", "sobre", "según", "segun"
    );

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository chunkRepository;
    private final ConversationRepository conversationRepository;
    private final MessageRepository messageRepository;
    private final AiProviderService aiProviderService;

    @Value("${memoridocx.retrieval.max-chunks:3}")
    private int maxChunks;

    @Value("${memoridocx.retrieval.min-score:0.05}")
    private double minScore;

    public ChatService(DocumentRepository documentRepository,
                       DocumentChunkRepository chunkRepository,
                       ConversationRepository conversationRepository,
                       MessageRepository messageRepository,
                       AiProviderService aiProviderService) {
        this.documentRepository = documentRepository;
        this.chunkRepository = chunkRepository;
        this.conversationRepository = conversationRepository;
        this.messageRepository = messageRepository;
        this.aiProviderService = aiProviderService;
    }

    public ChatResponse query(ChatRequest request) {
        long started = System.currentTimeMillis();

        DocumentEntity document = documentRepository.findById(request.documentId())
                .orElseThrow(() -> new ResourceNotFoundException("Documento no encontrado: " + request.documentId()));
        if (!"AVAILABLE".equals(document.getStatus())) {
            throw new IllegalStateException("El documento aún no está disponible para consulta. Estado: "
                    + document.getStatus());
        }

        String model = (request.model() == null || request.model().isBlank())
                ? "MISTRAL" : request.model().trim().toUpperCase(Locale.ROOT);

        List<DocumentChunk> chunks = chunkRepository.findByDocumentIdOrderByChunkIndexAsc(document.getId());
        Set<String> questionTokens = tokenize(request.question());

        List<Scored> ranked = new ArrayList<>();
        for (DocumentChunk chunk : chunks) {
            Set<String> chunkTokens = tokenize(chunk.getContent());
            if (questionTokens.isEmpty() || chunkTokens.isEmpty()) continue;
            int matches = 0;
            for (String token : questionTokens) {
                if (chunkTokens.contains(token)) matches++;
            }
            double score = (double) matches / questionTokens.size();
            if (score >= minScore) ranked.add(new Scored(chunk, score));
        }
        ranked.sort(Comparator.comparingDouble(Scored::score).reversed());
        List<Scored> top = ranked.stream().limit(maxChunks).toList();

        List<SourceRef> sources = top.stream()
                .map(s -> new SourceRef(s.chunk().getPageNumber(), excerpt(s.chunk().getContent(), 260)))
                .toList();

        String context = top.stream()
                .map(s -> "Página " + s.chunk().getPageNumber() + ": " + s.chunk().getContent())
                .collect(Collectors.joining("\n\n"));

        String answer = aiProviderService.generate(model, request.question(), context);
        if (answer == null || answer.isBlank()) {
            answer = groundedAnswer(top);
        }

        Conversation conversation = new Conversation();
        String title = request.question().length() > 60
                ? request.question().substring(0, 60) + "…" : request.question();
        conversation.setTitle(title);
        conversation = conversationRepository.save(conversation);

        saveMessage(conversation.getId(), "USER", request.question(), null, null);
        String sourcesText = sources.stream()
                .map(s -> "pagina " + s.page() + " | " + s.excerpt())
                .collect(Collectors.joining(" ; "));
        saveMessage(conversation.getId(), "ASSISTANT", answer, model, sourcesText);

        long elapsed = System.currentTimeMillis() - started;
        log.info("Consulta respondida con modelo {} | fragmentos={} | {} ms",
                model, top.size(), elapsed);

        return new ChatResponse(answer, sources, model, elapsed, top.size(), conversation.getId());
    }

    private String groundedAnswer(List<Scored> top) {
        if (top.isEmpty()) {
            return "La información consultada no se encuentra en el documento cargado. "
                    + "Se recomienda verificar el contenido del archivo o formular la pregunta de otra manera.";
        }
        SourceRef first = top.stream()
                .map(s -> new SourceRef(s.chunk().getPageNumber(), excerpt(s.chunk().getContent(), 240)))
                .findFirst().orElseThrow();
        StringBuilder sb = new StringBuilder("Según el documento, ");
        sb.append(first.excerpt().replaceFirst("^\\s+", ""));
        sb.append(" (página ").append(first.page()).append(").");
        if (top.size() > 1) {
            sb.append(" Información relacionada en la página ").append(top.get(1).chunk().getPageNumber()).append(".");
        }
        return sb.toString();
    }

    private void saveMessage(Long conversationId, String role, String content, String model, String sources) {
        Message message = new Message();
        message.setConversationId(conversationId);
        message.setRole(role);
        message.setContent(content);
        message.setModel(model);
        message.setSources(sources);
        messageRepository.save(message);
    }

    private String excerpt(String text, int max) {
        String clean = text.replaceAll("\\s+", " ").trim();
        return clean.length() <= max ? clean : clean.substring(0, max).trim() + "…";
    }

    private Set<String> tokenize(String text) {
        String normalized = Normalizer.normalize(text == null ? "" : text, Normalizer.Form.NFD)
                .replaceAll("\\p{InCombiningDiacriticalMarks}+", "")
                .toLowerCase(Locale.ROOT);
        return java.util.Arrays.stream(normalized.split("[^a-z0-9]+"))
                .filter(t -> t.length() > 1)
                .filter(t -> !STOPWORDS.contains(t))
                .collect(Collectors.toSet());
    }

    private record Scored(DocumentChunk chunk, double score) { }
}
