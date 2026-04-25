package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.TradeCategory;
import com.tskhra.modulith.trade_module.model.requests.TradeCategoryCreateDto;
import com.tskhra.modulith.trade_module.model.responses.TradeCategorySummaryDto;
import com.tskhra.modulith.trade_module.repositories.TradeCategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class TradeCategoryAdminService {

    private final TradeCategoryRepository tradeCategoryRepository;

    @Transactional
    public TradeCategorySummaryDto create(TradeCategoryCreateDto dto) {
        TradeCategory parent = null;
        if (dto.parentId() != null) {
            parent = tradeCategoryRepository.findById(dto.parentId())
                    .orElseThrow(() -> new HttpNotFoundException("Parent category not found"));
            if (parent.getParent() != null) {
                throw new HttpBadRequestException("Categories can only be nested 2 levels deep");
            }
        }

        TradeCategory category = TradeCategory.builder()
                .name(dto.name())
                .slug(dto.slug())
                .parent(parent)
                .build();

        TradeCategory saved = tradeCategoryRepository.save(category);
        return toDto(saved);
    }

    @Transactional(readOnly = true)
    public List<TradeCategorySummaryDto> findAllParents() {
        return tradeCategoryRepository.findAllParents().stream()
                .map(this::toDto)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<TradeCategorySummaryDto> findChildren(Integer parentId) {
        tradeCategoryRepository.findById(parentId)
                .orElseThrow(() -> new HttpNotFoundException("Category not found"));
        return tradeCategoryRepository.findChildIdsByParentId(parentId).stream()
                .map(id -> tradeCategoryRepository.findById(id).orElseThrow())
                .map(this::toDto)
                .toList();
    }

    @Transactional
    public void delete(Integer id) {
        TradeCategory category = tradeCategoryRepository.findById(id)
                .orElseThrow(() -> new HttpNotFoundException("Category not found"));
        tradeCategoryRepository.delete(category);
    }

    private TradeCategorySummaryDto toDto(TradeCategory c) {
        return new TradeCategorySummaryDto(
                c.getId(),
                c.getName(),
                c.getSlug(),
                c.getParent() != null ? c.getParent().getId() : null
        );
    }

}
