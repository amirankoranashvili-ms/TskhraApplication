package com.tskhra.modulith;

import com.tskhra.modulith.common.properties.KeycloakProperties;
import com.tskhra.modulith.common.properties.MinioProperties;
import com.tskhra.modulith.common.properties.SumsubProperties;
import jakarta.annotation.PostConstruct;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.scheduling.annotation.EnableAsync;

import java.util.TimeZone;

@SpringBootApplication
@EnableAsync
@EnableConfigurationProperties({KeycloakProperties.class, MinioProperties.class, SumsubProperties.class})
public class ModulithApplication {

    @PostConstruct
    public void init() {
        TimeZone.setDefault(TimeZone.getTimeZone("Asia/Tbilisi"));
    }

    public static void main(String[] args) {
        SpringApplication.run(ModulithApplication.class, args);
    }

}
