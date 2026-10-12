"""binary_sensor platform for the tesla_ble_vehicle component.

Allows declaring the vehicle's binary sensors with the standard ESPHome
platform syntax, in addition to the direct sub-key syntax under the
`tesla_ble_vehicle:` hub block:

    binary_sensor:
      - platform: tesla_ble_vehicle
        tesla_ble_vehicle_id: tesla_ble_vehicle_id
        locked:
          id: vehicle_locked
          name: "Tesla Vehicle Locked State"
        user_present:
          id: vehicle_user_present
          name: "Tesla User Presence"

Both syntaxes are fully equivalent - the entity is wired to the hub and
receives the same state updates. Use whichever you prefer; do not declare
the same key in both places (this is rejected at config validation time).
"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.types import ConfigType

from . import TeslaBLEVehicle

DEPENDENCIES = ["tesla_ble_vehicle"]

CONF_TESLA_BLE_VEHICLE_ID = "tesla_ble_vehicle_id"

# YAML key -> internal auto-entity id the C++ side publishes to.
# "charging" is the user-facing key for the auto entity internally called
# "charger" (VehicleStateManager::update_charge_state publishes to "charger").
BINARY_SENSOR_KEYS = {
    "locked": ("locked", None),
    "user_present": ("user_present", "occupancy"),
    "asleep": ("asleep", None),
    "charging": ("charger", "battery_charging"),
    "charge_flap_open": ("charge_flap_open", "door"),
    "boot_open": ("boot_open", "door"),
    "frunk_open": ("frunk_open", "door"),
    "windows_state": ("windows_state", "window"),
    "climate_on": ("climate_on", None),
    "parking_brake": ("parking_brake", "problem"),
    "door_driver_front": ("door_driver_front", "door"),
    "door_driver_rear": ("door_driver_rear", "door"),
    "door_passenger_front": ("door_passenger_front", "door"),
    "door_passenger_rear": ("door_passenger_rear", "door"),
    "window_driver_front": ("window_driver_front", "window"),
    "window_driver_rear": ("window_driver_rear", "window"),
    "window_passenger_front": ("window_passenger_front", "window"),
    "window_passenger_rear": ("window_passenger_rear", "window"),
    "sunroof": ("sunroof", "window"),
}

def _binary_sensor_schema(device_class):
    """binary_sensor_schema() with device_class only when set (None would fail validation)."""
    if device_class is None:
        return binary_sensor.binary_sensor_schema()
    return binary_sensor.binary_sensor_schema(device_class=device_class)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(binary_sensor.BinarySensor),
        cv.Required(CONF_TESLA_BLE_VEHICLE_ID): cv.use_id(TeslaBLEVehicle),
    }
).extend(
    {
        cv.Optional(key): _binary_sensor_schema(device_class)
        for key, (_, device_class) in BINARY_SENSOR_KEYS.items()
    }
)


async def to_code(config: ConfigType) -> None:
    hub = await cg.get_variable(config[CONF_TESLA_BLE_VEHICLE_ID])
    for key, (auto_id, _) in BINARY_SENSOR_KEYS.items():
        if key in config:
            bs = await binary_sensor.new_binary_sensor(config[key])
            # user_defined=True: always wins over the auto-created internal entity.
            cg.add(hub.set_binary_sensor(auto_id, bs, True))
