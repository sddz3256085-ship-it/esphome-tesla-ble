"""text_sensor platform for the tesla_ble_vehicle component.

Allows declaring the vehicle's text sensors with the standard ESPHome
platform syntax, in addition to the direct sub-key syntax under the
`tesla_ble_vehicle:` hub block:

    text_sensor:
      - platform: tesla_ble_vehicle
        tesla_ble_vehicle_id: tesla_ble_vehicle_id
        shift_state:
          id: vehicle_shift_state
          name: "Tesla Shift State"

Both syntaxes are fully equivalent - the entity is wired to the hub and
receives the same state updates. Do not declare the same key in both
places (this is rejected at config validation time).
"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.types import ConfigType

from . import TeslaBLEVehicle

DEPENDENCIES = ["tesla_ble_vehicle"]

CONF_TESLA_BLE_VEHICLE_ID = "tesla_ble_vehicle_id"

# YAML key -> internal auto-entity id the C++ side publishes to.
TEXT_SENSOR_KEYS = {
    "shift_state": "shift_state",
    "charging_state": "charging_state",
    "iec61851_state": "iec61851_state",
    "defrost_state": "defrost_state",
    "charge_port_latch_state": "charge_port_latch_state",
}

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(text_sensor.TextSensor),
        cv.Required(CONF_TESLA_BLE_VEHICLE_ID): cv.use_id(TeslaBLEVehicle),
    }
).extend(
    {
        cv.Optional(key): text_sensor.text_sensor_schema()
        for key in TEXT_SENSOR_KEYS
    }
)


async def to_code(config: ConfigType) -> None:
    hub = await cg.get_variable(config[CONF_TESLA_BLE_VEHICLE_ID])
    for key, auto_id in TEXT_SENSOR_KEYS.items():
        if key in config:
            ts = await text_sensor.new_text_sensor(config[key])
            # user_defined=True: always wins over the auto-created internal entity.
            cg.add(hub.set_text_sensor(auto_id, ts, True))
