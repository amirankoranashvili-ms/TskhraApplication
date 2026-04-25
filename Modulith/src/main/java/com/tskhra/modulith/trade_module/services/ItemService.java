package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.trade_module.elastic.services.ItemSearchService;
import com.tskhra.modulith.trade_module.model.domain.*;
import com.tskhra.modulith.trade_module.model.enums.ItemCondition;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.requests.ItemUploadDto;
import com.tskhra.modulith.trade_module.repositories.*;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.tskhra.modulith.trade_module.model.responses.ItemSummaryDto;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;

@Service
@RequiredArgsConstructor
public class ItemService {

    private final ItemRepository itemRepository;
    private final ItemSearchService itemSearchService;
    private final ItemImageService itemImageService;
    private final CategorySwapRepository categoryRepository;
    private final CitySwapRepository cityRepository;
    private final ItemTypeRepository itemTypeRepository;
    private final ItemDesiredTypeRepository itemDesiredTypeRepository;
    private final SpecificationValidationService specValidationService;
    private final UserService userService;
    private final ImageService imageService;

    @Transactional
    public UUID createItem(ItemUploadDto dto, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        CategorySwap categorySwap = categoryRepository.findById(dto.categoryId()).orElseThrow(
                () -> new HttpBadRequestException("No such category with id: " + dto.categoryId())
        );

        CitySwap city = cityRepository.findById(dto.cityId()).orElseThrow(
                () -> new HttpBadRequestException("No such city with id: " + dto.cityId())
        );

        List<CategorySwap> desiredCategories = List.of();
        if (dto.desiredCategories() != null && !dto.desiredCategories().isEmpty()) {
            desiredCategories = categoryRepository.findAllById(dto.desiredCategories());
            if (desiredCategories.size() != dto.desiredCategories().size()) {
                throw new HttpNotFoundException("One or more desired categories not found");
            }
        }

        ItemType itemType = null;
        Map<String, Object> specifications = null;

        if (dto.itemTypeId() != null) {
            itemType = itemTypeRepository.findById(dto.itemTypeId()).orElseThrow(
                    () -> new HttpBadRequestException("No such item type with id: " + dto.itemTypeId())
            );

            if (dto.specifications() != null && !dto.specifications().isEmpty()) {
                specValidationService.validate(dto.itemTypeId(), dto.specifications());
                specifications = dto.specifications();
            }
        }

        Item item = Item.builder()
                .name(dto.title())
                .ownerId(userId)
                .description(dto.description())
                .category(categorySwap)
                .city(city)
                .desiredCategories(desiredCategories)
                .itemType(itemType)
                .specifications(specifications)
                .condition(dto.condition())
                .tradeRange(dto.tradeRange())
                .estimatedValue(mockEstimatedValue(dto.condition()))
                .valueVarianceRatio(mockVarianceRatio(dto.condition()))
                .status(ItemStatus.AVAILABLE)
                .build();

        Item saved = itemRepository.save(item);

        if (dto.desiredTypes() != null && !dto.desiredTypes().isEmpty()) {
            for (ItemUploadDto.DesiredTypeEntry dt : dto.desiredTypes()) {
                ItemType desiredItemType = itemTypeRepository.findById(dt.itemTypeId()).orElseThrow(
                        () -> new HttpBadRequestException("No such item type with id: " + dt.itemTypeId())
                );
                if (dt.desiredSpecs() != null && !dt.desiredSpecs().isEmpty()) {
                    specValidationService.validateDesiredSpecs(dt.itemTypeId(), dt.desiredSpecs());
                }
                ItemDesiredType idt = ItemDesiredType.builder()
                        .item(saved)
                        .itemType(desiredItemType)
                        .desiredSpecs(dt.desiredSpecs())
                        .build();
                itemDesiredTypeRepository.save(idt);
            }
        }

        itemSearchService.indexItem(saved);
        return saved.getId();
    }

    @Transactional
    public void removeItem(UUID itemId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Item item = itemRepository.findById(itemId).orElseThrow(
                () -> new HttpNotFoundException("Item not found")
        );

        if (!item.getOwnerId().equals(userId)) {
            throw new HttpBadRequestException("You are not authorized to perform this action");
        }

        item.setStatus(ItemStatus.REMOVED);
        itemRepository.save(item);
        itemSearchService.deleteFromIndex(itemId);
    }

    @Transactional(readOnly = true)
    public ItemSummaryDto getItem(UUID itemId) {
        Item item = itemRepository.findById(itemId).orElseThrow(
                () -> new HttpNotFoundException("Item not found")
        );

        if (item.getStatus() == ItemStatus.REMOVED) {
            throw new HttpNotFoundException("Item not found");
        }

        return toSummaryDto(item);
    }

