package com.tskhra.modulith.booking_module.model.embeddable;

import com.tskhra.modulith.booking_module.model.enums.WeekDay;
import com.tskhra.modulith.booking_module.validation.ValidTimeInterval;
import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@ToString
@Embeddable
@ValidTimeInterval
public class WeekTimeInterval {

    @NotNull
    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "week_day", columnDefinition = "week_day")
    private WeekDay weekDay;

    @Min(0)
    @Max(1440)
    private int startTime;

    @Min(0)
    @Max(1440)
    private int endTime;

}
