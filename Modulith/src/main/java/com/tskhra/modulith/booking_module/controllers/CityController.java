package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.services.CityService;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/cities")
@RequiredArgsConstructor
public class CityController {

    private final CityService cityService;

    @Operation(summary = "List all available cities")
    @GetMapping
    public ResponseEntity<List<String>> getAll() {
        List<String> cities = cityService.getAllCityNames();
        return ResponseEntity.status(HttpStatus.OK).body(cities);
    }

}
