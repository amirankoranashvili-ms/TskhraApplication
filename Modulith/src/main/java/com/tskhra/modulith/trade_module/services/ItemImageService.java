package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpForbiddenError;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.domain.ItemImage;
import com.tskhra.modulith.trade_module.repositories.ItemImageRepository;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import com.tskhra.modulith.user_module.services.UserService;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ItemImageService {

    private final ItemRepository itemRepository;
    private final ItemImageRepository itemImageRepository;
    private final ImageService imageService;
    private final UserService userService;

    @Transactional
    public Long uploadImage(MultipartFile file, UUID itemId, boolean isMain, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Item item = itemRepository.findById(itemId)
                .orElseThrow(() -> new HttpNotFoundException("Item not found"));

        if (!item.getOwnerId().equals(userId)) {
            throw new HttpForbiddenError("You are not authorized to perform this action");
        }

        String filename = imageService.uploadItemImage(file);

        ItemImage image = new ItemImage();
        image.setItem(item);
        image.setUri(filename);
        image.setMain(isMain);

        ItemImage saved = itemImageRepository.save(image);
        return saved.getId();
    }

    @Transactional
    public void deleteImage(UUID itemId, Long imageId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Item item = itemRepository.findById(itemId)
                .orElseThrow(() -> new HttpNotFoundException("Item not found"));

        if (!item.getOwnerId().equals(userId)) {
            throw new HttpForbiddenError("You are not authorized to perform this action");
        }

        ItemImage image = itemImageRepository.findById(imageId)
                .orElseThrow(() -> new HttpNotFoundException("Image not found"));

        item.getImages().remove(image);
        imageService.deleteItemImage(image.getUri());
    }
}