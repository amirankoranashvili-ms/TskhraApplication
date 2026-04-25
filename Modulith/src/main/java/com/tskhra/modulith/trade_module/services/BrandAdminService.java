package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.Brand;
import com.tskhra.modulith.trade_module.model.requests.BrandCreateDto;
import com.tskhra.modulith.trade_module.model.responses.BrandSummaryDto;
import com.tskhra.modulith.trade_module.model.responses.BulkImportResult;
import com.tskhra.modulith.trade_module.repositories.BrandRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class BrandAdminService {

    private final BrandRepository brandRepository;

    @Transactional
    public BrandSummaryDto create(BrandCreateDto dto) {
        Brand brand = Brand.builder()
                .name(dto.name())
                .slug(dto.slug())
                .build();

        Brand saved = brandRepository.save(brand);
        return toDto(saved);
    }

    @Transactional(readOnly = true)
    public List<BrandSummaryDto> findAll() {
        return brandRepository.findAll().stream()
                .map(this::toDto)
                .toList();
    }

    @Transactional(readOnly = true)
    public Page<BrandSummaryDto> findAll(Pageable pageable) {
        return brandRepository.findAll(pageable).map(this::toDto);
    }

    @Transactional
    public BulkImportResult bulkCreate(List<BrandCreateDto> dtos) {
        int created = 0, skipped = 0, failed = 0;
        List<String> errors = new ArrayList<>();

        for (BrandCreateDto dto : dtos) {
            if (brandRepository.existsBySlug(dto.slug())) { skipped++; continue; }
            Brand brand = Brand.builder().name(dto.name()).slug(dto.slug()).build();
            brandRepository.save(brand);
            created++;
        }

        return new BulkImportResult(created, skipped, failed, errors);
    }

    @Transactional(readOnly = true)
    public List<BrandCreateDto> exportAll() {
        return brandRepository.findAll().stream()
                .map(b -> new BrandCreateDto(b.getName(), b.getSlug()))
                .toList();
    }

    @Transactional
    public void delete(Integer id) {
        Brand brand = brandRepository.findById(id)
                .orElseThrow(() -> new HttpNotFoundException("Brand not found"));
        brandRepository.delete(brand);
    }

    private BrandSummaryDto toDto(Brand b) {
        return new BrandSummaryDto(b.getId(), b.getName(), b.getSlug());
    }

}
