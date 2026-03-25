package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/users/me/favorites")
@RequiredArgsConstructor
public class UserBusinessFavoriteController {

    private final UserService userService;

    @PutMapping("/businesses/{id}")
    public ResponseEntity<Void> favoriteBusiness(@PathVariable("id") Long businessId,
                                                 @AuthenticationPrincipal Jwt jwt) {

        userService.favoriteBusiness(businessId, jwt);
        return ResponseEntity.noContent().build();
    }

    @DeleteMapping("/businesses/{id}")
    public ResponseEntity<Void> unfavoriteBusiness(@PathVariable("id") Long businessId,
                                                   @AuthenticationPrincipal Jwt jwt) {

        userService.unfavoriteBusiness(businessId, jwt);
        return ResponseEntity.noContent().build();
    }

}
