package com.memoridocx.repository;

import com.memoridocx.entity.AiProvider;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface AiProviderRepository extends JpaRepository<AiProvider, Long> {

    Optional<AiProvider> findByCode(String code);

    List<AiProvider> findAllByOrderByIdAsc();
}
