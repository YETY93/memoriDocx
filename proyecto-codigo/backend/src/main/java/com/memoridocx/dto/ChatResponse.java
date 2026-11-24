package com.memoridocx.dto;

import java.util.List;

public record ChatResponse(
        String answer,
        List<SourceRef> sources,
        String model,
        long responseTimeMs,
        int retrievedCount,
        Long conversationId
) {
}
