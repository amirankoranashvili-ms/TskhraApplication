package com.tskhra.modulith.booking_module.model.enums;

import java.time.DayOfWeek;

public enum WeekDay {
    MON,
    TUE,
    WED,
    THU,
    FRI,
    SAT,
    SUN;

    public static WeekDay from(DayOfWeek dayOfWeek) {
        return values()[dayOfWeek.ordinal()];
    }
}
