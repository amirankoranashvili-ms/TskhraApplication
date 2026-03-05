package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.City;
import com.tskhra.modulith.booking_module.repositories.CityRepository;
import com.tskhra.modulith.common.exception.HttpNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CityService {

    private final CityRepository cityRepository;

    public List<String> getAllCityNames() {
        return cityRepository.findAll().stream()
                .map(City::getName)
                .toList();
    }
}
