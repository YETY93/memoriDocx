package com.memoridocx.repository;

import com.memoridocx.entity.ProcessingLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ProcessingLogRepository extends JpaRepository<ProcessingLog, Long> {

    List<ProcessingLog> findByDocumentIdOrderByIdAsc(Long documentId);

    List<ProcessingLog> findAllByOrderByIdDesc();
}
