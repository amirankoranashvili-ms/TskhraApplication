package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.booking_module.model.domain.City;
import com.tskhra.modulith.booking_module.repositories.CategoryRepository;
import com.tskhra.modulith.booking_module.repositories.CityRepository;
import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.CategorySwap;
import com.tskhra.modulith.trade_module.model.domain.CitySwap;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.requests.ItemUploadDto;
import com.tskhra.modulith.trade_module.repositories.CategorySwapRepository;
import com.tskhra.modulith.trade_module.repositories.CitySwapRepository;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ItemService {

    private final ItemRepository itemRepository;
    private final CategorySwapRepository categoryRepository;
    private final CitySwapRepository cityRepository;
    private final UserService userService;

    @Transactional
    public UUID createItem(ItemUploadDto dto, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        CategorySwap categorySwap = categoryRepository.findById(dto.categoryId()).orElseThrow(
                () -> new HttpBadRequestException("No such category with id: " + dto.categoryId())
        );

        CitySwap city = cityRepository.findById(dto.cityId()).orElseThrow(
                () -> new HttpBadRequestException("No such city with id: " + dto.cityId())
        );

        List<CategorySwap> desiredCategories = categoryRepository.findAllById(dto.desiredCategories());
        if (desiredCategories.size() != dto.desiredCategories().size()) {
            throw new HttpNotFoundException("One or more desired categories not found");
        }

        Item item = Item.builder()
                .name(dto.title())
                .ownerId(userId)
                .description(dto.description())
                .category(categorySwap)
                .city(city)
                .desiredCategories(desiredCategories)
                .condition(dto.condition())
                .tradeRange(dto.tradeRange())
                .status(ItemStatus.AVAILABLE)
                .build();

        Item save = itemRepository.save(item);
        return save.getId();
    }
}
