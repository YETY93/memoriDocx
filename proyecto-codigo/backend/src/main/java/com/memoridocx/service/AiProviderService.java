package com.memoridocx.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.memoridocx.entity.AiProvider;
import com.memoridocx.repository.AiProviderRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Capa de abstraccion de proveedores de IA. Si existe una API key en el
 * entorno se llama al proveedor real; si no, devuelve null y el ChatService
 * genera una respuesta fundamentada en el contexto recuperado (modo demo).
 */
@Service
public class AiProviderService {

    private static final Logger log = LoggerFactory.getLogger(AiProviderService.class);

    private final AiProviderRepository providerRepository;
    private final ObjectMapper objectMapper;

    @Value("${memoridocx.ai.timeout-ms:40000}")
    private long timeoutMs;

    public AiProviderService(AiProviderRepository providerRepository, ObjectMapper objectMapper) {
        this.providerRepository = providerRepository;
        this.objectMapper = objectMapper;
    }

    public List<AiProvider> list() {
        return providerRepository.findAllByOrderByIdAsc();
    }

    public String generate(String code, String question, String context) {
        Optional<AiProvider> found = providerRepository.findByCode(code);
        if (found.isEmpty() || !Boolean.TRUE.equals(found.get().getEnabled())) {
            return null;
        }
        AiProvider provider = found.get();
        String apiKey = apiKeyFor(code);
        if (apiKey == null || apiKey.isBlank()) {
            return null;
        }

        try {
            String system = "Responde únicamente con base en el siguiente contexto documental. "
                    + "Si la respuesta no aparece en el contexto, indícalo explícitamente. "
                    + "Menciona la página de origen cuando sea posible.\n\n" + context;

            Map<String, Object> body = new LinkedHashMap<>();
            body.put("model", provider.getModelId());
            body.put("temperature", 0.2);
            body.put("max_tokens", 800);
            body.put("messages", List.of(
                    Map.of("role", "system", "content", system),
                    Map.of("role", "user", "content", question)
            ));
            String payload = objectMapper.writeValueAsString(body);

            String url = provider.getBaseUrl().replaceAll("/+$", "") + "/chat/completions";
            HttpClient client = HttpClient.newBuilder()
                    .version(HttpClient.Version.HTTP_1_1)
                    .connectTimeout(Duration.ofMillis(timeoutMs))
                    .followRedirects(HttpClient.Redirect.NORMAL)
                    .build();
            HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                    .timeout(Duration.ofMillis(timeoutMs))
                    .header("Authorization", "Bearer " + apiKey)
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(payload, StandardCharsets.UTF_8))
                    .build();

            HttpResponse<String> response = client.send(request,
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            if (response.statusCode() / 100 != 2) {
                throw new IllegalStateException("HTTP " + response.statusCode() + ": " + response.body());
            }

            JsonNode root = objectMapper.readTree(response.body());
            JsonNode content = root.path("choices").path(0).path("message").path("content");
            StringBuilder texto = new StringBuilder();
            if (content.isTextual()) {
                texto.append(content.asText());
            } else if (content.isArray()) {
                for (JsonNode bloque : content) {
                    if ("text".equals(bloque.path("type").asText()) && bloque.hasNonNull("text")) {
                        texto.append(bloque.path("text").asText());
                    }
                }
            }
            String answer = texto.toString().trim();
            if (!answer.isBlank()) return answer;
        } catch (Exception ex) {
            log.warn("No fue posible consultar al proveedor {}: {}", code, ex.getMessage());
        }
        return null;
    }

    private String apiKeyFor(String code) {
        String variable = switch (code) {
            case "MISTRAL" -> "MISTRAL_API_KEY";
            case "DEEPSEEK" -> "DEEPSEEK_API_KEY";
            case "GLM" -> "GLM_API_KEY";
            default -> "OPENAI_API_KEY";
        };
        String valor = System.getenv(variable);
        return (valor != null && !valor.isBlank()) ? valor : readDotEnv(variable);
    }

    /** Lee proyecto-codigo/.env cuando la variable de entorno no esta definida. */
    private String readDotEnv(String variable) {
        java.io.File[] candidatos = {
                new java.io.File(System.getProperty("user.dir"), ".env"),
                new java.io.File(System.getProperty("user.dir"), ".." + java.io.File.separator + ".env"),
                new java.io.File(System.getProperty("user.dir"),
                        ".." + java.io.File.separator + ".." + java.io.File.separator + ".env")
        };
        for (java.io.File archivo : candidatos) {
            if (!archivo.exists()) continue;
            try (var lineas = java.nio.file.Files.lines(archivo.toPath())) {
                String encontrado = lineas
                        .filter(l -> l.trim().startsWith(variable + "="))
                        .map(l -> l.substring(l.indexOf('=') + 1).trim()
                                .replaceAll("^\"|\"$", ""))
                        .findFirst().orElse(null);
                if (encontrado != null && !encontrado.isBlank()) return encontrado;
            } catch (Exception ignored) {
                // Se prueba el siguiente candidato
            }
        }
        return null;
    }
}
