package com.memoridocx.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "ai_providers")
public class AiProvider {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String code;

    @Column(name = "display_name")
    private String displayName;

    @Column(name = "model_id")
    private String modelId;

    @Column(name = "base_url")
    private String baseUrl;

    private Boolean enabled = true;

    private Boolean active = false;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    public String getDisplayName() { return displayName; }
    public void setDisplayName(String displayName) { this.displayName = displayName; }
    public String getModelId() { return modelId; }
    public void setModelId(String modelId) { this.modelId = modelId; }
    public String getBaseUrl() { return baseUrl; }
    public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }
    public Boolean getEnabled() { return enabled; }
    public void setEnabled(Boolean enabled) { this.enabled = enabled; }
    public Boolean getActive() { return active; }
    public void setActive(Boolean active) { this.active = active; }
}
