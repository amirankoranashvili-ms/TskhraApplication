package com.tskhra.modulith.user_module.model.requests;

public record LoginRequestDto( // todo  should i add validation?
        String username,
        String password
) {
}
