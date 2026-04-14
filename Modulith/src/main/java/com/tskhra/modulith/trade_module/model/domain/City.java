package com.tskhra.modulith.trade_module.model.domain;

import jakarta.persistence.*;
import lombok.Getter;

@Entity
@Table(name = "cities_swap")
@Getter
public class City {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String name;

}
