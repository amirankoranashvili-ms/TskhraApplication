package com.tskhra.modulith.user_module.repositories;

import com.tskhra.modulith.user_module.model.domain.UserDevice;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserDevicesRepository extends JpaRepository<UserDevice, Long> {
    boolean existsUserDeviceByDeviceId(String deviceId);

    Optional<UserDevice> findByDeviceId(String deviceId);
}
