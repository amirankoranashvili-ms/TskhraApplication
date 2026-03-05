package com.tskhra.modulith.booking_module.model.domain;

import com.tskhra.modulith.booking_module.model.embeddable.WeekTimeInterval;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "business_schedules")
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class BusinessSchedule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "business_id", nullable = false)
    private Business business;

    @Embedded
    private WeekTimeInterval interval;

}
