#include "tesla_ble_vehicle_sensor.h"
#include "esphome/core/log.h"
#include "esphome/core/application.h"
#include "esphome/components/tesla_ble_vehicle/tesla_ble_vehicle.h"
#include "esphome/components/tesla_ble_vehicle/vehicle_state_manager.h"

namespace esphome {
namespace tesla_ble_vehicle {

static const char *const SENSOR_TAG = "tesla_ble_vehicle.sensor";

void TeslaBLEVehicleSensor::setup() {
  ESP_LOGCONFIG(SENSOR_TAG, "Tesla BLE Vehicle Sensor component setup.");
}

void TeslaBLEVehicleSensor::update() {
  ESP_LOGD(SENSOR_TAG, "Update called - data is handled directly by VehicleStateManager.");
  // 无需手动搬运传感器数据，状态管理器已自动发布
}

}  // namespace tesla_ble_vehicle
}  // namespace esphome
