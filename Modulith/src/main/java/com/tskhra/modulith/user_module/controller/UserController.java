package com.tskhra.modulith.user_module.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/users")
public class UserController {

    @GetMapping("/sanity-check")
    public ResponseEntity<String> sanityCheck() {
        return ResponseEntity.ok("Sanity check passed!");
    }

}
