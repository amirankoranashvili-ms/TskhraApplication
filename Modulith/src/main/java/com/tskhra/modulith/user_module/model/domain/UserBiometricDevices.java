package com.tskhra.modulith.user_module.model.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "user_biometric_devices")
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserBiometricDevices {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String userId;

    private String deviceId;

    private String publicKey;

    @CreationTimestamp
    private LocalDateTime createdAt;

}
