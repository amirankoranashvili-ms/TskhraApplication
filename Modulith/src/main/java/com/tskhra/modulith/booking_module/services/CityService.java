package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.City;
import com.tskhra.modulith.booking_module.model.enums.Lang;
import com.tskhra.modulith.booking_module.model.responses.CityDto;
import com.tskhra.modulith.booking_module.repositories.CityRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CityService {

    private final CityRepository cityRepository;

    public List<CityDto> getAllCities(Lang lang) {
        return cityRepository.findAll().stream()
                .map(city -> mapToDto(city, lang))
                .toList();
    }

    private CityDto mapToDto(City city, Lang lang) {
        String name = switch (lang) {
            case EN -> city.getName();
            case KA -> city.getNameKa();
        };
        return new CityDto(city.getId(), name);
    }


}
