package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.ItemType;
import com.tskhra.modulith.trade_module.model.domain.TradeCategory;
import com.tskhra.modulith.trade_module.model.requests.ItemTypeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.ItemTypeSummaryDto;
import com.tskhra.modulith.trade_module.repositories.ItemTypeRepository;
import com.tskhra.modulith.trade_module.repositories.TradeCategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ItemTypeAdminService {

    private final ItemTypeRepository itemTypeRepository;
    private final TradeCategoryRepository tradeCategoryRepository;

    @Transactional
    public ItemTypeSummaryDto create(ItemTypeCreateDto dto) {
        TradeCategory category = tradeCategoryRepository.findById(dto.categoryId())
                .orElseThrow(() -> new HttpNotFoundException("Category not found"));

        ItemType itemType = ItemType.builder()
                .category(category)
                .name(dto.name())
                .slug(dto.slug())
                .build();

        ItemType saved = itemTypeRepository.save(itemType);
        return toDto(saved);
    }

    @Transactional(readOnly = true)
    public List<ItemTypeSummaryDto> findAllByCategoryId(Integer categoryId) {
        return itemTypeRepository.findAllByCategoryId(categoryId).stream()
                .map(this::toDto)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<ItemTypeSummaryDto> findAll() {
        return itemTypeRepository.findAll().stream()
                .map(this::toDto)
                .toList();
    }

    @Transactional
    public void delete(Integer id) {
        ItemType itemType = itemTypeRepository.findById(id)
                .orElseThrow(() -> new HttpNotFoundException("Item type not found"));
        itemTypeRepository.delete(itemType);
    }

    private ItemTypeSummaryDto toDto(ItemType it) {
        return new ItemTypeSummaryDto(
                it.getId(),
                it.getCategory().getId(),
                it.getCategory().getName(),
                it.getName(),
                it.getSlug()
        );
    }

}
