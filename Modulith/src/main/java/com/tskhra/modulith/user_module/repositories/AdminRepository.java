package com.tskhra.modulith.user_module.repositories;

import com.tskhra.modulith.user_module.model.domain.Admin;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AdminRepository extends JpaRepository<Admin, Long> {
}
