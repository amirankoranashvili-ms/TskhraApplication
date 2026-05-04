package com.tskhra.modulith.common.logging;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

@Aspect
@Component
@Slf4j
public class ServiceLoggingAspect {

    private static final long SLOW_THRESHOLD_MS = 500;

    @Around("within(@org.springframework.stereotype.Service *) && within(com.tskhra.modulith..*)")
    public Object logServiceMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        String className = joinPoint.getSignature().getDeclaringType().getSimpleName();
        String methodName = joinPoint.getSignature().getName();

        log.debug("==> {}.{}()", className, methodName);
        long start = System.currentTimeMillis();

        try {
            Object result = joinPoint.proceed();
            long duration = System.currentTimeMillis() - start;

            if (duration > SLOW_THRESHOLD_MS) {
                log.warn("<== {}.{}() completed in {}ms (SLOW)", className, methodName, duration);
            } else {
                log.debug("<== {}.{}() completed in {}ms", className, methodName, duration);
            }
            return result;
        } catch (Throwable ex) {
            long duration = System.currentTimeMillis() - start;
            log.debug("<== {}.{}() failed in {}ms with {}", className, methodName,
                    duration, ex.getClass().getSimpleName());
            throw ex;
        }
    }
}
