package com.memoridocx.controller;

import com.memoridocx.dto.ChatRequest;
import com.memoridocx.dto.ChatResponse;
import com.memoridocx.service.ChatService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping("/query")
    public ChatResponse query(@Valid @RequestBody ChatRequest request) {
        return chatService.query(request);
    }
}
