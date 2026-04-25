package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.Attribute;
import com.tskhra.modulith.trade_module.model.requests.AttributeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.AttributeSummaryDto;
import com.tskhra.modulith.trade_module.repositories.AttributeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AttributeAdminService {

    private final AttributeRepository attributeRepository;

    @Transactional
    public AttributeSummaryDto create(AttributeCreateDto dto) {
        Attribute attribute = Attribute.builder()
                .name(dto.name())
                .key(dto.key())
                .dataType(dto.dataType())
                .unit(dto.unit())
                .build();

        Attribute saved = attributeRepository.save(attribute);
        return toDto(saved);
    }

    @Transactional(readOnly = true)
    public List<AttributeSummaryDto> findAll() {
        return attributeRepository.findAll().stream()
                .map(this::toDto)
                .toList();
    }

    @Transactional
    public void delete(Integer id) {
        Attribute attribute = attributeRepository.findById(id)
                .orElseThrow(() -> new HttpNotFoundException("Attribute not found"));
        attributeRepository.delete(attribute);
    }

    private AttributeSummaryDto toDto(Attribute a) {
        return new AttributeSummaryDto(
                a.getId(),
                a.getName(),
                a.getKey(),
                a.getDataType(),
                a.getUnit()
        );
    }

}
