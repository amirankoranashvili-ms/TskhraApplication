package com.tskhra.modulith.booking_module.model.domain;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "business_chatbot")
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
public class BusinessChatbot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "business_id", nullable = false, unique = true)
    private Business business;

    @Column(name = "ai_provider_id", nullable = false)
    private String aiProviderId;

    @Column(name = "chat_api_key", nullable = false)
    private String chatApiKey;

    @Column(name = "admin_api_key") // todo add nullable
    private String adminApiKey;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
}
