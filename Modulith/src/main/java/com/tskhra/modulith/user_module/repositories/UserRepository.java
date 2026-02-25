package com.tskhra.modulith.user_module.repositories;

import com.tskhra.modulith.user_module.model.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
}
