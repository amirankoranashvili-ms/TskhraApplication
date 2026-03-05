package com.tskhra.modulith.booking_module.model.domain;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "business_images")
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
public class BusinessImage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "business_id")
    private Business business;

    @Column(nullable = false, unique = true)
    private String filename;

    @Column(nullable = false)
    private Long uploadedBy;

    @CreationTimestamp
    private LocalDateTime uploadedAt;

}
