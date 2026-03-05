package com.tskhra.modulith.booking_module.model.embeddable;

import com.tskhra.modulith.booking_module.model.enums.WeekDay;
import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@ToString
@Embeddable
public class WeekTimeInterval {

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "week_day", columnDefinition = "week_day")
    private WeekDay weekDay;
    private int startTime;
    private int endTime;

}
