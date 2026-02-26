package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.requests.UserRegistrationRequestDto;
import com.tskhra.modulith.user_module.model.responses.GenericResponse;
import com.tskhra.modulith.user_module.services.UserService;
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
    public ResponseEntity<GenericResponse> registerUser(@RequestBody UserRegistrationRequestDto dto) {

        String id = userService.registerUser(dto);

        return ResponseEntity.status(HttpStatus.CREATED).body(
                new GenericResponse(
                        HttpStatus.CREATED,
                        "User Registered Successfully",
                        LocalDateTime.now(),
                        id
                ));
    }

    @GetMapping("/sanity-check")
    public ResponseEntity<String> sanityCheck() {
        return ResponseEntity.ok("Sanity check passed!");
    }

}
