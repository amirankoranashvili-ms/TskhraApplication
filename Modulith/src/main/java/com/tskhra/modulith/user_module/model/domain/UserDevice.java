package com.tskhra.modulith.user_module.model.domain;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "user_devices")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Setter
public class UserDevice {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String userId;

    private String deviceId;

    @Column(columnDefinition = "TEXT")
    private String pinPublicKey;

    @Column(columnDefinition = "TEXT")
    private String biometricPublicKey;

    @CreationTimestamp
    private LocalDateTime createdAt;

}
