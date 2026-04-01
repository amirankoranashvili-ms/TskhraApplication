package com.tskhra.modulith.messaging_module.controllers;

import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

import java.text.SimpleDateFormat;
import java.util.Date;

@Slf4j
@Controller
public class GreetingController {

    @MessageMapping("/greeting")
    @SendTo("/topic/greetings")
    public String handle(String greeting) {
        log.info("Received message: {}", greeting);
        return "[" + getTimestamp() + "] : " + greeting;
    }

    private String getTimestamp() {
        return new SimpleDateFormat("dd/MM/yyyy hh:mm:ss a").format(new Date());
    }

}
