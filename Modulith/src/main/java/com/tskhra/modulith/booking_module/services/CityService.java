package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.City;
import com.tskhra.modulith.booking_module.model.enums.Lang;
import com.tskhra.modulith.booking_module.repositories.CityRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CityService {

    private final CityRepository cityRepository;

    public List<String> getAllCityNames(Lang lang) {
        return switch (lang) {
            case EN -> cityRepository.findAll().stream()
                    .map(City::getName)
                    .toList();
            case KA -> cityRepository.findAll().stream()
                    .map(City::getNameKa)
                    .toList();
        };
    }
}
