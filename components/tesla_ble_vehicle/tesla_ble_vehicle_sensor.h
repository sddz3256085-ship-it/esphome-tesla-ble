#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace tesla_ble_vehicle {

class TeslaBLEVehicle;

class TeslaBLEVehicleSensor : public PollingComponent {
 public:
  // Setter 方法声明（按字母顺序）
  void set_battery_level_sensor(sensor::Sensor *s) { battery_level_sensor_ = s; }
  void set_range_sensor(sensor::Sensor *s) { range_sensor_ = s; }
  void set_range_rated_api_sensor(sensor::Sensor *s) { range_rated_api_sensor_ = s; }
  void set_outside_temp_sensor(sensor::Sensor *s) { outside_temp_sensor_ = s; }
  void set_inside_temp_sensor(sensor::Sensor *s) { inside_temp_sensor_ = s; }
  void set_driver_temp_setting_sensor(sensor::Sensor *s) { driver_temp_setting_sensor_ = s; }
  void set_passenger_temp_setting_sensor(sensor::Sensor *s) { passenger_temp_setting_sensor_ = s; }
  void set_speed_sensor(sensor::Sensor *s) { speed_sensor_ = s; }
  void set_odometer_sensor(sensor::Sensor *s) { odometer_sensor_ = s; }
  void set_charger_power_sensor(sensor::Sensor *s) { charger_power_sensor_ = s; }
  void set_charger_voltage_sensor(sensor::Sensor *s) { charger_voltage_sensor_ = s; }
  void set_charger_current_sensor(sensor::Sensor *s) { charger_current_sensor_ = s; }
  void set_charging_rate_sensor(sensor::Sensor *s) { charging_rate_sensor_ = s; }
  void set_charge_rate_sensor(sensor::Sensor *s) { charge_rate_sensor_ = s; }
  void set_energy_added_sensor(sensor::Sensor *s) { energy_added_sensor_ = s; }
  void set_charge_energy_added_sensor(sensor::Sensor *s) { charge_energy_added_sensor_ = s; }
  void set_time_to_full_sensor(sensor::Sensor *s) { time_to_full_sensor_ = s; }
  void set_time_to_full_charge_sensor(sensor::Sensor *s) { time_to_full_charge_sensor_ = s; }
  void set_tpms_fl_sensor(sensor::Sensor *s) { tpms_fl_sensor_ = s; }
  void set_tpms_fr_sensor(sensor::Sensor *s) { tpms_fr_sensor_ = s; }
  void set_tpms_rl_sensor(sensor::Sensor *s) { tpms_rl_sensor_ = s; }
  void set_tpms_rr_sensor(sensor::Sensor *s) { tpms_rr_sensor_ = s; }

  void setup() override;
  void update() override;

 protected:
  // 传感器指针成员
  sensor::Sensor *battery_level_sensor_{nullptr};
  sensor::Sensor *range_sensor_{nullptr};
  sensor::Sensor *range_rated_api_sensor_{nullptr};
  sensor::Sensor *outside_temp_sensor_{nullptr};
  sensor::Sensor *inside_temp_sensor_{nullptr};
  sensor::Sensor *driver_temp_setting_sensor_{nullptr};
  sensor::Sensor *passenger_temp_setting_sensor_{nullptr};
  sensor::Sensor *speed_sensor_{nullptr};
  sensor::Sensor *odometer_sensor_{nullptr};
  sensor::Sensor *charger_power_sensor_{nullptr};
  sensor::Sensor *charger_voltage_sensor_{nullptr};
  sensor::Sensor *charger_current_sensor_{nullptr};
  sensor::Sensor *charging_rate_sensor_{nullptr};
  sensor::Sensor *charge_rate_sensor_{nullptr};
  sensor::Sensor *energy_added_sensor_{nullptr};
  sensor::Sensor *charge_energy_added_sensor_{nullptr};
  sensor::Sensor *time_to_full_sensor_{nullptr};
  sensor::Sensor *time_to_full_charge_sensor_{nullptr};
  sensor::Sensor *tpms_fl_sensor_{nullptr};
  sensor::Sensor *tpms_fr_sensor_{nullptr};
  sensor::Sensor *tpms_rl_sensor_{nullptr};
  sensor::Sensor *tpms_rr_sensor_{nullptr};
};

}  // namespace tesla_ble_vehicle
}  // namespace esphome
