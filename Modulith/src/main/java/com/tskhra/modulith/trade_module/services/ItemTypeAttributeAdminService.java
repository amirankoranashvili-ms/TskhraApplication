package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.Attribute;
import com.tskhra.modulith.trade_module.model.domain.ItemType;
import com.tskhra.modulith.trade_module.model.domain.ItemTypeAttribute;
import com.tskhra.modulith.trade_module.model.requests.ItemTypeAttributeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.ItemTypeAttributeSummaryDto;
import com.tskhra.modulith.trade_module.repositories.AttributeRepository;
import com.tskhra.modulith.trade_module.repositories.ItemTypeAttributeRepository;
import com.tskhra.modulith.trade_module.repositories.ItemTypeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ItemTypeAttributeAdminService {

    private final ItemTypeAttributeRepository itemTypeAttributeRepository;
    private final ItemTypeRepository itemTypeRepository;
    private final AttributeRepository attributeRepository;

    @Transactional
    public ItemTypeAttributeSummaryDto create(ItemTypeAttributeCreateDto dto) {
        ItemType itemType = itemTypeRepository.findById(dto.itemTypeId())
                .orElseThrow(() -> new HttpNotFoundException("Item type not found"));

        Attribute attribute = attributeRepository.findById(dto.attributeId())
                .orElseThrow(() -> new HttpNotFoundException("Attribute not found"));

        ItemTypeAttribute ita = ItemTypeAttribute.builder()
                .itemType(itemType)
                .attribute(attribute)
                .required(dto.required())
                .filterable(dto.filterable())
                .constraints(dto.constraints())
                .build();

        ItemTypeAttribute saved = itemTypeAttributeRepository.save(ita);
        return toDto(saved);
    }

    @Transactional(readOnly = true)
    public List<ItemTypeAttributeSummaryDto> findAllByItemTypeId(Integer itemTypeId) {
        return itemTypeAttributeRepository.findAllByItemTypeId(itemTypeId).stream()
                .map(this::toDto)
                .toList();
    }

    @Transactional
    public void delete(Integer id) {
        ItemTypeAttribute ita = itemTypeAttributeRepository.findById(id)
                .orElseThrow(() -> new HttpNotFoundException("Item type attribute not found"));
        itemTypeAttributeRepository.delete(ita);
    }

    private ItemTypeAttributeSummaryDto toDto(ItemTypeAttribute ita) {
        Attribute attr = ita.getAttribute();
        return new ItemTypeAttributeSummaryDto(
                ita.getId(),
                attr.getId(),
                attr.getName(),
                attr.getKey(),
                attr.getDataType(),
                attr.getUnit(),
                ita.isRequired(),
                ita.isFilterable(),
                ita.getConstraints()
        );
    }

}
