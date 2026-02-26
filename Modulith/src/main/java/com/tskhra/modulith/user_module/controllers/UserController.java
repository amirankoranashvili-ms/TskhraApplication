package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.requests.UserRegistrationRequestDto;
import com.tskhra.modulith.user_module.services.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/register")
    public ResponseEntity<Void> registerUser(@Valid @RequestBody UserRegistrationRequestDto dto) {

        userService.registerUser(dto);
        return new ResponseEntity<>(HttpStatus.CREATED);
    }

    @GetMapping("/sanity-check")
    public ResponseEntity<String> sanityCheck() {
        return ResponseEntity.ok("Sanity check passed!");
    }

}
