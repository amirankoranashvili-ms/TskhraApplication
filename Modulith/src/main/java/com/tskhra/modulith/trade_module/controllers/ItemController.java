package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.ItemUploadDto;
import com.tskhra.modulith.trade_module.model.responses.ImageUploadedDto;
import com.tskhra.modulith.trade_module.model.responses.ItemCreatedDto;
import com.tskhra.modulith.trade_module.model.responses.ItemSummaryDto;
import com.tskhra.modulith.trade_module.services.ItemImageService;
import com.tskhra.modulith.trade_module.services.ItemService;
import com.tskhra.modulith.trade_module.validation.ImageFile;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;

@RestController
@Validated
@RequestMapping("/items")
@RequiredArgsConstructor
public class ItemController {

    private final ItemService itemService;
    private final ItemImageService itemImageService;

    @PostMapping
    public ResponseEntity<ItemCreatedDto> uploadItem(@Valid @RequestBody ItemUploadDto dto,
                                                     @AuthenticationPrincipal Jwt jwt) {
        UUID id = itemService.createItem(dto, jwt);
        return new ResponseEntity<>(new ItemCreatedDto(id.toString()), HttpStatus.CREATED);
    }

    @PostMapping(value = "/{itemId}/images", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ImageUploadedDto> uploadItemImage(@AuthenticationPrincipal Jwt jwt,
                                                            @PathVariable UUID itemId,
                                                            @RequestParam(defaultValue = "false") boolean isMain,
                                                            @ImageFile @RequestParam("file") MultipartFile file) {
        Long id = itemImageService.uploadImage(file, itemId, isMain, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new ImageUploadedDto(id));
    }

    @DeleteMapping("/items/{itemId}")
    public ResponseEntity<Void> deleteVoid(@PathVariable UUID itemId,
                                           @AuthenticationPrincipal Jwt jwt) {

        itemService.removeItem(itemId, jwt);
        return ResponseEntity.noContent().build();
    }

    @DeleteMapping("/{itemId}/images/{imageId}")
    public ResponseEntity<Void> deleteItemImage(@PathVariable UUID itemId,
                                                @PathVariable Long imageId,
                                                @AuthenticationPrincipal Jwt jwt) {
        itemImageService.deleteImage(itemId, imageId, jwt);
        return ResponseEntity.noContent().build();
    }

    @GetMapping
    public ResponseEntity<Page<ItemSummaryDto>> getAllItems(Pageable pageable) {
        return ResponseEntity.ok(itemService.getAllAvailableItems(pageable));
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<Page<ItemSummaryDto>> getItemsByUser(@PathVariable Long userId,
                                                               Pageable pageable) {
        return ResponseEntity.ok(itemService.getAvailableItemsByUser(userId, pageable));
    }

    @GetMapping("/me")
    public ResponseEntity<Page<ItemSummaryDto>> getCurrentUserItems(@AuthenticationPrincipal Jwt jwt,
                                                                    Pageable pageable) {
        return ResponseEntity.ok(itemService.getCurrentUserItems(jwt, pageable));
    }

}
