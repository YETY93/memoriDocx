package com.memoridocx.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record ChatRequest(
        @NotBlank(message = "La pregunta es obligatoria")
        String question,

        @NotNull(message = "El documento es obligatorio")
        Long documentId,

        String model
) {
}