    @Transactional
    public void hideItem(UUID itemId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Item item = itemRepository.findById(itemId).orElseThrow(
                () -> new HttpNotFoundException("Item not found")
        );

        if (!item.getOwnerId().equals(userId)) {
            throw new HttpBadRequestException("You are not authorized to perform this action");
        }

        if (item.getStatus() != ItemStatus.AVAILABLE) {
            throw new HttpBadRequestException("Only available items can be hidden");
        }

        item.setStatus(ItemStatus.HIDDEN);
        itemRepository.save(item);
        itemSearchService.updateItemStatus(itemId, ItemStatus.HIDDEN);
    }

    @Transactional
    public void unhideItem(UUID itemId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Item item = itemRepository.findById(itemId).orElseThrow(
                () -> new HttpNotFoundException("Item not found")
        );

        if (!item.getOwnerId().equals(userId)) {
            throw new HttpBadRequestException("You are not authorized to perform this action");
        }

        if (item.getStatus() != ItemStatus.HIDDEN) {
            throw new HttpBadRequestException("Only hidden items can be unhidden");
        }

        item.setStatus(ItemStatus.AVAILABLE);
        itemRepository.save(item);
        itemSearchService.updateItemStatus(itemId, ItemStatus.AVAILABLE);
    }

    @Transactional(readOnly = true)
    public Page<ItemSummaryDto> getAllAvailableItems(Pageable pageable) {
        return itemRepository.findAllByStatus(ItemStatus.AVAILABLE, pageable)
                .map(this::toSummaryDto);
    }

    @Transactional(readOnly = true)
    public Page<ItemSummaryDto> getAvailableItemsByUser(Long userId, Pageable pageable) {
        return itemRepository.findAllByOwnerIdAndStatus(userId, ItemStatus.AVAILABLE, pageable)
                .map(this::toSummaryDto);
    }

    @Transactional(readOnly = true)
    public Page<ItemSummaryDto> getCurrentUserItems(Jwt jwt, Pageable pageable) {
        Long userId = userService.getCurrentUser(jwt).getId();
        return itemRepository.findAllByOwnerIdAndStatuses(userId, List.of(ItemStatus.AVAILABLE, ItemStatus.HIDDEN), pageable)
                .map(this::toSummaryDto);
    }

    private BigDecimal mockEstimatedValue(ItemCondition condition) {
        double base = switch (condition) {
            case NEW -> 200.0;
            case LIKE_NEW -> 150.0;
            case USED -> 80.0;
            case DAMAGED -> 30.0;
        };
        double randomFactor = 0.7 + ThreadLocalRandom.current().nextDouble() * 0.6; // 0.7 - 1.3
        return BigDecimal.valueOf(base * randomFactor).setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal mockVarianceRatio(ItemCondition condition) {
        double base = switch (condition) {
            case NEW -> 0.05;
            case LIKE_NEW -> 0.10;
            case USED -> 0.20;
            case DAMAGED -> 0.35;
        };
        double jitter = ThreadLocalRandom.current().nextDouble() * 0.05; // 0 - 0.05
        return BigDecimal.valueOf(base + jitter).setScale(2, RoundingMode.HALF_UP);
    }

    private ItemSummaryDto toSummaryDto(Item item) {
        List<ItemSummaryDto.DesiredTypeSummary> desiredTypeSummaries = null;
        if (item.getItemType() != null) {
            List<ItemDesiredType> desiredTypes = itemDesiredTypeRepository.findAllByItemId(item.getId());
            desiredTypeSummaries = desiredTypes.stream()
                    .map(dt -> new ItemSummaryDto.DesiredTypeSummary(
                            dt.getItemType().getId(),
                            dt.getItemType().getName(),
                            dt.getDesiredSpecs()
                    )).toList();
        }

        return new ItemSummaryDto(
                item.getId(),
                item.getOwnerId(),
                item.getName(),
                item.getDescription(),
                item.getCategory() != null ? item.getCategory().getName() : null,
                item.getCity() != null ? item.getCity().getName() : null,
                item.getCondition(),
                item.getTradeRange(),
                item.getEstimatedValue(),
                item.getCreatedAt(),
                item.getImages().stream()
                        .map(ItemImage::getUri)
                        .map(imageService::getItemImageUrl)
                        .toList(),
                item.getStatus(),
                false,
                item.getItemType() != null ? item.getItemType().getId() : null,
                item.getItemType() != null ? item.getItemType().getName() : null,
                item.getSpecifications(),
                desiredTypeSummaries
        );
    }

}
