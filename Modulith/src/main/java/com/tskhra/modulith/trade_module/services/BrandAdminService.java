package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.Brand;
import com.tskhra.modulith.trade_module.model.requests.BrandCreateDto;
import com.tskhra.modulith.trade_module.model.responses.BrandSummaryDto;
import com.tskhra.modulith.trade_module.repositories.BrandRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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
