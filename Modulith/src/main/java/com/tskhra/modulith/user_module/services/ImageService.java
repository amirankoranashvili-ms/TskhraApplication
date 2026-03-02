package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.properties.MinioProperties;
import io.minio.*;
import io.minio.http.Method;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.UUID;

@Service
public class ImageService {

    private final MinioClient minioInternalClient;
    private final MinioClient minioExternalClient;
    private final MinioProperties minioProperties;

    public ImageService(@Qualifier("minioInternalClient") MinioClient minioInternalClient,
                        @Qualifier("minioExternalClient") MinioClient minioExternalClient,
                        MinioProperties minioProperties) {

        this.minioInternalClient = minioInternalClient;
        this.minioExternalClient = minioExternalClient;
        this.minioProperties = minioProperties;
    }

    @PostConstruct
    public void init() throws Exception {
        String bucketName = minioProperties.bucketName();
        boolean found = minioInternalClient.bucketExists(BucketExistsArgs.builder().bucket(bucketName).build());
        if (!found) {
            minioInternalClient.makeBucket(MakeBucketArgs.builder().bucket(bucketName).build());
        }
    }

    public String uploadAvatar(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Cannot upload an empty file.");
        }

        String bucketName = minioProperties.bucketName();
        String originalFilename = file.getOriginalFilename();

        String extension = StringUtils.getFilenameExtension(originalFilename);
        String fileName = UUID.randomUUID() + (extension == null ? "" : "." + extension);

        try (InputStream inputStream = file.getInputStream()) {
            minioInternalClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucketName)
                            .object(fileName)
                            .stream(inputStream, file.getSize(), -1)
                            .contentType(file.getContentType())
                            .build()
            );
            return fileName;

        } catch (Exception e) {
            throw new RuntimeException("Failed to upload file: " + originalFilename, e);
        }
    }

    public String getAvatarUrl(String fileName) {
        if (fileName == null || fileName.isEmpty()) return null;

        try {
            return minioExternalClient.getPresignedObjectUrl(
                    GetPresignedObjectUrlArgs.builder()
                            .method(Method.GET)
                            .bucket(minioProperties.bucketName())
                            .region("us-east-1")
                            .object(fileName)
                            .build()
            );
        } catch (Exception e) {
            return null;
        }
    }


}
