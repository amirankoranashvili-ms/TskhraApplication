package com.tskhra.modulith;

import com.tskhra.modulith.common.properties.KeycloakProperties;
import com.tskhra.modulith.common.properties.MinioProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties({KeycloakProperties.class, MinioProperties.class})
public class ModulithApplication {

    public static void main(String[] args) {
        SpringApplication.run(ModulithApplication.class, args);
    }

}
