package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.enums.Lang;
import com.tskhra.modulith.booking_module.model.responses.CityDto;
import com.tskhra.modulith.booking_module.services.CityService;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/cities")
@RequiredArgsConstructor
public class CityController {

    private final CityService cityService;

    @Operation(summary = "List all available cities")
    @GetMapping
    public ResponseEntity<List<CityDto>> getAll(@RequestParam(defaultValue = "EN") Lang lang) {
        List<CityDto> cities = cityService.getAllCities(lang);
        return ResponseEntity.status(HttpStatus.OK).body(cities);
    }

}
