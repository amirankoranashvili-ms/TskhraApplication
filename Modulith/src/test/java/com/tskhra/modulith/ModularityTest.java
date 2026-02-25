package com.tskhra.modulith;

import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModules;
import org.springframework.modulith.docs.Documenter;

public class ModularityTest {

    @Test
    public void applicationModules() {
        ApplicationModules modules = ApplicationModules.of(ModulithApplication.class);
        modules.forEach(System.out::println);
        modules.verify();

    }

    @Test
    void createDocumentation(){
        ApplicationModules modules = ApplicationModules.of(ModulithApplication.class);
        new Documenter(modules).writeDocumentation();
    }

}
