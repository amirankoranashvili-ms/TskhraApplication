package com.tskhra.modulith.user_module.repositories;

import com.tskhra.modulith.user_module.model.domain.UserBiometricDevices;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserBiometricDevicesRepository extends JpaRepository<UserBiometricDevices, Long> {
}
