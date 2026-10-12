"""sensor platform for the tesla_ble_vehicle component.

Allows declaring the vehicle's numeric sensors with the standard ESPHome
platform syntax, in addition to the direct sub-key syntax under the
`tesla_ble_vehicle:` hub block:

    sensor:
      - platform: tesla_ble_vehicle
        tesla_ble_vehicle_id: tesla_ble_vehicle_id
        odometer:
          id: vehicle_odometer
          name: "Tesla Odometer"

Both syntaxes are fully equivalent - the entity is wired to the hub and
receives the same state updates. Do not declare the same key in both
places (this is rejected at config validation time).

NOTE: this file used to create a standalone TeslaBLEVehicleSensor container
that was never connected to the vehicle state manager, so sensors declared
this way never received any updates. The container class is still created
for backward compatibility of `id:` references, but every sensor is now
registered on the TeslaBLEVehicle hub and receives live data.
"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_ID,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_SPEED,
    DEVICE_CLASS_DISTANCE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_DURATION,
    DEVICE_CLASS_PRESSURE,
    STATE_CLASS_MEASUREMENT,
    UNIT_PERCENT,
    UNIT_KILOMETER_PER_HOUR,
    UNIT_KILOMETER,
    UNIT_CELSIUS,
    UNIT_KILOWATT,
    UNIT_VOLT,
    UNIT_AMPERE,
    UNIT_KILOWATT_HOURS,
    UNIT_MINUTE,
    UNIT_SECOND,
)
from esphome.types import ConfigType

from . import TeslaBLEVehicle

DEPENDENCIES = ['tesla_ble_vehicle']

CONF_TESLA_BLE_VEHICLE_ID = "tesla_ble_vehicle_id"

tesla_ble_vehicle_ns = cg.esphome_ns.namespace('tesla_ble_vehicle')
# Kept for backward compatibility: the platform block itself still gets a
# component id you can reference, it simply no longer owns the sensors.
TeslaBLEVehicleSensor = tesla_ble_vehicle_ns.class_(
    'TeslaBLEVehicleSensor', cg.PollingComponent
)

# (YAML key, hub auto-entity id) -> sensor schema options.
# The hub auto-entity id is the key VehicleStateManager publishes to; the
# legacy aliases "energy_added" and "time_to_full" are mapped onto the live
# hub ids so they actually receive data.
SENSOR_KEYS = {
    "battery_level": (
        "battery_level",
        dict(unit_of_measurement=UNIT_PERCENT, device_class=DEVICE_CLASS_BATTERY,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=0),
    ),
    "range": (
        "range",
        dict(unit_of_measurement="mi", device_class=DEVICE_CLASS_DISTANCE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "range_rated_api": (
        "range_rated_api",
        dict(unit_of_measurement=UNIT_KILOMETER, device_class=DEVICE_CLASS_DISTANCE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "outside_temp": (
        "outside_temp",
        dict(unit_of_measurement=UNIT_CELSIUS, device_class=DEVICE_CLASS_TEMPERATURE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "inside_temp": (
        "inside_temp",
        dict(unit_of_measurement=UNIT_CELSIUS, device_class=DEVICE_CLASS_TEMPERATURE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "driver_temp_setting": (
        "driver_temp_setting",
        dict(unit_of_measurement=UNIT_CELSIUS, device_class=DEVICE_CLASS_TEMPERATURE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "passenger_temp_setting": (
        "passenger_temp_setting",
        dict(unit_of_measurement=UNIT_CELSIUS, device_class=DEVICE_CLASS_TEMPERATURE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "speed": (
        "speed",
        dict(unit_of_measurement=UNIT_KILOMETER_PER_HOUR, device_class=DEVICE_CLASS_SPEED,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "odometer": (
        "odometer",
        # update_drive_state() publishes optional_odometer_in_hundredths_of_a_mile / 100, i.e. MILES.
        dict(unit_of_measurement="mi", device_class=DEVICE_CLASS_DISTANCE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=2),
    ),
    "charger_power": (
        "charger_power",
        dict(unit_of_measurement=UNIT_KILOWATT, device_class=DEVICE_CLASS_POWER,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "charger_voltage": (
        "charger_voltage",
        dict(unit_of_measurement=UNIT_VOLT, device_class=DEVICE_CLASS_VOLTAGE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=0),
    ),
    "charger_current": (
        "charger_current",
        dict(unit_of_measurement=UNIT_AMPERE, device_class=DEVICE_CLASS_CURRENT,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "charging_rate": (
        "charging_rate",
        dict(unit_of_measurement="mph", device_class=DEVICE_CLASS_SPEED,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "charge_rate": (
        "charge_rate",
        dict(unit_of_measurement=UNIT_KILOMETER_PER_HOUR, device_class=DEVICE_CLASS_SPEED,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    # Legacy alias kept for backward compatibility; the live hub id is charge_energy_added.
    "energy_added": (
        "charge_energy_added",
        dict(unit_of_measurement=UNIT_KILOWATT_HOURS, device_class=DEVICE_CLASS_ENERGY,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=2),
    ),
    "charge_energy_added": (
        "charge_energy_added",
        dict(unit_of_measurement=UNIT_KILOWATT_HOURS, device_class=DEVICE_CLASS_ENERGY,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=2),
    ),
    # Legacy alias kept for backward compatibility; the live hub id is time_to_full_charge.
    "time_to_full": (
        "time_to_full_charge",
        dict(unit_of_measurement=UNIT_MINUTE, device_class=DEVICE_CLASS_DURATION,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=0),
    ),
    "time_to_full_charge": (
        "time_to_full_charge",
        dict(unit_of_measurement=UNIT_MINUTE, device_class=DEVICE_CLASS_DURATION,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=0),
    ),
    "tpms_front_left": (
        "tpms_front_left",
        dict(unit_of_measurement="bar", device_class=DEVICE_CLASS_PRESSURE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "tpms_front_right": (
        "tpms_front_right",
        dict(unit_of_measurement="bar", device_class=DEVICE_CLASS_PRESSURE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "tpms_rear_left": (
        "tpms_rear_left",
        dict(unit_of_measurement="bar", device_class=DEVICE_CLASS_PRESSURE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    "tpms_rear_right": (
        "tpms_rear_right",
        dict(unit_of_measurement="bar", device_class=DEVICE_CLASS_PRESSURE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=1),
    ),
    # --- Migrated from PedroKTFC/esphome-tesla-ble ---
    "max_soc": (
        "max_soc",
        dict(unit_of_measurement=UNIT_PERCENT, device_class=DEVICE_CLASS_BATTERY,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=0),
    ),
    "max_amps": (
        "max_amps",
        dict(unit_of_measurement=UNIT_AMPERE, device_class=DEVICE_CLASS_CURRENT,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=0),
    ),
    "charge_distance_added": (
        "charge_distance_added",
        dict(unit_of_measurement="mi", device_class=DEVICE_CLASS_DISTANCE,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=2),
    ),
    "charger_phases": (
        "charger_phases",
        dict(accuracy_decimals=0),
    ),
    "ble_disconnected_time": (
        "ble_disconnected_time",
        dict(unit_of_measurement=UNIT_SECOND, device_class=DEVICE_CLASS_DURATION,
             state_class=STATE_CLASS_MEASUREMENT, accuracy_decimals=0),
    ),
}

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(TeslaBLEVehicleSensor),
        cv.Required(CONF_TESLA_BLE_VEHICLE_ID): cv.use_id(TeslaBLEVehicle),
    }
).extend(
    {
        cv.Optional(key): sensor.sensor_schema(**options)
        for key, (_, options) in SENSOR_KEYS.items()
    }
).extend(cv.polling_component_schema('60s'))


async def to_code(config: ConfigType) -> None:
    # Backward-compatible container component (its update() is a no-op).
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    hub = await cg.get_variable(config[CONF_TESLA_BLE_VEHICLE_ID])
    for key, (auto_id, _) in SENSOR_KEYS.items():
        if key in config:
            sens = await sensor.new_sensor(config[key])
            # user_defined=True: always wins over the auto-created internal entity.
            cg.add(hub.set_sensor(auto_id, sens, True))
