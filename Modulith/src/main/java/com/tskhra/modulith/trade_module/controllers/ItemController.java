package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.ItemUploadDto;
import com.tskhra.modulith.trade_module.model.responses.ItemCreatedDto;
import com.tskhra.modulith.trade_module.services.ItemImageService;
import com.tskhra.modulith.trade_module.services.ItemService;
import com.tskhra.modulith.trade_module.validation.ImageFile;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
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
    public ResponseEntity<Long> uploadItemImage(@AuthenticationPrincipal Jwt jwt,
                                                @PathVariable UUID itemId,
                                                @RequestParam(defaultValue = "false") boolean isMain,
                                                @ImageFile @RequestParam("file") MultipartFile file) {
        Long id = itemImageService.uploadImage(file, itemId, isMain, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(id);
    }

    @DeleteMapping("/{itemId}/images/{imageId}")
    public ResponseEntity<Void> deleteItemImage(@PathVariable UUID itemId,
                                                @PathVariable Long imageId,
                                                @AuthenticationPrincipal Jwt jwt) {
        itemImageService.deleteImage(itemId, imageId, jwt);
        return ResponseEntity.noContent().build();
    }

}
