package com.tskhra.modulith.booking_module.model.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;

@Entity
@Table(name = "business_unavailable_onetimes")
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class BusinessUnavailableOnetime {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "business_id", nullable = false)
    private Business business;

    @Column(nullable = false)
    private LocalDate date;

    @Column(nullable = false)
    private int startTime;

    @Column(nullable = false)
    private int endTime;

}
