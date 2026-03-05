package com.tskhra.modulith.common.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.modulith.NamedInterface;

@NamedInterface
@ConfigurationProperties(prefix = "minio")
public record MinioProperties(
        String url,
        String externalUrl,
        String accessKey,
        String secretKey,
        String bucketName,
        String avatarFolder,
        String businessFolder
) {
}
