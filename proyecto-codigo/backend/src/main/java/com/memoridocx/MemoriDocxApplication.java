package com.memoridocx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class MemoriDocxApplication {

    public static void main(String[] args) {
        SpringApplication.run(MemoriDocxApplication.class, args);
    }
}
