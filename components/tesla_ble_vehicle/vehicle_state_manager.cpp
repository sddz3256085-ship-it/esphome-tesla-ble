#include "vehicle_state_manager.h"
#include "tesla_ble_vehicle.h"
#include <esphome/core/helpers.h>
#include <cmath>
#include <algorithm>

namespace esphome {
namespace tesla_ble_vehicle {

VehicleStateManager::VehicleStateManager(TeslaBLEVehicle* parent)
    : parent_(parent) {}

void VehicleStateManager::set_binary_sensor(const std::string& id, binary_sensor::BinarySensor* sensor) {
    if (sensor == nullptr) {
        return;
    }
    binary_sensors_[id] = sensor;
}

void VehicleStateManager::set_sensor(const std::string& id, sensor::Sensor* sensor) {
    if (sensor == nullptr) {
        return;
    }
    sensors_[id] = sensor;
}

void VehicleStateManager::set_text_sensor(const std::string& id, text_sensor::TextSensor* sensor) {
    if (sensor == nullptr) {
        return;
    }
    text_sensors_[id] = sensor;
}

binary_sensor::BinarySensor* VehicleStateManager::get_binary_sensor(const std::string& id) {
    auto it = binary_sensors_.find(id);
    return (it != binary_sensors_.end()) ? it->second : nullptr;
}

sensor::Sensor* VehicleStateManager::get_sensor(const std::string& id) {
    auto it = sensors_.find(id);
    return (it != sensors_.end()) ? it->second : nullptr;
}

text_sensor::TextSensor* VehicleStateManager::get_text_sensor(const std::string& id) {
    auto it = text_sensors_.find(id);
    return (it != text_sensors_.end()) ? it->second : nullptr;
}

const binary_sensor::BinarySensor* VehicleStateManager::get_binary_sensor(const std::string& id) const {
    auto it = binary_sensors_.find(id);
    return (it != binary_sensors_.end()) ? it->second : nullptr;
}

const sensor::Sensor* VehicleStateManager::get_sensor(const std::string& id) const {
    auto it = sensors_.find(id);
    return (it != sensors_.end()) ? it->second : nullptr;
}

const text_sensor::TextSensor* VehicleStateManager::get_text_sensor(const std::string& id) const {
    auto it = text_sensors_.find(id);
    return (it != text_sensors_.end()) ? it->second : nullptr;
}

bool VehicleStateManager::publish_binary_sensor(const std::string& id, bool state) {
    auto* sensor = get_binary_sensor(id);
    return sensor != nullptr && publish_sensor_state(sensor, state);
}

bool VehicleStateManager::publish_sensor(const std::string& id, float state) {
    auto* sensor = get_sensor(id);
    return sensor != nullptr && publish_sensor_state(sensor, state);
}

bool VehicleStateManager::publish_text_sensor(const std::string& id, const std::string& state) {
    auto* sensor = get_text_sensor(id);
    return sensor != nullptr && publish_sensor_state(sensor, state);
}

void VehicleStateManager::update_vehicle_status(const VCSEC_VehicleStatus& status) {
    
    update_sleep_status(status.vehicleSleepStatus);
    update_lock_status(status.vehicleLockState);
    update_user_presence(status.userPresence);
    
    if (status.has_closureStatuses) {
        bool flap_open = (status.closureStatuses.chargePort == VCSEC_ClosureState_E_CLOSURESTATE_OPEN);
        update_charge_flap_open(flap_open);
    }
}

void VehicleStateManager::update_sleep_status(VCSEC_VehicleSleepStatus_E status) {
    auto asleep = convert_sleep_status(status);
    if (asleep.has_value()) {
        update_asleep(asleep.value());
    } else {
        set_sensor_available(get_binary_sensor("asleep"), false);
    }
}

void VehicleStateManager::update_lock_status(VCSEC_VehicleLockState_E status) {
    auto unlocked = convert_lock_status(status);
    if (unlocked.has_value()) {
        update_unlocked(unlocked.value());
    }
}

void VehicleStateManager::update_user_presence(VCSEC_UserPresence_E presence) {
    auto present = convert_user_presence(presence);
    if (present.has_value()) {
        update_user_present(present.value());
    } else {
        set_sensor_available(get_binary_sensor("user_present"), false);
    }
}

void VehicleStateManager::update_charge_state(const CarServer_ChargeState& charge_state) {
    
    if (charge_state.has_charging_state) {
        const bool was_charging = is_charging_;
        const bool new_charging_state = (
            charge_state.charging_state.which_type == CarServer_ChargeState_ChargingState_Charging_tag ||
            charge_state.charging_state.which_type == CarServer_ChargeState_ChargingState_Starting_tag
        );
        
        
        is_charging_ = new_charging_state;
        
        if (charging_switch_ && (!charging_switch_->has_state() || charging_switch_->state != is_charging_)) {
            publish_sensor_state(charging_switch_, is_charging_);
        }
        
        publish_text_sensor("charging_state", get_charging_state_text(charge_state.charging_state));
        publish_text_sensor("iec61851_state", get_iec61851_state_text(charge_state.charging_state));
        
        const bool charger_connected = is_charger_connected_from_state(charge_state.charging_state);
        publish_binary_sensor("charger", charger_connected);
    }
    
    if (charge_state.which_optional_battery_level) {
        const float battery_level = static_cast<float>(charge_state.optional_battery_level.battery_level);
        if (battery_level >= 0.0f && battery_level <= 100.0f && std::isfinite(battery_level)) {
            if (publish_sensor("battery_level", battery_level)) {
                ESP_LOGI(STATE_MANAGER_TAG, "Updating battery level to %.1f%%", battery_level);
            }
        }
    }
    
    if (charge_state.which_optional_charger_power) {
        const float power_kw = static_cast<float>(charge_state.optional_charger_power.charger_power);
        if (power_kw >= 0.0f && power_kw <= 500.0f && std::isfinite(power_kw)) {
            publish_sensor("charger_power", power_kw);
        }
    }
    
    if (charge_state.which_optional_battery_range) {
        const float range = charge_state.optional_battery_range.battery_range;
        if (range >= 0.0f && range <= 500.0f && std::isfinite(range)) {
            publish_sensor("range", range);
        }
    }
    
    // range_rated_api: CarServer_ChargeState 中不存在此字段，已删除
    
    if (charge_state.which_optional_charge_energy_added) {
        const float energy = charge_state.optional_charge_energy_added.charge_energy_added;
        if (energy >= 0.0f && std::isfinite(energy)) {
            publish_sensor("charge_energy_added", energy);
        }
    }
    
    if (charge_state.which_optional_minutes_to_full_charge) {
        const float minutes = static_cast<float>(charge_state.optional_minutes_to_full_charge.minutes_to_full_charge);
        if (minutes >= 0.0f && std::isfinite(minutes)) {
            publish_sensor("time_to_full_charge", minutes);
        }
    }
    
    if (charge_state.which_optional_charger_voltage) {
        const float voltage = static_cast<float>(charge_state.optional_charger_voltage.charger_voltage);
        if (voltage >= 0.0f && voltage <= 600.0f && std::isfinite(voltage)) {
            publish_sensor("charger_voltage", voltage);
        }
    }
    
    if (charge_state.which_optional_charger_actual_current) {
        const float current = static_cast<float>(charge_state.optional_charger_actual_current.charger_actual_current);
        if (current >= 0.0f && current <= 100.0f && std::isfinite(current)) {
            publish_sensor("charger_current", current);
        }
    }
    
    if (charge_state.which_optional_charge_rate_mph) {
        const float rate_mph = static_cast<float>(charge_state.optional_charge_rate_mph.charge_rate_mph);
        publish_sensor("charging_rate", rate_mph);
        // "charge_rate" (km/h) migrated from PedroKTFC/esphome-tesla-ble: the proto only
        // exposes the rate in mph, so convert it the same way "speed" is converted below.
        publish_sensor("charge_rate", rate_mph * 1.60934f);
    }

    // --- Migrated from PedroKTFC/esphome-tesla-ble: max_soc / max_amps / charge_distance_added / charger_phases ---
    if (charge_state.which_optional_charge_limit_soc) {
        const float limit = static_cast<float>(charge_state.optional_charge_limit_soc.charge_limit_soc);
        publish_sensor("max_soc", limit);
    }

    if (charge_state.which_optional_charging_amps) {
        const float amps = static_cast<float>(charge_state.optional_charging_amps.charging_amps);
        publish_sensor("max_amps", amps);
    }

    if (charge_state.which_optional_charge_miles_added_ideal) {
        const float miles_added = static_cast<float>(charge_state.optional_charge_miles_added_ideal.charge_miles_added_ideal);
        if (std::isfinite(miles_added)) {
            publish_sensor("charge_distance_added", miles_added);
        }
    }

    if (charge_state.which_optional_charger_phases) {
        const float phases = static_cast<float>(charge_state.optional_charger_phases.charger_phases);
        publish_sensor("charger_phases", phases);
    }

    if (charge_state.which_optional_charger_actual_current && charging_amps_number_) {
        const float amps = static_cast<float>(charge_state.optional_charger_actual_current.charger_actual_current);
        update_charging_amps(amps);
    }
    
    if (charge_state.which_optional_charge_limit_soc && charging_limit_number_) {
        const float limit = static_cast<float>(charge_state.optional_charge_limit_soc.charge_limit_soc);
        publish_sensor_state(charging_limit_number_, limit);
    }
    
    if (charge_state.which_optional_charge_current_request_max) {
        int32_t new_max = charge_state.optional_charge_current_request_max.charge_current_request_max;
        if (new_max > 0 && new_max != charging_amps_max_) {
            ESP_LOGI(STATE_MANAGER_TAG, "Received new max charging amps: %ld A", static_cast<long>(new_max));
            update_charging_amps_max(new_max);
        }
    }
    
    if (charge_state.which_optional_charge_port_door_open) {
        const bool door_open = charge_state.optional_charge_port_door_open.charge_port_door_open;
        if (charge_port_door_cover_ != nullptr) {
            charge_port_door_cover_->position = door_open ? cover::COVER_OPEN : cover::COVER_CLOSED;
            charge_port_door_cover_->publish_state();
        }
    }
    
    if (charge_state.has_charge_port_latch) {
        const bool latch_engaged = (charge_state.charge_port_latch.which_type == CarServer_ChargePortLatchState_Engaged_tag);
        const bool latch_disengaged = (charge_state.charge_port_latch.which_type == CarServer_ChargePortLatchState_Disengaged_tag);
        if (charge_port_latch_lock_ != nullptr && (latch_engaged || latch_disengaged)) {
            auto new_state = latch_engaged ? lock::LOCK_STATE_LOCKED : lock::LOCK_STATE_UNLOCKED;
            if (charge_port_latch_lock_->state != new_state) {
                charge_port_latch_lock_->publish_state(new_state);
            }
        }
        // Migrated from PedroKTFC/esphome-tesla-ble: "charge_port_latch_state" text sensor
        // (SNA / Disengaged / Engaged / Blocking) alongside the existing lock entity above.
        publish_text_sensor("charge_port_latch_state",
                             get_charge_port_latch_state_text(charge_state.charge_port_latch.which_type));
    }
}

void VehicleStateManager::update_climate_state(const CarServer_ClimateState& climate_state) {
    
    if (climate_state.which_optional_inside_temp_celsius) {
        const float temp = climate_state.optional_inside_temp_celsius.inside_temp_celsius;
        if (temp >= -40.0f && temp <= 60.0f && std::isfinite(temp)) {
            current_inside_temp_ = temp;
            publish_sensor("inside_temp", temp);
        }
    }
    
    if (climate_state.which_optional_outside_temp_celsius) {
        const float temp = climate_state.optional_outside_temp_celsius.outside_temp_celsius;
        if (temp >= -50.0f && temp <= 60.0f && std::isfinite(temp)) {
            publish_sensor("outside_temp", temp);
        }
    }
    
    if (climate_state.which_optional_driver_temp_setting) {
        const float temp = climate_state.optional_driver_temp_setting.driver_temp_setting;
        if (temp >= 15.0f && temp <= 30.0f && std::isfinite(temp)) {
            target_temp_ = temp;
            publish_sensor("driver_temp_setting", temp);
        }
    }
    if (climate_state.which_optional_passenger_temp_setting) {
        const float temp = climate_state.optional_passenger_temp_setting.passenger_temp_setting;
        if (temp >= 15.0f && temp <= 30.0f && std::isfinite(temp)) {
            publish_sensor("passenger_temp_setting", temp);
        }
    }
    
    if (climate_state.which_optional_is_climate_on) {
        climate_on_ = climate_state.optional_is_climate_on.is_climate_on;
        // Migrated from PedroKTFC/esphome-tesla-ble: expose "is_climate_on" as its own
        // binary sensor in addition to the TeslaClimate entity which already reflects it.
        publish_binary_sensor("climate_on", climate_on_);
    }

    // Migrated from PedroKTFC/esphome-tesla-ble: "defrost_state" text sensor (Off / Normal / Max).
    if (climate_state.has_defrost_mode) {
        publish_text_sensor("defrost_state", get_defrost_state_text(climate_state.defrost_mode.which_type));
    }
    
    if (climate_state.which_optional_steering_wheel_heater && steering_wheel_heat_switch_ != nullptr) {
        const bool heater_on = climate_state.optional_steering_wheel_heater.steering_wheel_heater;
        if (!steering_wheel_heat_switch_->has_state() || steering_wheel_heat_switch_->state != heater_on) {
            publish_sensor_state(steering_wheel_heat_switch_, heater_on);
        }
    }
    
    if (auto* tesla_climate = static_cast<TeslaClimate*>(climate_)) {
        tesla_climate->update_state(climate_on_, current_inside_temp_, target_temp_);
    }
}

void VehicleStateManager::update_drive_state(const CarServer_DriveState& drive_state) {
    
    if (drive_state.has_shift_state) {
        publish_text_sensor("shift_state", get_shift_state_text(drive_state.shift_state));
        
        const bool parked = (drive_state.shift_state.which_type == CarServer_ShiftState_P_tag);
        publish_binary_sensor("parking_brake", parked);
    }
    
    if (drive_state.which_optional_speed) {
        const float speed_mph = static_cast<float>(drive_state.optional_speed.speed);
        const float speed_kmh = speed_mph * 1.60934f;
        if (speed_kmh >= 0.0f && speed_kmh <= 300.0f && std::isfinite(speed_kmh)) {
            publish_sensor("speed", speed_kmh);
        }
    }
    
    if (drive_state.which_optional_odometer_in_hundredths_of_a_mile) {
        const float odometer = static_cast<float>(drive_state.optional_odometer_in_hundredths_of_a_mile.odometer_in_hundredths_of_a_mile) / 100.0f;
        if (odometer >= 0.0f && std::isfinite(odometer)) {
            publish_sensor("odometer", odometer);
        }
    }
}

void VehicleStateManager::update_tire_pressure_state(const CarServer_TirePressureState& tire_pressure_state) {
    
    if (tire_pressure_state.which_optional_tpms_pressure_fl) {
        const float pressure = tire_pressure_state.optional_tpms_pressure_fl.tpms_pressure_fl;
        if (pressure >= 0.0f && pressure <= 5.0f && std::isfinite(pressure)) {
            publish_sensor("tpms_front_left", pressure);
        }
    }
    
    if (tire_pressure_state.which_optional_tpms_pressure_fr) {
        const float pressure = tire_pressure_state.optional_tpms_pressure_fr.tpms_pressure_fr;
        if (pressure >= 0.0f && pressure <= 5.0f && std::isfinite(pressure)) {
            publish_sensor("tpms_front_right", pressure);
        }
    }
    
    if (tire_pressure_state.which_optional_tpms_pressure_rl) {
        const float pressure = tire_pressure_state.optional_tpms_pressure_rl.tpms_pressure_rl;
        if (pressure >= 0.0f && pressure <= 5.0f && std::isfinite(pressure)) {
            publish_sensor("tpms_rear_left", pressure);
        }
    }
    
    if (tire_pressure_state.which_optional_tpms_pressure_rr) {
        const float pressure = tire_pressure_state.optional_tpms_pressure_rr.tpms_pressure_rr;
        if (pressure >= 0.0f && pressure <= 5.0f && std::isfinite(pressure)) {
            publish_sensor("tpms_rear_right", pressure);
        }
    }
}

void VehicleStateManager::update_closures_state(const CarServer_ClosuresState& closures_state) {
    
    if (closures_state.which_optional_door_open_driver_front) {
        publish_binary_sensor("door_driver_front", closures_state.optional_door_open_driver_front.door_open_driver_front);
    }
    if (closures_state.which_optional_door_open_driver_rear) {
        publish_binary_sensor("door_driver_rear", closures_state.optional_door_open_driver_rear.door_open_driver_rear);
    }
    if (closures_state.which_optional_door_open_passenger_front) {
        publish_binary_sensor("door_passenger_front", closures_state.optional_door_open_passenger_front.door_open_passenger_front);
    }
    if (closures_state.which_optional_door_open_passenger_rear) {
        publish_binary_sensor("door_passenger_rear", closures_state.optional_door_open_passenger_rear.door_open_passenger_rear);
    }
    
    if (closures_state.which_optional_door_open_trunk_front) {
        const bool frunk_open = closures_state.optional_door_open_trunk_front.door_open_trunk_front;
        if (frunk_cover_ != nullptr) {
            frunk_cover_->position = frunk_open ? cover::COVER_OPEN : cover::COVER_CLOSED;
            frunk_cover_->publish_state();
        }
        // Migrated from PedroKTFC/esphome-tesla-ble: "is_frunk_open" binary sensor,
        // in addition to the frunk Cover entity above.
        publish_binary_sensor("frunk_open", frunk_open);
    }
    if (closures_state.which_optional_door_open_trunk_rear) {
        const bool trunk_open = closures_state.optional_door_open_trunk_rear.door_open_trunk_rear;
        if (trunk_cover_ != nullptr) {
            trunk_cover_->position = trunk_open ? cover::COVER_OPEN : cover::COVER_CLOSED;
            trunk_cover_->publish_state();
        }
        // Migrated from PedroKTFC/esphome-tesla-ble: "is_boot_open" binary sensor,
        // in addition to the trunk Cover entity above.
        publish_binary_sensor("boot_open", trunk_open);
    }
    
    bool window_df = false, window_dr = false, window_pf = false, window_pr = false;
    if (closures_state.which_optional_window_open_driver_front) {
        window_df = closures_state.optional_window_open_driver_front.window_open_driver_front;
        publish_binary_sensor("window_driver_front", window_df);
    }
    if (closures_state.which_optional_window_open_driver_rear) {
        window_dr = closures_state.optional_window_open_driver_rear.window_open_driver_rear;
        publish_binary_sensor("window_driver_rear", window_dr);
    }
    if (closures_state.which_optional_window_open_passenger_front) {
        window_pf = closures_state.optional_window_open_passenger_front.window_open_passenger_front;
        publish_binary_sensor("window_passenger_front", window_pf);
    }
    if (closures_state.which_optional_window_open_passenger_rear) {
        window_pr = closures_state.optional_window_open_passenger_rear.window_open_passenger_rear;
        publish_binary_sensor("window_passenger_rear", window_pr);
    }
    const bool any_window_open = window_df || window_dr || window_pf || window_pr;
    
    if (windows_cover_ != nullptr) {
        windows_cover_->position = any_window_open ? cover::COVER_OPEN : cover::COVER_CLOSED;
        windows_cover_->publish_state();
    }
    // Migrated from PedroKTFC/esphome-tesla-ble: "windows_state" aggregate binary sensor,
    // in addition to the per-window binary sensors and the Windows Cover entity above.
    // BUGFIX: only publish when ALL FOUR window fields are present in the message
    // (Pedro's original logic). Publishing on partial data could report "all windows
    // closed" when the not-reported windows were actually open.
    if (closures_state.which_optional_window_open_driver_front &&
        closures_state.which_optional_window_open_driver_rear &&
        closures_state.which_optional_window_open_passenger_front &&
        closures_state.which_optional_window_open_passenger_rear) {
        publish_binary_sensor("windows_state", any_window_open);
    }
    
    if (closures_state.which_optional_sun_roof_percent_open) {
        const bool sunroof_open = closures_state.optional_sun_roof_percent_open.sun_roof_percent_open > 0;
        publish_binary_sensor("sunroof", sunroof_open);
    }
    
    if (closures_state.has_sentry_mode_state && sentry_mode_switch_ != nullptr) {
        const bool sentry_active = (closures_state.sentry_mode_state.which_type == CarServer_ClosuresState_SentryModeState_Armed_tag ||
                              closures_state.sentry_mode_state.which_type == CarServer_ClosuresState_SentryModeState_Aware_tag ||
                              closures_state.sentry_mode_state.which_type == CarServer_ClosuresState_SentryModeState_Panic_tag);
        if (!sentry_mode_switch_->has_state() || sentry_mode_switch_->state != sentry_active) {
            publish_sensor_state(sentry_mode_switch_, sentry_active);
        }
    }
    
    if (closures_state.which_optional_locked) {
        update_unlocked(!closures_state.optional_locked.locked);
    }
}

void VehicleStateManager::update_asleep(bool asleep) {
    if (publish_binary_sensor("asleep", asleep)) {
        ESP_LOGI(STATE_MANAGER_TAG, "Vehicle sleep state: %s", asleep ? "ASLEEP" : "AWAKE");
    }
}

void VehicleStateManager::update_unlocked(bool unlocked) {
    if (doors_lock_ != nullptr) {
        auto new_state = unlocked ? lock::LOCK_STATE_UNLOCKED : lock::LOCK_STATE_LOCKED;
        if (doors_lock_->state != new_state) {
            doors_lock_->publish_state(new_state);
            ESP_LOGI(STATE_MANAGER_TAG, "Vehicle lock state: %s", unlocked ? "UNLOCKED" : "LOCKED");
        }
    }
    // NOTE: "locked" uses device_class "lock" (see __init__.py CONFIG_SCHEMA), for which the
    // HA convention is state=ON means "unlocked"/open. This matches Pedro's "is_unlocked"
    // sensor. (The previous "!unlocked" here was inverted relative to that device_class.)
    publish_binary_sensor("locked", unlocked);
}

void VehicleStateManager::update_user_present(bool present) {
    if (publish_binary_sensor("user_present", present)) {
        ESP_LOGI(STATE_MANAGER_TAG, "User presence: %s", present ? "PRESENT" : "NOT_PRESENT");
    }
    is_user_present_ = present;
}

void VehicleStateManager::update_charge_flap_open(bool open) {
    if (charge_port_door_cover_ != nullptr) {
        charge_port_door_cover_->position = open ? cover::COVER_OPEN : cover::COVER_CLOSED;
        charge_port_door_cover_->publish_state();
    }
    publish_binary_sensor("charge_flap_open", open);
}

void VehicleStateManager::update_charging_amps(float amps) {
    publish_sensor_state(charging_amps_number_, amps);
}

void VehicleStateManager::update_charger_connected(bool connected) {
    publish_binary_sensor("charger", connected);
}

// Migrated from PedroKTFC/esphome-tesla-ble: "ble_disconnected_time" sensor.
// Driven from TeslaBLEVehicle::update()/handle_connection_*() (tesla_ble_vehicle.cpp),
// which tracks how long the BLE link has been down.
void VehicleStateManager::update_ble_disconnected_seconds(float seconds) {
    publish_sensor("ble_disconnected_time", seconds);
}

void VehicleStateManager::set_sensors_available(bool available) {
    set_sensor_available(get_binary_sensor("asleep"), available);
    set_sensor_available(get_binary_sensor("user_present"), available);
}

void VehicleStateManager::reset_all_states() {
    is_charging_ = false;
    set_sensors_available(false);
}

bool VehicleStateManager::is_asleep() const {
    auto* sensor = get_binary_sensor("asleep");
    return sensor ? sensor->state : true;
}

bool VehicleStateManager::is_unlocked() const {
    if (doors_lock_) {
        return doors_lock_->state == lock::LOCK_STATE_UNLOCKED;
    }
    return false;
}

bool VehicleStateManager::is_user_present() const {
    auto* sensor = get_binary_sensor("user_present");
    return sensor ? sensor->state : false;
}

bool VehicleStateManager::is_charge_flap_open() const {
    if (charge_port_door_cover_) {
        return charge_port_door_cover_->position == cover::COVER_OPEN;
    }
    return false;
}

float VehicleStateManager::get_charging_amps() const {
    return charging_amps_number_ ? charging_amps_number_->state : 0.0f;
}

void VehicleStateManager::update_charging_amps_max(int32_t new_max) {
    if (new_max <= 0) {
        ESP_LOGW(STATE_MANAGER_TAG, "Invalid max charging amps: %ld A", static_cast<long>(new_max));
        return;
    }

    if (new_max == charging_amps_max_) {
        return;
    }

    charging_amps_max_ = new_max;

    if (charging_amps_number_ && parent_) {
        parent_->update_charging_amps_max_value(new_max);
    }
}

void VehicleStateManager::track_command_issued() {
}

bool VehicleStateManager::publish_sensor_state(binary_sensor::BinarySensor* sensor, bool state) {
    if (sensor != nullptr) {
        sensor->publish_state(state);
        return true;
    }
    return false;
}

bool VehicleStateManager::publish_sensor_state(sensor::Sensor* sensor, float state) {
    if (sensor != nullptr) {
        sensor->publish_state(state);
        return true;
    }
    return false;
}

bool VehicleStateManager::publish_sensor_state(switch_::Switch* switch_comp, bool state) {
    if (switch_comp != nullptr) {
        switch_comp->publish_state(state);
        return true;
    }
    return false;
}

bool VehicleStateManager::publish_sensor_state(number::Number* number_comp, float state) {
    if (number_comp != nullptr) {
        number_comp->publish_state(state);
        return true;
    }
    return false;
}

bool VehicleStateManager::publish_sensor_state(text_sensor::TextSensor* sensor, const std::string& state) {
    if (sensor != nullptr) {
        sensor->publish_state(state);
        return true;
    }
    return false;
}

void VehicleStateManager::set_sensor_available(binary_sensor::BinarySensor* sensor, bool available) {
    if (sensor != nullptr) {
        sensor->set_has_state(available);
    }
}

void VehicleStateManager::set_sensor_available(sensor::Sensor* sensor, bool available) {
    if (sensor != nullptr) {
        sensor->set_has_state(available);
    }
}

std::optional<bool> VehicleStateManager::convert_sleep_status(VCSEC_VehicleSleepStatus_E status) {
    switch (status) {
        case VCSEC_VehicleSleepStatus_E_VEHICLE_SLEEP_STATUS_AWAKE:
            return false;
        case VCSEC_VehicleSleepStatus_E_VEHICLE_SLEEP_STATUS_ASLEEP:
            return true;
        default:
            return std::nullopt;
    }
}

std::optional<bool> VehicleStateManager::convert_lock_status(VCSEC_VehicleLockState_E status) {
    switch (status) {
        case VCSEC_VehicleLockState_E_VEHICLELOCKSTATE_UNLOCKED:
        case VCSEC_VehicleLockState_E_VEHICLELOCKSTATE_SELECTIVE_UNLOCKED:
            return true;
        case VCSEC_VehicleLockState_E_VEHICLELOCKSTATE_LOCKED:
        case VCSEC_VehicleLockState_E_VEHICLELOCKSTATE_INTERNAL_LOCKED:
            return false;
        default:
            return std::nullopt;
    }
}

std::optional<bool> VehicleStateManager::convert_user_presence(VCSEC_UserPresence_E presence) {
    switch (presence) {
        case VCSEC_UserPresence_E_VEHICLE_USER_PRESENCE_PRESENT:
            return true;
        case VCSEC_UserPresence_E_VEHICLE_USER_PRESENCE_NOT_PRESENT:
            return false;
        default:
            return std::nullopt;
    }
}

std::string VehicleStateManager::get_charging_state_text(const CarServer_ChargeState_ChargingState& state) {
    switch (state.which_type) {
        case CarServer_ChargeState_ChargingState_Disconnected_tag: return "Disconnected";
        case CarServer_ChargeState_ChargingState_NoPower_tag: return "No Power";
        case CarServer_ChargeState_ChargingState_Starting_tag: return "Starting";
        case CarServer_ChargeState_ChargingState_Charging_tag: return "Charging";
        case CarServer_ChargeState_ChargingState_Complete_tag: return "Complete";
        case CarServer_ChargeState_ChargingState_Stopped_tag: return "Stopped";
        case CarServer_ChargeState_ChargingState_Calibrating_tag: return "Calibrating";
        default: return "Unknown";
    }
}

bool VehicleStateManager::is_charger_connected_from_state(const CarServer_ChargeState_ChargingState& state) {
    switch (state.which_type) {
        case CarServer_ChargeState_ChargingState_Disconnected_tag:
        case CarServer_ChargeState_ChargingState_Unknown_tag:
            return false;
        default:
            return true;
    }
}

std::string VehicleStateManager::get_iec61851_state_text(const CarServer_ChargeState_ChargingState& state) {
    switch (state.which_type) {
        case CarServer_ChargeState_ChargingState_Disconnected_tag: return "A";
        case CarServer_ChargeState_ChargingState_NoPower_tag: return "E";
        case CarServer_ChargeState_ChargingState_Starting_tag: return "C";
        case CarServer_ChargeState_ChargingState_Charging_tag: return "C";
        case CarServer_ChargeState_ChargingState_Complete_tag: return "B";
        case CarServer_ChargeState_ChargingState_Stopped_tag: return "B";
        case CarServer_ChargeState_ChargingState_Calibrating_tag: return "C";
        default: return "F";
    }
}

std::string VehicleStateManager::get_shift_state_text(const CarServer_ShiftState& state) {
    switch (state.which_type) {
        case CarServer_ShiftState_P_tag: return "P";
        case CarServer_ShiftState_R_tag: return "R";
        case CarServer_ShiftState_N_tag: return "N";
        case CarServer_ShiftState_D_tag: return "D";
        case CarServer_ShiftState_SNA_tag: return "SNA";
        case CarServer_ShiftState_Invalid_tag: return "Invalid";
        default: return "Unknown";
    }
}

// Migrated from PedroKTFC/esphome-tesla-ble: text mapping for CarServer_ClimateState.defrost_mode.
std::string VehicleStateManager::get_defrost_state_text(int defrost_mode_tag) {
    switch (defrost_mode_tag) {
        case CarServer_ClimateState_DefrostMode_Off_tag: return "Off";
        case CarServer_ClimateState_DefrostMode_Normal_tag: return "Normal";
        case CarServer_ClimateState_DefrostMode_Max_tag: return "Max";
        default: return "Unknown";
    }
}

// Migrated from PedroKTFC/esphome-tesla-ble: text mapping for CarServer_ChargeState.charge_port_latch.
std::string VehicleStateManager::get_charge_port_latch_state_text(int latch_tag) {
    switch (latch_tag) {
        case CarServer_ChargePortLatchState_SNA_tag: return "SNA";
        case CarServer_ChargePortLatchState_Disengaged_tag: return "Disengaged";
        case CarServer_ChargePortLatchState_Engaged_tag: return "Engaged";
        case CarServer_ChargePortLatchState_Blocking_tag: return "Blocking";
        default: return "Unknown";
    }
}

} // namespace tesla_ble_vehicle
} // namespace esphome
