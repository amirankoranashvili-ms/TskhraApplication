package com.tskhra.modulith.common.logging;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.MDC;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

public class MdcFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        try {
            String requestId = request.getHeader("X-Request-Id");
            if (requestId == null || requestId.isBlank()) {
                requestId = UUID.randomUUID().toString().substring(0, 8);
            }
            MDC.put("requestId", requestId);

            extractAndSetUserId();

            MDC.put("module", deriveModule(request.getRequestURI()));

            response.setHeader("X-Request-Id", requestId);

            filterChain.doFilter(request, response);
        } finally {
            MDC.clear();
        }
    }

    private void extractAndSetUserId() {
        try {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            if (auth instanceof JwtAuthenticationToken jwtAuth) {
                String sub = jwtAuth.getToken().getClaimAsString("sub");
                if (sub != null) {
                    MDC.put("userId", sub);
                }
            }
        } catch (Exception ignored) {
        }
    }

    private String deriveModule(String uri) {
        if (uri.startsWith("/users") || uri.startsWith("/user-profile")
                || uri.startsWith("/auth") || uri.startsWith("/kyc")
                || uri.startsWith("/credentials")) {
            return "user";
        }
        if (uri.startsWith("/bookings") || uri.startsWith("/business")
                || uri.startsWith("/services") || uri.startsWith("/categories")
                || uri.startsWith("/cities") || uri.startsWith("/chatbot")
                || uri.startsWith("/chat")) {
            return "booking";
        }
        if (uri.startsWith("/notifications")) {
            return "notification";
        }
        if (uri.startsWith("/ws") || uri.startsWith("/app")) {
            return "messaging";
        }
        if (uri.startsWith("/trade") || uri.startsWith("/items")
                || uri.startsWith("/chain") || uri.startsWith("/brands")
                || uri.startsWith("/admin")) {
            return "trade";
        }
        return "common";
    }
}
