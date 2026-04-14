package com.tskhra.modulith.common.services;

import com.tskhra.modulith.common.properties.MinioProperties;
import io.minio.*;
import io.minio.http.Method;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.modulith.NamedInterface;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.UUID;

@Service
@NamedInterface
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
        String folderPrefix = minioProperties.avatarFolder();
        String originalFilename = file.getOriginalFilename();

        String extension = StringUtils.getFilenameExtension(originalFilename);
        String fileName = UUID.randomUUID() + (extension == null ? "" : "." + extension);

        try (InputStream inputStream = file.getInputStream()) {
            minioInternalClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucketName)
                            .object(folderPrefix + fileName)
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

        String objectKey = minioProperties.avatarFolder() + fileName;

        try {
            return minioExternalClient.getPresignedObjectUrl(
                    GetPresignedObjectUrlArgs.builder()
                            .method(Method.GET)
                            .bucket(minioProperties.bucketName())
                            .region("us-east-1")
                            .object(objectKey)
                            .build()
            );
        } catch (Exception e) {
            return null;
        }
    }


    public String uploadBusinessImage(MultipartFile file) { // todo decompose
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Cannot upload an empty file.");
        }

        String bucketName = minioProperties.bucketName();
        String folderPrefix = minioProperties.businessFolder();
        String originalFilename = file.getOriginalFilename();

        String extension = StringUtils.getFilenameExtension(originalFilename);
        String fileName = UUID.randomUUID() + (extension == null ? "" : "." + extension);

        try (InputStream inputStream = file.getInputStream()) {
            minioInternalClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucketName)
                            .object(folderPrefix + fileName)
                            .stream(inputStream, file.getSize(), -1)
                            .contentType(file.getContentType())
                            .build()
            );
            return fileName;

        } catch (Exception e) {
            throw new RuntimeException("Failed to upload file: " + originalFilename, e);
        }
    }

    public void deleteBusinessImage(String fileName) {
        String objectKey = minioProperties.businessFolder() + fileName;
        try {
            minioInternalClient.removeObject(
                    RemoveObjectArgs.builder()
                            .bucket(minioProperties.bucketName())
                            .object(objectKey)
                            .build()
            );
        } catch (Exception e) {
            throw new RuntimeException("Failed to delete file: " + fileName, e);
        }
    }

    public String uploadItemImage(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Cannot upload an empty file.");
        }

        String bucketName = minioProperties.bucketName();
        String folderPrefix = minioProperties.itemFolder();
        String originalFilename = file.getOriginalFilename();

        String extension = StringUtils.getFilenameExtension(originalFilename);
        String fileName = UUID.randomUUID() + (extension == null ? "" : "." + extension);

        try (InputStream inputStream = file.getInputStream()) {
            minioInternalClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucketName)
                            .object(folderPrefix + fileName)
                            .stream(inputStream, file.getSize(), -1)
                            .contentType(file.getContentType())
                            .build()
            );
            return fileName;

        } catch (Exception e) {
            throw new RuntimeException("Failed to upload file: " + originalFilename, e);
        }
    }

    public void deleteItemImage(String fileName) {
        String objectKey = minioProperties.itemFolder() + fileName;
        try {
            minioInternalClient.removeObject(
                    RemoveObjectArgs.builder()
                            .bucket(minioProperties.bucketName())
                            .object(objectKey)
                            .build()
            );
        } catch (Exception e) {
            throw new RuntimeException("Failed to delete file: " + fileName, e);
        }
    }

    public String getBusinessImageUrl(String fileName) {
        if (fileName == null || fileName.isEmpty()) return null;

        String objectKey = minioProperties.businessFolder() + fileName;

        try {
            return minioExternalClient.getPresignedObjectUrl(
                    GetPresignedObjectUrlArgs.builder()
                            .method(Method.GET)
                            .bucket(minioProperties.bucketName())
                            .region("us-east-1")
                            .object(objectKey)
                            .build()
            );
        } catch (Exception e) {
            return null;
        }
    }




}
