package com.tskhra.modulith.booking_module.model.domain;

import com.tskhra.modulith.booking_module.model.embeddable.ModificationDetails;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.util.Set;

@Entity
@Table(name = "services")
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
public class Service {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "business_id", nullable = false)
    private Business business;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "activity_status", columnDefinition = "activity_status")
    private ActivityStatus activityStatus;

    @Column(nullable = false)
    private String name;

//    @Column(nullable = false) todo uncomment on DB reset
    private String nameKa;

    private int capacity;

    private String description;

    private String descriptionKa;

    @Column(nullable = false)
    private BigDecimal sessionPrice;

    @Column(nullable = false)
    private int sessionDuration;

    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE}, fetch = FetchType.LAZY)
    @JoinTable(
            name = "service_resources",
            joinColumns = @JoinColumn(name = "service_id"),
            inverseJoinColumns = @JoinColumn(name = "resource_id")
    )
    private Set<Resource> resources;

    @Embedded
    private ModificationDetails modificationDetails;

}
