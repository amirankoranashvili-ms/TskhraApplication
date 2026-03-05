package com.tskhra.modulith.common.config;

import com.tskhra.modulith.common.properties.MinioProperties;
import io.minio.MinioClient;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@RequiredArgsConstructor
public class MinioConfiguration {

    private final MinioProperties minioProperties;

    @Bean(name = "minioInternalClient")
    public MinioClient minioInternalClient() {
        return MinioClient.builder()
                .endpoint(minioProperties.url())
                .credentials(minioProperties.accessKey(), minioProperties.secretKey())
                .build();
    }

    @Bean(name = "minioExternalClient")
    public MinioClient minioExternalClient() {
        return MinioClient.builder()
                .endpoint(minioProperties.externalUrl())
                .credentials(minioProperties.accessKey(), minioProperties.secretKey())
                .build();
    }

}
