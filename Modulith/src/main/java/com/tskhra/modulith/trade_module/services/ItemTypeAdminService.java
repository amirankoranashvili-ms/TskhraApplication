package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.ItemType;
import com.tskhra.modulith.trade_module.model.domain.TradeCategory;
import com.tskhra.modulith.trade_module.model.requests.ItemTypeBulkDto;
import com.tskhra.modulith.trade_module.model.requests.ItemTypeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.BulkImportResult;
import com.tskhra.modulith.trade_module.model.responses.ItemTypeSummaryDto;
import com.tskhra.modulith.trade_module.repositories.ItemTypeRepository;
import com.tskhra.modulith.trade_module.repositories.TradeCategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
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

    @Transactional(readOnly = true)
    public Page<ItemTypeSummaryDto> findAll(Pageable pageable) {
        return itemTypeRepository.findAll(pageable).map(this::toDto);
    }

    @Transactional
    public BulkImportResult bulkCreate(List<ItemTypeBulkDto> dtos) {
        int created = 0, skipped = 0, failed = 0;
        List<String> errors = new ArrayList<>();

        for (ItemTypeBulkDto dto : dtos) {
            if (itemTypeRepository.existsBySlug(dto.slug())) { skipped++; continue; }
            var category = tradeCategoryRepository.findBySlug(dto.categorySlug());
            if (category.isEmpty()) { failed++; errors.add("Category not found: " + dto.categorySlug()); continue; }
            ItemType it = ItemType.builder().category(category.get()).name(dto.name()).slug(dto.slug()).build();
            itemTypeRepository.save(it);
            created++;
        }

        return new BulkImportResult(created, skipped, failed, errors);
    }

    @Transactional(readOnly = true)
    public List<ItemTypeBulkDto> exportAll() {
        return itemTypeRepository.findAll().stream()
                .map(it -> new ItemTypeBulkDto(it.getCategory().getSlug(), it.getName(), it.getSlug()))
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
