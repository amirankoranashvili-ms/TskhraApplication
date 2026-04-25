package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.trade_module.model.domain.ItemTypeAttribute;
import com.tskhra.modulith.trade_module.model.enums.AttributeDataType;
import com.tskhra.modulith.trade_module.repositories.BrandRepository;
import com.tskhra.modulith.trade_module.repositories.ItemTypeAttributeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class SpecificationValidationService {

    private final ItemTypeAttributeRepository itemTypeAttributeRepository;
    private final BrandRepository brandRepository;

    public void validate(Integer itemTypeId, Map<String, Object> specifications) {
        if (specifications == null || specifications.isEmpty()) return;

        List<ItemTypeAttribute> schema = itemTypeAttributeRepository.findAllByItemTypeId(itemTypeId);
        Map<String, ItemTypeAttribute> schemaByKey = schema.stream()
                .collect(Collectors.toMap(
                        ita -> ita.getAttribute().getKey(),
                        Function.identity()
                ));

        List<String> errors = new ArrayList<>();

        for (Map.Entry<String, Object> entry : specifications.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();

            ItemTypeAttribute attr = schemaByKey.get(key);
            if (attr == null) {
                errors.add("Unknown attribute: " + key);
                continue;
            }

            validateValue(key, value, attr, errors);
        }

        for (ItemTypeAttribute attr : schema) {
            if (attr.isRequired() && !specifications.containsKey(attr.getAttribute().getKey())) {
                errors.add("Missing required attribute: " + attr.getAttribute().getKey());
            }
        }

        if (!errors.isEmpty()) {
            throw new HttpBadRequestException("Specification validation failed: " + String.join("; ", errors));
        }
    }

    public void validateDesiredSpecs(Integer itemTypeId, Map<String, Object> desiredSpecs) {
        if (desiredSpecs == null || desiredSpecs.isEmpty()) return;

        List<ItemTypeAttribute> schema = itemTypeAttributeRepository.findAllByItemTypeId(itemTypeId);
        Map<String, ItemTypeAttribute> schemaByKey = schema.stream()
                .collect(Collectors.toMap(
                        ita -> ita.getAttribute().getKey(),
                        Function.identity()
                ));

        List<String> errors = new ArrayList<>();

        for (Map.Entry<String, Object> entry : desiredSpecs.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();

            ItemTypeAttribute attr = schemaByKey.get(key);
            if (attr == null) {
                errors.add("Unknown attribute: " + key);
                continue;
            }

            String lookup = getLookup(attr);
            if (lookup != null) {
                validateLookupDesiredValue(key, value, lookup, errors);
            }
        }

        if (!errors.isEmpty()) {
            throw new HttpBadRequestException("Desired specs validation failed: " + String.join("; ", errors));
        }
    }

    private void validateValue(String key, Object value, ItemTypeAttribute attr, List<String> errors) {
        AttributeDataType dataType = attr.getAttribute().getDataType();
        Map<String, Object> constraints = attr.getConstraints();

        String lookup = getLookup(attr);
        if (lookup != null) {
            if (!(value instanceof String strVal)) {
                errors.add(key + ": expected string");
                return;
            }
            if (!existsInLookup(lookup, strVal)) {
                errors.add(key + ": '" + strVal + "' not found in " + lookup);
            }
            return;
        }

        switch (dataType) {
            case STRING -> {
                if (!(value instanceof String)) {
                    errors.add(key + ": expected string");
                }
            }
            case NUMBER -> {
                if (!(value instanceof Number)) {
                    errors.add(key + ": expected number");
                    return;
                }
                if (constraints != null) {
                    double numVal = ((Number) value).doubleValue();
                    if (constraints.containsKey("min")) {
                        double min = ((Number) constraints.get("min")).doubleValue();
                        if (numVal < min) errors.add(key + ": must be >= " + min);
                    }
                    if (constraints.containsKey("max")) {
                        double max = ((Number) constraints.get("max")).doubleValue();
                        if (numVal > max) errors.add(key + ": must be <= " + max);
                    }
                }
            }
            case BOOLEAN -> {
                if (!(value instanceof Boolean)) {
                    errors.add(key + ": expected boolean");
                }
            }
            case ENUM -> {
                if (!(value instanceof String)) {
                    errors.add(key + ": expected string (enum value)");
                    return;
                }
                if (constraints != null && constraints.containsKey("options")) {
                    @SuppressWarnings("unchecked")
                    List<String> options = (List<String>) constraints.get("options");
                    if (!options.contains(value)) {
                        errors.add(key + ": must be one of " + options);
                    }
                }
            }
        }
    }

    private void validateLookupDesiredValue(String key, Object value, String lookup, List<String> errors) {
        if (value instanceof String strVal) {
            if (!existsInLookup(lookup, strVal)) {
                errors.add(key + ": '" + strVal + "' not found in " + lookup);
            }
        } else if (value instanceof List<?> listVal) {
            for (Object item : listVal) {
                if (!(item instanceof String strItem)) {
                    errors.add(key + ": expected string values in list");
                    return;
                }
                if (!existsInLookup(lookup, strItem)) {
                    errors.add(key + ": '" + strItem + "' not found in " + lookup);
                }
            }
        }
    }

    private String getLookup(ItemTypeAttribute attr) {
        Map<String, Object> constraints = attr.getConstraints();
        if (constraints != null && constraints.containsKey("lookup")) {
            return (String) constraints.get("lookup");
        }
        return null;
    }

    private boolean existsInLookup(String lookup, String value) {
        if ("brands".equals(lookup)) {
            return brandRepository.existsByNameIgnoreCase(value);
        }
        return true;
    }

}
