package com.tskhra.modulith.booking_module.model.domain;

import com.tskhra.modulith.booking_module.model.embeddable.ModificationDetails;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import com.tskhra.modulith.booking_module.model.enums.BusinessType;
import com.tskhra.modulith.booking_module.model.enums.CallType;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "businesses")
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
public class Business {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long userId;

    @Column(nullable = false)
    private String name;

    private String description;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private Category category;

    @Column(nullable = false)
    private String phoneNumber;

    private String instagramUrl;

    private String facebookUrl;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "address_id")
    private Address address;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "business_type", columnDefinition = "business_type", nullable = false)
    private BusinessType businessType;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "activity_status", columnDefinition = "activity_status", nullable = false)
    private ActivityStatus activityStatus;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "call_type", columnDefinition = "call_type")
    private CallType callType;

    @OneToMany(mappedBy = "business", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<BusinessSchedule> businessSchedules = new ArrayList<>();

    @OneToMany(mappedBy = "business", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<BusinessUnavailableSchedule> businessUnavailableSchedules = new ArrayList<>();

    @OneToMany(mappedBy = "business", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<BusinessUnavailableOnetime> businessUnavailableOnetimes = new ArrayList<>();

    @OneToMany(mappedBy = "business", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<BusinessImage> businessImages = new ArrayList<>();

    @OneToMany(mappedBy = "business", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Service> services = new ArrayList<>();

    @OneToMany(mappedBy = "business", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Resource> resources = new ArrayList<>();

    @Embedded
    private ModificationDetails modificationDetails;

//    helpers

    public void addService(Service service) {
        this.services.add(service);
        service.setBusiness(this);
    }

    public void removeService(Service service) {
        this.services.remove(service);
        service.setBusiness(null);
    }

    public void addResource(Resource resource) {
        this.resources.add(resource);
        resource.setBusiness(this);
    }

    public void removeResource(Resource resource) {
        this.resources.remove(resource);
        resource.setBusiness(null);
    }

    public void addBusinessSchedule(BusinessSchedule businessSchedule) {
        this.businessSchedules.add(businessSchedule);
        businessSchedule.setBusiness(this);
    }

    public void removeBusinessSchedule(BusinessSchedule businessSchedule) {
        this.businessSchedules.remove(businessSchedule);
        businessSchedule.setBusiness(null);
    }

    public void addBusinessUnavailableSchedule(BusinessUnavailableSchedule businessUnavailableSchedule) {
        this.businessUnavailableSchedules.add(businessUnavailableSchedule);
        businessUnavailableSchedule.setBusiness(this);
    }

    public void removeBusinessUnavailableSchedule(BusinessUnavailableSchedule businessUnavailableSchedule) {
        this.businessUnavailableSchedules.remove(businessUnavailableSchedule);
        businessUnavailableSchedule.setBusiness(null);
    }

    public void addBusinessUnavailableOnetime(BusinessUnavailableOnetime businessUnavailableOnetime) {
        this.businessUnavailableOnetimes.add(businessUnavailableOnetime);
        businessUnavailableOnetime.setBusiness(this);
    }

    public void removeBusinessUnavailableOnetime(BusinessUnavailableOnetime businessUnavailableOnetime) {
        this.businessUnavailableOnetimes.remove(businessUnavailableOnetime);
        businessUnavailableOnetime.setBusiness(null);
    }

    public void addBusinessImage(BusinessImage businessImage) {
        this.businessImages.add(businessImage);
        businessImage.setBusiness(this);
    }

    public void removeBusinessImage(BusinessImage businessImage) {
        this.businessImages.remove(businessImage);
        businessImage.setBusiness(null);
    }

}
