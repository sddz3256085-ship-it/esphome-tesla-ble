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
    UNIT_BAR,
    UNIT_MILES_PER_HOUR,
    UNIT_MILES,
)

DEPENDENCIES = ['tesla_ble_vehicle']

tesla_ble_vehicle_ns = cg.esphome_ns.namespace('tesla_ble_vehicle')
TeslaBLEVehicleSensor = tesla_ble_vehicle_ns.class_(
    'TeslaBLEVehicleSensor', cg.PollingComponent
)

# 所有支持的传感器键名（与内部 ID 保持一致）
CONF_BATTERY_LEVEL = "battery_level"
CONF_RANGE = "range"
CONF_RANGE_RATED_API = "range_rated_api"
CONF_OUTSIDE_TEMP = "outside_temp"
CONF_INSIDE_TEMP = "inside_temp"
CONF_DRIVER_TEMP_SETTING = "driver_temp_setting"
CONF_PASSENGER_TEMP_SETTING = "passenger_temp_setting"
CONF_SPEED = "speed"
CONF_ODOMETER = "odometer"
CONF_CHARGER_POWER = "charger_power"
CONF_CHARGER_VOLTAGE = "charger_voltage"
CONF_CHARGER_CURRENT = "charger_current"
CONF_CHARGING_RATE = "charging_rate"
CONF_CHARGE_RATE = "charge_rate"
CONF_ENERGY_ADDED = "energy_added"
CONF_CHARGE_ENERGY_ADDED = "charge_energy_added"
CONF_TIME_TO_FULL = "time_to_full"
CONF_TIME_TO_FULL_CHARGE = "time_to_full_charge"
CONF_TPMS_FL = "tpms_front_left"
CONF_TPMS_FR = "tpms_front_right"
CONF_TPMS_RL = "tpms_rear_left"
CONF_TPMS_RR = "tpms_rear_right"

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(TeslaBLEVehicleSensor),
    cv.Optional(CONF_BATTERY_LEVEL): sensor.sensor_schema(
        unit_of_measurement=UNIT_PERCENT,
        device_class=DEVICE_CLASS_BATTERY,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=0,
    ),
    cv.Optional(CONF_RANGE): sensor.sensor_schema(
        unit_of_measurement=UNIT_MILES,           # 内部单位是英里
        device_class=DEVICE_CLASS_DISTANCE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_RANGE_RATED_API): sensor.sensor_schema(
        unit_of_measurement=UNIT_KILOMETER,
        device_class=DEVICE_CLASS_DISTANCE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_OUTSIDE_TEMP): sensor.sensor_schema(
        unit_of_measurement=UNIT_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_INSIDE_TEMP): sensor.sensor_schema(
        unit_of_measurement=UNIT_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_DRIVER_TEMP_SETTING): sensor.sensor_schema(
        unit_of_measurement=UNIT_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_PASSENGER_TEMP_SETTING): sensor.sensor_schema(
        unit_of_measurement=UNIT_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_SPEED): sensor.sensor_schema(
        unit_of_measurement=UNIT_KILOMETER_PER_HOUR,
        device_class=DEVICE_CLASS_SPEED,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_ODOMETER): sensor.sensor_schema(
        unit_of_measurement=UNIT_MILES,           # 内部单位英里
        device_class=DEVICE_CLASS_DISTANCE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_CHARGER_POWER): sensor.sensor_schema(
        unit_of_measurement=UNIT_KILOWATT,
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_CHARGER_VOLTAGE): sensor.sensor_schema(
        unit_of_measurement=UNIT_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=0,
    ),
    cv.Optional(CONF_CHARGER_CURRENT): sensor.sensor_schema(
        unit_of_measurement=UNIT_AMPERE,
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_CHARGING_RATE): sensor.sensor_schema(
        unit_of_measurement=UNIT_MILES_PER_HOUR,
        device_class=DEVICE_CLASS_SPEED,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_CHARGE_RATE): sensor.sensor_schema(
        unit_of_measurement=UNIT_KILOMETER_PER_HOUR,
        device_class=DEVICE_CLASS_SPEED,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_ENERGY_ADDED): sensor.sensor_schema(
        unit_of_measurement=UNIT_KILOWATT_HOURS,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=2,
    ),
    cv.Optional(CONF_CHARGE_ENERGY_ADDED): sensor.sensor_schema(
        unit_of_measurement=UNIT_KILOWATT_HOURS,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=2,
    ),
    cv.Optional(CONF_TIME_TO_FULL): sensor.sensor_schema(
        unit_of_measurement=UNIT_MINUTE,
        device_class=DEVICE_CLASS_DURATION,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=0,
    ),
    cv.Optional(CONF_TIME_TO_FULL_CHARGE): sensor.sensor_schema(
        unit_of_measurement=UNIT_MINUTE,
        device_class=DEVICE_CLASS_DURATION,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=0,
    ),
    cv.Optional(CONF_TPMS_FL): sensor.sensor_schema(
        unit_of_measurement=UNIT_BAR,
        device_class=DEVICE_CLASS_PRESSURE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_TPMS_FR): sensor.sensor_schema(
        unit_of_measurement=UNIT_BAR,
        device_class=DEVICE_CLASS_PRESSURE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_TPMS_RL): sensor.sensor_schema(
        unit_of_measurement=UNIT_BAR,
        device_class=DEVICE_CLASS_PRESSURE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
    cv.Optional(CONF_TPMS_RR): sensor.sensor_schema(
        unit_of_measurement=UNIT_BAR,
        device_class=DEVICE_CLASS_PRESSURE,
        state_class=STATE_CLASS_MEASUREMENT,
        accuracy_decimals=1,
    ),
}).extend(cv.polling_component_schema('60s'))

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    # 直接映射配置键到 setter 方法
    sensor_map = {
        CONF_BATTERY_LEVEL: "set_battery_level_sensor",
        CONF_RANGE: "set_range_sensor",
        CONF_RANGE_RATED_API: "set_range_rated_api_sensor",
        CONF_OUTSIDE_TEMP: "set_outside_temp_sensor",
        CONF_INSIDE_TEMP: "set_inside_temp_sensor",
        CONF_DRIVER_TEMP_SETTING: "set_driver_temp_setting_sensor",
        CONF_PASSENGER_TEMP_SETTING: "set_passenger_temp_setting_sensor",
        CONF_SPEED: "set_speed_sensor",
        CONF_ODOMETER: "set_odometer_sensor",
        CONF_CHARGER_POWER: "set_charger_power_sensor",
        CONF_CHARGER_VOLTAGE: "set_charger_voltage_sensor",
        CONF_CHARGER_CURRENT: "set_charger_current_sensor",
        CONF_CHARGING_RATE: "set_charging_rate_sensor",
        CONF_CHARGE_RATE: "set_charge_rate_sensor",
        CONF_ENERGY_ADDED: "set_energy_added_sensor",
        CONF_CHARGE_ENERGY_ADDED: "set_charge_energy_added_sensor",
        CONF_TIME_TO_FULL: "set_time_to_full_sensor",
        CONF_TIME_TO_FULL_CHARGE: "set_time_to_full_charge_sensor",
        CONF_TPMS_FL: "set_tpms_fl_sensor",
        CONF_TPMS_FR: "set_tpms_fr_sensor",
        CONF_TPMS_RL: "set_tpms_rl_sensor",
        CONF_TPMS_RR: "set_tpms_rr_sensor",
    }
    for key, setter in sensor_map.items():
        if key in config:
            sens = await sensor.new_sensor(config[key])
            cg.add(getattr(var, setter)(sens))
