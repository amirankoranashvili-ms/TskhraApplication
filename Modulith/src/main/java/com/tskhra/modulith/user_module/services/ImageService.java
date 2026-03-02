package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.properties.MinioProperties;
import io.minio.*;
import io.minio.errors.*;
import io.minio.http.Method;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class ImageService {

    private final MinioClient minioClient;
    private final MinioProperties minioProperties;

    @PostConstruct
    public void init() throws Exception {
        String bucketName = minioProperties.bucketName();
        boolean found = minioClient.bucketExists(BucketExistsArgs.builder().bucket(bucketName).build());
        if (!found) {
            minioClient.makeBucket(MakeBucketArgs.builder().bucket(bucketName).build());
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
            minioClient.putObject(
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
        if (fileName == null || fileName.isEmpty()) {
            return null;
        }

        try {
            return minioClient.getPresignedObjectUrl(
                    GetPresignedObjectUrlArgs.builder()
                            .method(Method.GET)
                            .bucket(minioProperties.bucketName())
                            .object(fileName)
                            .build()
            );
        } catch (Exception e) {
            return null;
        }
    }


}
