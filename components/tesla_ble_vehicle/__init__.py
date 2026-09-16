import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import ble_client, binary_sensor, button, switch, number, sensor, text_sensor, lock, cover, climate
from esphome.const import (
    CONF_ACCURACY_DECIMALS,
    CONF_DEVICE_CLASS,
    CONF_DISABLED_BY_DEFAULT,
    CONF_ENTITY_CATEGORY,
    CONF_FORCE_UPDATE,
    CONF_ICON,
    CONF_ID,
    CONF_INTERNAL,
    CONF_MODE,
    CONF_NAME,
    CONF_RESTORE_MODE,
    CONF_UNIT_OF_MEASUREMENT,
)
from esphome import automation


CODEOWNERS = ["@yoziru"]
DEPENDENCIES = ["ble_client"]
AUTO_LOAD = ["binary_sensor", "button", "switch", "number", "sensor", "text_sensor", "lock", "cover", "climate"]

tesla_ble_vehicle_ns = cg.esphome_ns.namespace("tesla_ble_vehicle")
TeslaBLEVehicle = tesla_ble_vehicle_ns.class_(
    "TeslaBLEVehicle", cg.PollingComponent, ble_client.BLEClientNode
)

# Custom button classes
TeslaWakeButton = tesla_ble_vehicle_ns.class_("TeslaWakeButton", button.Button)
TeslaPairButton = tesla_ble_vehicle_ns.class_("TeslaPairButton", button.Button)
TeslaRegenerateKeyButton = tesla_ble_vehicle_ns.class_("TeslaRegenerateKeyButton", button.Button)
TeslaForceUpdateButton = tesla_ble_vehicle_ns.class_("TeslaForceUpdateButton", button.Button)
TeslaFlashLightsButton = tesla_ble_vehicle_ns.class_("TeslaFlashLightsButton", button.Button)
TeslaHonkHornButton = tesla_ble_vehicle_ns.class_("TeslaHonkHornButton", button.Button)
TeslaUnlatchDriverDoorButton = tesla_ble_vehicle_ns.class_("TeslaUnlatchDriverDoorButton", button.Button)
TeslaStartDrivingButton = tesla_ble_vehicle_ns.class_("TeslaStartDrivingButton", button.Button)

# Custom switch classes
TeslaChargingSwitch = tesla_ble_vehicle_ns.class_("TeslaChargingSwitch", switch.Switch)
TeslaSteeringWheelHeatSwitch = tesla_ble_vehicle_ns.class_("TeslaSteeringWheelHeatSwitch", switch.Switch)
TeslaSentryModeSwitch = tesla_ble_vehicle_ns.class_("TeslaSentryModeSwitch", switch.Switch)

# Custom lock classes
TeslaDoorsLock = tesla_ble_vehicle_ns.class_("TeslaDoorsLock", lock.Lock)
TeslaChargePortLatchLock = tesla_ble_vehicle_ns.class_("TeslaChargePortLatchLock", lock.Lock)

# Custom cover classes
TeslaTrunkCover = tesla_ble_vehicle_ns.class_("TeslaTrunkCover", cover.Cover)
TeslaFrunkCover = tesla_ble_vehicle_ns.class_("TeslaFrunkCover", cover.Cover)
TeslaWindowsCover = tesla_ble_vehicle_ns.class_("TeslaWindowsCover", cover.Cover)
TeslaChargePortDoorCover = tesla_ble_vehicle_ns.class_("TeslaChargePortDoorCover", cover.Cover)

# Custom climate class
TeslaClimate = tesla_ble_vehicle_ns.class_("TeslaClimate", climate.Climate)

# Custom number classes
TeslaChargingAmpsNumber = tesla_ble_vehicle_ns.class_("TeslaChargingAmpsNumber", number.Number)
TeslaChargingLimitNumber = tesla_ble_vehicle_ns.class_("TeslaChargingLimitNumber", number.Number)

# Actions
WakeAction = tesla_ble_vehicle_ns.class_("WakeAction", automation.Action)
PairAction = tesla_ble_vehicle_ns.class_("PairAction", automation.Action)
RegenerateKeyAction = tesla_ble_vehicle_ns.class_("RegenerateKeyAction", automation.Action)
ForceUpdateAction = tesla_ble_vehicle_ns.class_("ForceUpdateAction", automation.Action)
SetChargingAction = tesla_ble_vehicle_ns.class_("SetChargingAction", automation.Action)
SetChargingAmpsAction = tesla_ble_vehicle_ns.class_("SetChargingAmpsAction", automation.Action)
SetChargingLimitAction = tesla_ble_vehicle_ns.class_("SetChargingLimitAction", automation.Action)
StartDrivingAction = tesla_ble_vehicle_ns.class_("StartDrivingAction", automation.Action)

# Configuration constants
CONF_VIN = "vin"
CONF_CHARGING_AMPS_MAX = "charging_amps_max"
CONF_ROLE = "role"

CONF_VCSEC_POLL_INTERVAL = "vcsec_poll_interval"
CONF_INFOTAINMENT_POLL_INTERVAL_AWAKE = "infotainment_poll_interval_awake"
CONF_INFOTAINMENT_POLL_INTERVAL_ACTIVE = "infotainment_poll_interval_active"
CONF_INFOTAINMENT_SLEEP_TIMEOUT = "infotainment_sleep_timeout"

# Must match C++ static constexpr in tesla_ble_vehicle.cpp
MIN_CHARGING_LIMIT = 50
MAX_CHARGING_LIMIT = 100
MIN_CHARGING_AMPS = 0
MAX_CHARGING_AMPS = 80

TESLA_ROLES = {
    "OWNER": "Keys_Role_ROLE_OWNER",
    "DRIVER": "Keys_Role_ROLE_DRIVER",
    "CHARGING_MANAGER": "Keys_Role_ROLE_CHARGING_MANAGER",
}

BINARY_SENSORS = [
    {"id": "asleep", "name": "Asleep", "icon": "mdi:sleep", "internal": True},
    {"id": "user_present", "name": "User Present", "icon": "mdi:account-check", "device_class": "occupancy", "internal": True},
    {"id": "charger", "name": "Charger", "icon": "mdi:power-plug", "device_class": "plug", "internal": True},
    {"id": "parking_brake", "name": "Parking Brake", "icon": "mdi:car-brake-parking", "internal": True},
    {"id": "door_driver_front", "name": "Door Driver Front", "icon": "mdi:car-door", "device_class": "door", "disabled_by_default": True, "internal": True},
    {"id": "door_driver_rear", "name": "Door Driver Rear", "icon": "mdi:car-door", "device_class": "door", "disabled_by_default": True, "internal": True},
    {"id": "door_passenger_front", "name": "Door Passenger Front", "icon": "mdi:car-door", "device_class": "door", "disabled_by_default": True, "internal": True},
    {"id": "door_passenger_rear", "name": "Door Passenger Rear", "icon": "mdi:car-door", "device_class": "door", "disabled_by_default": True, "internal": True},
    {"id": "window_driver_front", "name": "Window Driver Front", "icon": "mdi:car-window-side", "device_class": "window", "disabled_by_default": True, "internal": True},
    {"id": "window_driver_rear", "name": "Window Driver Rear", "icon": "mdi:car-window-side", "device_class": "window", "disabled_by_default": True, "internal": True},
    {"id": "window_passenger_front", "name": "Window Passenger Front", "icon": "mdi:car-window-side", "device_class": "window", "disabled_by_default": True, "internal": True},
    {"id": "window_passenger_rear", "name": "Window Passenger Rear", "icon": "mdi:car-window-side", "device_class": "window", "disabled_by_default": True, "internal": True},
    {"id": "sunroof", "name": "Sunroof", "icon": "mdi:car-select", "device_class": "window", "disabled_by_default": True, "internal": True},
]

SENSORS = [
    {"id": "battery_level", "name": "Battery", "icon": "mdi:battery", "unit": "%", "internal": True},
    {"id": "range", "name": "Range", "icon": "mdi:map-marker-distance", "device_class": "distance", "unit": "mi", "internal": True},
    {"id": "charger_power", "name": "Charger Power", "icon": "mdi:flash", "device_class": "power", "unit": "kW", "internal": True},
    {"id": "charger_voltage", "name": "Charger Voltage", "icon": "mdi:lightning-bolt", "device_class": "voltage", "unit": "V", "internal": True},
    {"id": "charger_current", "name": "Charger Current", "icon": "mdi:current-ac", "device_class": "current", "unit": "A", "internal": True},
    {"id": "charging_rate", "name": "Charging Rate", "icon": "mdi:speedometer", "device_class": "speed", "unit": "mph", "accuracy_decimals": 1, "internal": True},
    {"id": "energy_added", "name": "Energy Added", "icon": "mdi:battery-charging", "device_class": "energy", "unit": "kWh", "accuracy_decimals": 1, "internal": True},
    {"id": "time_to_full", "name": "Time to Full", "icon": "mdi:clock-outline", "device_class": "duration", "unit": "min", "internal": True},
    {"id": "outside_temp", "name": "Outside Temperature", "icon": "mdi:thermometer", "device_class": "temperature", "unit": "°C", "accuracy_decimals": 1, "internal": True},
    {"id": "odometer", "name": "Odometer", "icon": "mdi:counter", "device_class": "distance", "unit": "mi", "disabled_by_default": True, "internal": True},
    {"id": "tpms_front_left", "name": "TPMS Front Left", "icon": "mdi:car-tire-alert", "device_class": "pressure", "unit": "bar", "accuracy_decimals": 1, "internal": True},
    {"id": "tpms_front_right", "name": "TPMS Front Right", "icon": "mdi:car-tire-alert", "device_class": "pressure", "unit": "bar", "accuracy_decimals": 1, "internal": True},
    {"id": "tpms_rear_left", "name": "TPMS Rear Left", "icon": "mdi:car-tire-alert", "device_class": "pressure", "unit": "bar", "accuracy_decimals": 1, "internal": True},
    {"id": "tpms_rear_right", "name": "TPMS Rear Right", "icon": "mdi:car-tire-alert", "device_class": "pressure", "unit": "bar", "accuracy_decimals": 1, "internal": True},
]

TEXT_SENSORS = [
    {"id": "charging_state", "name": "Charging", "icon": "mdi:ev-station", "internal": True},
    {"id": "iec61851_state", "name": "IEC 61851", "icon": "mdi:ev-plug-type2", "disabled_by_default": True, "internal": True},
    {"id": "shift_state", "name": "Shift State", "icon": "mdi:car-shift-pattern", "disabled_by_default": True, "internal": True},
]

BUTTONS = [
    {"id": "wake", "name": "Wake up", "class": TeslaWakeButton, "setter": "set_wake_button", "icon": "mdi:sleep-off", "internal": True},
    {"id": "pair", "name": "Pair BLE Key", "class": TeslaPairButton, "setter": "set_pair_button", "icon": "mdi:key-wireless", "entity_category": "diagnostic", "internal": True},
    {"id": "regenerate_key", "name": "Regenerate key", "class": TeslaRegenerateKeyButton, "setter": "set_regenerate_key_button", "icon": "mdi:key-change", "entity_category": "diagnostic", "disabled_by_default": True, "internal": True},
    {"id": "force_update", "name": "Force data update", "class": TeslaForceUpdateButton, "setter": "set_force_update_button", "icon": "mdi:database-sync", "entity_category": "diagnostic", "internal": True},
    {"id": "unlatch_driver_door", "name": "Unlatch Driver Door", "class": TeslaUnlatchDriverDoorButton, "setter": None, "icon": "mdi:car-door", "disabled_by_default": True, "internal": True},
    {"id": "flash_lights", "name": "Flash Lights", "class": TeslaFlashLightsButton, "setter": None, "icon": "mdi:car-light-high", "internal": True},
    {"id": "honk_horn", "name": "Sound Horn", "class": TeslaHonkHornButton, "setter": None, "icon": "mdi:bullhorn", "internal": True},
    {"id": "start_driving", "name": "Start Driving", "class": TeslaStartDrivingButton, "setter": "set_start_driving_button", "icon": "mdi:car-key", "internal": True},
]

SWITCHES = [
    {"id": "charging", "name": "Charger", "class": TeslaChargingSwitch, "setter": "set_charging_switch", "icon": "mdi:ev-station", "internal": True},
    {"id": "steering_wheel_heat", "name": "Heated Steering", "class": TeslaSteeringWheelHeatSwitch, "setter": "set_steering_wheel_heat_switch", "icon": "mdi:steering", "internal": True},
    {"id": "sentry_mode", "name": "Sentry Mode", "class": TeslaSentryModeSwitch, "setter": "set_sentry_mode_switch", "icon": "mdi:shield-car", "internal": True},
]

LOCKS = [
    {"id": "doors", "name": "Doors", "class": TeslaDoorsLock, "setter": "set_doors_lock", "icon": "mdi:car-door-lock", "internal": True},
    {"id": "charge_port_latch", "name": "Charge Port Latch", "class": TeslaChargePortLatchLock, "setter": "set_charge_port_latch_lock", "icon": "mdi:ev-plug-tesla", "internal": True},
]

COVERS = [
    {"id": "trunk", "name": "Trunk", "class": TeslaTrunkCover, "setter": "set_trunk_cover", "icon": "mdi:car-back", "device_class": "door", "internal": True},
    {"id": "frunk", "name": "Frunk", "class": TeslaFrunkCover, "setter": "set_frunk_cover", "icon": "mdi:car", "device_class": "door", "internal": True},
    {"id": "windows", "name": "Windows", "class": TeslaWindowsCover, "setter": "set_windows_cover", "icon": "mdi:car-door", "device_class": "awning", "internal": True},
    {"id": "charge_port_door", "name": "Charge Port Door", "class": TeslaChargePortDoorCover, "setter": "set_charge_port_door_cover", "icon": "mdi:ev-plug-tesla", "device_class": "door", "internal": True},
]

CLIMATE = {
    "id": "climate", "name": "Climate", "class": TeslaClimate, "setter": "set_climate", "internal": True,
}

NUMBERS = [
    {"id": "charging_amps", "name": "Charging Amps", "class": TeslaChargingAmpsNumber, "setter": "set_charging_amps_number", "icon": "mdi:current-ac", "unit": "A", "min": 0, "max": "config", "step": 1, "internal": True},
    {"id": "charging_limit", "name": "Charging Limit", "class": TeslaChargingLimitNumber, "setter": "set_charging_limit_number", "icon": "mdi:battery-charging-100", "unit": "%", "min": 50, "max": 100, "step": 1, "internal": True},
]

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(CONF_ID): cv.declare_id(TeslaBLEVehicle),
            cv.Required(CONF_VIN): cv.string,
            cv.Optional(CONF_CHARGING_AMPS_MAX, default=32): cv.int_range(min=1, max=48),
            cv.Optional(CONF_ROLE, default="DRIVER"): cv.enum(TESLA_ROLES, upper=True),


            cv.Optional(CONF_VCSEC_POLL_INTERVAL, default=10.0): cv.float_range(min=0.2, max=300.0),
            cv.Optional(CONF_INFOTAINMENT_POLL_INTERVAL_AWAKE, default=30.0): cv.float_range(min=0.2, max=600.0),
            cv.Optional(CONF_INFOTAINMENT_POLL_INTERVAL_ACTIVE, default=10.0): cv.float_range(min=0.2, max=120.0),
            cv.Optional(CONF_INFOTAINMENT_SLEEP_TIMEOUT, default=660.0): cv.float_range(min=0.2, max=3600.0),
            cv.Optional("battery_level"): sensor.sensor_schema(unit_of_measurement="%", accuracy_decimals=0),
            cv.Optional("range"): sensor.sensor_schema(unit_of_measurement="mi", device_class="distance", accuracy_decimals=0), 
            cv.Optional("range_rated_api"): sensor.sensor_schema(unit_of_measurement="km", accuracy_decimals=1),
            cv.Optional("inside_temp"): sensor.sensor_schema(unit_of_measurement="°C", device_class="temperature", accuracy_decimals=1),
            cv.Optional("outside_temp"): sensor.sensor_schema(unit_of_measurement="°C", device_class="temperature", accuracy_decimals=1),
            cv.Optional("driver_temp_setting"): sensor.sensor_schema(unit_of_measurement="°C", device_class="temperature", accuracy_decimals=1),
            cv.Optional("passenger_temp_setting"): sensor.sensor_schema(unit_of_measurement="°C", device_class="temperature", accuracy_decimals=1),
            cv.Optional("odometer"): sensor.sensor_schema(unit_of_measurement="km", device_class="distance", accuracy_decimals=1),
            cv.Optional("speed"): sensor.sensor_schema(unit_of_measurement="km/h", device_class="speed", accuracy_decimals=1),
            cv.Optional("charge_energy_added"): sensor.sensor_schema(unit_of_measurement="kWh", device_class="energy", accuracy_decimals=2),
            cv.Optional("charge_rate"): sensor.sensor_schema(unit_of_measurement="km/h", accuracy_decimals=1),
            cv.Optional("charger_power"): sensor.sensor_schema(unit_of_measurement="kW", device_class="power", accuracy_decimals=0),
            cv.Optional("charger_voltage"): sensor.sensor_schema(unit_of_measurement="V", device_class="voltage", accuracy_decimals=0), 
            cv.Optional("charger_current"): sensor.sensor_schema(unit_of_measurement="A", device_class="current", accuracy_decimals=1), 
            cv.Optional("charging_rate"): sensor.sensor_schema(unit_of_measurement="mph", device_class="speed", accuracy_decimals=1),   
            cv.Optional("time_to_full_charge"): sensor.sensor_schema(unit_of_measurement="min", device_class="duration", accuracy_decimals=0),
            cv.Optional("tpms_front_left"): sensor.sensor_schema(unit_of_measurement="bar", device_class="pressure", accuracy_decimals=1),  
            cv.Optional("tpms_front_right"): sensor.sensor_schema(unit_of_measurement="bar", device_class="pressure", accuracy_decimals=1),  
            cv.Optional("tpms_rear_left"): sensor.sensor_schema(unit_of_measurement="bar", device_class="pressure", accuracy_decimals=1),   
            cv.Optional("tpms_rear_right"): sensor.sensor_schema(unit_of_measurement="bar", device_class="pressure", accuracy_decimals=1),  
            cv.Optional("locked"): binary_sensor.binary_sensor_schema(device_class="lock"),
            cv.Optional("user_present"): binary_sensor.binary_sensor_schema(device_class="presence"),
            cv.Optional("charge_flap_open"): binary_sensor.binary_sensor_schema(device_class="opening"),
            cv.Optional("asleep"): binary_sensor.binary_sensor_schema(),
            cv.Optional("charging"): binary_sensor.binary_sensor_schema(device_class="battery_charging"),
            # Additional binary sensors (auto-created but internal, allow user override)
            cv.Optional("parking_brake"): binary_sensor.binary_sensor_schema(device_class="problem"),
            cv.Optional("door_driver_front"): binary_sensor.binary_sensor_schema(device_class="door"),
            cv.Optional("door_driver_rear"): binary_sensor.binary_sensor_schema(device_class="door"),
            cv.Optional("door_passenger_front"): binary_sensor.binary_sensor_schema(device_class="door"),
            cv.Optional("door_passenger_rear"): binary_sensor.binary_sensor_schema(device_class="door"),
            cv.Optional("window_driver_front"): binary_sensor.binary_sensor_schema(device_class="window"),
            cv.Optional("window_driver_rear"): binary_sensor.binary_sensor_schema(device_class="window"),
            cv.Optional("window_passenger_front"): binary_sensor.binary_sensor_schema(device_class="window"),
            cv.Optional("window_passenger_rear"): binary_sensor.binary_sensor_schema(device_class="window"),
            # Switches (auto-created but internal, allow user override)
            cv.Optional("charging_switch"): switch.switch_schema(TeslaChargingSwitch, icon="mdi:ev-station"),
            cv.Optional("steering_wheel_heat_switch"): switch.switch_schema(TeslaSteeringWheelHeatSwitch, icon="mdi:steering"),
            # Numbers (auto-created but internal, allow user override)
            cv.Optional("charging_amps"): number.number_schema(TeslaChargingAmpsNumber, icon="mdi:current-ac"),
            # Locks (auto-created but internal, allow user override)
            cv.Optional("doors_lock"): lock.lock_schema(TeslaDoorsLock, icon="mdi:car-door-lock"),
            cv.Optional("charge_port_latch_lock"): lock.lock_schema(TeslaChargePortLatchLock, icon="mdi:ev-plug-tesla"),
            # Covers (auto-created but internal, allow user override)
            cv.Optional("frunk_cover"): cover.cover_schema(TeslaFrunkCover, icon="mdi:car", device_class="door"),
            cv.Optional("trunk_cover"): cover.cover_schema(TeslaTrunkCover, icon="mdi:car-back", device_class="door"),
            cv.Optional("windows_cover"): cover.cover_schema(TeslaWindowsCover, icon="mdi:car-door", device_class="awning"),
            cv.Optional("charge_port_door_cover"): cover.cover_schema(TeslaChargePortDoorCover, icon="mdi:ev-plug-tesla", device_class="door"),
            cv.Optional("shift_state"): text_sensor.text_sensor_schema(),
            cv.Optional("charging_state"): text_sensor.text_sensor_schema(),
            cv.Optional("iec61851_state"): text_sensor.text_sensor_schema(),
        },
    )
    .extend(cv.polling_component_schema("10s"))
    .extend(ble_client.BLE_CLIENT_SCHEMA)
)

def get_device_class_const(component_module, device_class_str):
    if device_class_str is None:
        return None
    return getattr(component_module, f"DEVICE_CLASS_{device_class_str.upper()}", None)

async def create_binary_sensor(var, definition, user_config=None):
    if user_config:
        bs = await binary_sensor.new_binary_sensor(user_config)
    else:
        config = {
            CONF_ID: cv.declare_id(binary_sensor.BinarySensor)(f"tesla_{definition['id']}_sensor"),
            CONF_NAME: definition["name"],
            CONF_DISABLED_BY_DEFAULT: definition.get("disabled_by_default", False),
        }
        if "icon" in definition: config[CONF_ICON] = definition["icon"]
        if "device_class" in definition:
            dc = get_device_class_const(binary_sensor, definition["device_class"])
            if dc: config[CONF_DEVICE_CLASS] = dc
        if definition.get("internal"):
            config[CONF_INTERNAL] = True
        bs = await binary_sensor.new_binary_sensor(config)
    cg.add(var.set_binary_sensor(definition["id"], bs))
    return bs

async def create_sensor(var, definition, user_config=None):
    if user_config:
        sens = await sensor.new_sensor(user_config)
    else:
        config = {
            CONF_ID: cv.declare_id(sensor.Sensor)(f"tesla_{definition['id']}_sensor"),
            CONF_NAME: definition["name"],
            CONF_DISABLED_BY_DEFAULT: definition.get("disabled_by_default", False),
            CONF_FORCE_UPDATE: False,
        }
        if "icon" in definition: config[CONF_ICON] = definition["icon"]
        if "unit" in definition: config[CONF_UNIT_OF_MEASUREMENT] = definition["unit"]
        if "accuracy_decimals" in definition: config[CONF_ACCURACY_DECIMALS] = definition["accuracy_decimals"]
        if "device_class" in definition:
            dc = get_device_class_const(sensor, definition["device_class"])
            if dc: config[CONF_DEVICE_CLASS] = dc
        if definition.get("internal"):
            config[CONF_INTERNAL] = True
        sens = await sensor.new_sensor(config)
    cg.add(var.set_sensor(definition["id"], sens))
    return sens

async def create_text_sensor(var, definition, user_config=None):
    if user_config:
        ts = await text_sensor.new_text_sensor(user_config)
    else:
        config = {
            CONF_ID: cv.declare_id(text_sensor.TextSensor)(f"tesla_{definition['id']}_sensor"),
            CONF_NAME: definition["name"],
            CONF_DISABLED_BY_DEFAULT: definition.get("disabled_by_default", False),
            CONF_FORCE_UPDATE: False,
        }
        if "icon" in definition: config[CONF_ICON] = definition["icon"]
        if definition.get("internal"):
            config[CONF_INTERNAL] = True
        ts = await text_sensor.new_text_sensor(config)
    cg.add(var.set_text_sensor(definition["id"], ts))
    return ts

async def create_button(var, definition):
    config = {
        CONF_ID: cv.declare_id(definition["class"])(f"tesla_{definition['id']}_button"),
        CONF_NAME: definition["name"],
        CONF_DISABLED_BY_DEFAULT: definition.get("disabled_by_default", False),
    }
    if "icon" in definition: config[CONF_ICON] = definition["icon"]
    if "entity_category" in definition:
        if definition["entity_category"] == "diagnostic":
            config[CONF_ENTITY_CATEGORY] = cg.EntityCategory.ENTITY_CATEGORY_DIAGNOSTIC
    if definition.get("internal"):
        config[CONF_INTERNAL] = True
    btn = await button.new_button(config)
    cg.add(btn.set_parent(var))
    if definition.get("setter"):
        cg.add(getattr(var, definition["setter"])(btn))
    return btn

async def create_switch(var, definition):
    config = {
        CONF_ID: cv.declare_id(definition["class"])(f"tesla_{definition['id']}_switch"),
        CONF_NAME: definition["name"],
        CONF_DISABLED_BY_DEFAULT: definition.get("disabled_by_default", False),
        CONF_RESTORE_MODE: switch.RESTORE_MODES['RESTORE_DEFAULT_OFF'],
    }
    if "icon" in definition: config[CONF_ICON] = definition["icon"]
    if definition.get("internal"):
        config[CONF_INTERNAL] = True
    sw = await switch.new_switch(config)
    cg.add(sw.set_parent(var))
    if definition.get("setter"):
        cg.add(getattr(var, definition["setter"])(sw))
    return sw

async def create_number(var, definition, config):
    max_val = definition["max"]
    if max_val == "config": max_val = config.get(CONF_CHARGING_AMPS_MAX, 32)
    num_config = {
        CONF_ID: cv.declare_id(definition["class"])(f"tesla_{definition['id']}_number"),
        CONF_NAME: definition["name"],
        CONF_DISABLED_BY_DEFAULT: definition.get("disabled_by_default", False),
        CONF_MODE: number.NUMBER_MODES['AUTO'],
    }
    if "icon" in definition: num_config[CONF_ICON] = definition["icon"]
    if "unit" in definition: num_config[CONF_UNIT_OF_MEASUREMENT] = definition["unit"]
    if definition.get("internal"):
        num_config[CONF_INTERNAL] = True
    num = await number.new_number(num_config, min_value=definition["min"], max_value=max_val, step=definition["step"])
    cg.add(num.set_parent(var))
    if definition.get("setter"): cg.add(getattr(var, definition["setter"])(num))
    return num

async def create_lock(var, definition):
    config = {
        CONF_ID: cv.declare_id(definition["class"])(f"tesla_{definition['id']}_lock"),
        CONF_NAME: definition["name"],
        CONF_DISABLED_BY_DEFAULT: definition.get("disabled_by_default", False),
    }
    if "icon" in definition: config[CONF_ICON] = definition["icon"]
    if definition.get("internal"):
        config[CONF_INTERNAL] = True
    lck = cg.new_Pvariable(config[CONF_ID])
    await lock.register_lock(lck, config)
    cg.add(lck.set_parent(var))
    if definition.get("setter"): cg.add(getattr(var, definition["setter"])(lck))
    return lck

async def create_cover(var, definition):
    config = {
        CONF_ID: cv.declare_id(definition["class"])(f"tesla_{definition['id']}_cover"),
        CONF_NAME: definition["name"],
        CONF_DISABLED_BY_DEFAULT: definition.get("disabled_by_default", False),
    }
    if "icon" in definition: config[CONF_ICON] = definition["icon"]
    if "device_class" in definition: config[CONF_DEVICE_CLASS] = definition["device_class"]
    if definition.get("internal"):
        config[CONF_INTERNAL] = True
    cvr = cg.new_Pvariable(config[CONF_ID])
    await cover.register_cover(cvr, config)
    cg.add(cvr.set_parent(var))
    if definition.get("setter"): cg.add(getattr(var, definition["setter"])(cvr))
    return cvr

async def create_climate_entity(var, definition):
    from esphome.components.climate import CONF_VISUAL
    config = {
        CONF_ID: cv.declare_id(definition["class"])(f"tesla_{definition['id']}_climate"),
        CONF_NAME: definition["name"],
        CONF_DISABLED_BY_DEFAULT: False,
        CONF_VISUAL: {},
        CONF_ACCURACY_DECIMALS: 1,
    }
    if definition.get("internal"):
        config[CONF_INTERNAL] = True
    clm = cg.new_Pvariable(config[CONF_ID])
    await climate.register_climate(clm, config)
    cg.add(clm.set_parent(var))
    if definition.get("setter"): cg.add(getattr(var, definition["setter"])(clm))
    return clm

# Map: YAML config key -> internal auto-created entity id to skip when user provides the key.
# None means no auto-entity to skip (purely user-defined; e.g. "locked" has no auto version).
SENSOR_OVERRIDES = {
    "battery_level": "battery_level",
    "range": "range",
    "range_rated_api": "range_rated_api",
    "inside_temp": "inside_temp",
    "outside_temp": "outside_temp",
    "driver_temp_setting": "driver_temp_setting",
    "passenger_temp_setting": "passenger_temp_setting",
    "odometer": "odometer",
    "speed": "speed",
    "charge_energy_added": "charge_energy_added",
    "charge_rate": "charge_rate",
    "charger_power": "charger_power",
    "charger_voltage": "charger_voltage",
    "charger_current": "charger_current",
    "charging_rate": "charging_rate",
    "time_to_full_charge": "time_to_full_charge",
    "tpms_front_left": "tpms_front_left",
    "tpms_front_right": "tpms_front_right",
    "tpms_rear_left": "tpms_rear_left",
    "tpms_rear_right": "tpms_rear_right",
}

BINARY_SENSOR_OVERRIDES = {
    "locked": None,                # Purely user-defined
    "user_present": "user_present",
    "charge_flap_open": None,      # Purely user-defined
    "asleep": "asleep",
    "charging": "charger",         # "charging" user key overrides "charger" auto entity
    "parking_brake": "parking_brake",
    "door_driver_front": "door_driver_front",
    "door_driver_rear": "door_driver_rear",
    "door_passenger_front": "door_passenger_front",
    "door_passenger_rear": "door_passenger_rear",
    "window_driver_front": "window_driver_front",
    "window_driver_rear": "window_driver_rear",
    "window_passenger_front": "window_passenger_front",
    "window_passenger_rear": "window_passenger_rear",
}

TEXT_SENSOR_OVERRIDES = {
    "shift_state": "shift_state",
    "charging_state": "charging_state",
    "iec61851_state": "iec61851_state",
}

# Switches that the user can override; key is the user-config key, value is the auto id to skip.
SWITCH_OVERRIDES = {
    "charging_switch": "charging",
    "steering_wheel_heat_switch": "steering_wheel_heat",
}

NUMBER_OVERRIDES = {
    "charging_amps": "charging_amps",
}

LOCK_OVERRIDES = {
    "doors_lock": "doors",
    "charge_port_latch_lock": "charge_port_latch",
}

COVER_OVERRIDES = {
    "frunk_cover": "frunk",
    "trunk_cover": "trunk",
    "windows_cover": "windows",
    "charge_port_door_cover": "charge_port_door",
}


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await ble_client.register_ble_node(var, config)

    cg.add(var.set_vin(config[CONF_VIN]))
    cg.add(var.set_role(TESLA_ROLES[config[CONF_ROLE]]))
    cg.add(var.set_charging_amps_max(config[CONF_CHARGING_AMPS_MAX]))

    vcsec_ms = int(config[CONF_VCSEC_POLL_INTERVAL] * 1000)
    cg.add(var.set_update_interval(vcsec_ms))
    cg.add(var.set_vcsec_poll_interval(vcsec_ms))
    cg.add(var.set_infotainment_poll_interval_awake(int(config[CONF_INFOTAINMENT_POLL_INTERVAL_AWAKE] * 1000)))
    cg.add(var.set_infotainment_poll_interval_active(int(config[CONF_INFOTAINMENT_POLL_INTERVAL_ACTIVE] * 1000)))
    cg.add(var.set_infotainment_sleep_timeout(int(config[CONF_INFOTAINMENT_SLEEP_TIMEOUT] * 1000)))

    # Compute skip sets: which auto entities to skip because user provided a custom one.
    skip_binary = {auto_id for user_key, auto_id in BINARY_SENSOR_OVERRIDES.items()
                   if auto_id is not None and user_key in config}
    skip_sensor = {auto_id for user_key, auto_id in SENSOR_OVERRIDES.items() if user_key in config}
    skip_text = {auto_id for user_key, auto_id in TEXT_SENSOR_OVERRIDES.items() if user_key in config}
    skip_switch = {auto_id for user_key, auto_id in SWITCH_OVERRIDES.items() if user_key in config}
    skip_number = {auto_id for user_key, auto_id in NUMBER_OVERRIDES.items() if user_key in config}
    skip_lock = {auto_id for user_key, auto_id in LOCK_OVERRIDES.items() if user_key in config}
    skip_cover = {auto_id for user_key, auto_id in COVER_OVERRIDES.items() if user_key in config}

    # Auto-create default entities (skipped if user has provided an override)
    for definition in BINARY_SENSORS:
        if definition["id"] not in skip_binary:
            await create_binary_sensor(var, definition)
    for definition in SENSORS:
        if definition["id"] not in skip_sensor:
            await create_sensor(var, definition)
    for definition in TEXT_SENSORS:
        if definition["id"] not in skip_text:
            await create_text_sensor(var, definition)
    for definition in BUTTONS:
        await create_button(var, definition)
    for definition in SWITCHES:
        if definition["id"] not in skip_switch:
            await create_switch(var, definition)
    for definition in NUMBERS:
        if definition["id"] not in skip_number:
            await create_number(var, definition, config)
    for definition in LOCKS:
        if definition["id"] not in skip_lock:
            await create_lock(var, definition)
    for definition in COVERS:
        if definition["id"] not in skip_cover:
            await create_cover(var, definition)
    await create_climate_entity(var, CLIMATE)

    # User-provided overrides for sensor/binary/text
    for user_key, auto_id in SENSOR_OVERRIDES.items():
        if user_key in config:
            await create_sensor(var, {"id": auto_id}, user_config=config[user_key])
    for user_key, auto_id in BINARY_SENSOR_OVERRIDES.items():
        if user_key in config:
            await create_binary_sensor(var, {"id": user_key}, user_config=config[user_key])
    for user_key, auto_id in TEXT_SENSOR_OVERRIDES.items():
        if user_key in config:
            await create_text_sensor(var, {"id": user_key}, user_config=config[user_key])

    # User-provided switches
    if "charging_switch" in config:
        sw = await switch.new_switch(config["charging_switch"])
        cg.add(sw.set_parent(var))
        cg.add(var.set_charging_switch(sw))
    if "steering_wheel_heat_switch" in config:
        sw = await switch.new_switch(config["steering_wheel_heat_switch"])
        cg.add(sw.set_parent(var))
        cg.add(var.set_steering_wheel_heat_switch(sw))

    # User-provided numbers
    if "charging_amps" in config:
        num = await number.new_number(
            config["charging_amps"],
            min_value=0,
            max_value=config[CONF_CHARGING_AMPS_MAX],
            step=1,
        )
        cg.add(num.set_parent(var))
        cg.add(var.set_charging_amps_number(num))

    # User-provided locks
    for user_key, setter in (("doors_lock", "set_doors_lock"), ("charge_port_latch_lock", "set_charge_port_latch_lock")):
        if user_key in config:
            lck = cg.new_Pvariable(config[user_key][CONF_ID])
            await lock.register_lock(lck, config[user_key])
            cg.add(lck.set_parent(var))
            cg.add(getattr(var, setter)(lck))

    # User-provided covers
    cover_setter_map = {
        "frunk_cover": "set_frunk_cover",
        "trunk_cover": "set_trunk_cover",
        "windows_cover": "set_windows_cover",
        "charge_port_door_cover": "set_charge_port_door_cover",
    }
    for user_key, setter in cover_setter_map.items():
        if user_key in config:
            cvr = cg.new_Pvariable(config[user_key][CONF_ID])
            await cover.register_cover(cvr, config[user_key])
            cg.add(cvr.set_parent(var))
            cg.add(getattr(var, setter)(cvr))

# Base schema for all Tesla vehicle actions: requires a TeslaBLEVehicle reference
TESLA_VEHICLE_BASE_ACTION_SCHEMA = cv.Schema({cv.Required(CONF_ID): cv.use_id(TeslaBLEVehicle)})
# Concrete schemas - most are identical to base; parametrized schemas are defined separately
TESLA_WAKE_ACTION_SCHEMA = TESLA_VEHICLE_BASE_ACTION_SCHEMA
TESLA_PAIR_ACTION_SCHEMA = TESLA_VEHICLE_BASE_ACTION_SCHEMA
TESLA_REGENERATE_KEY_ACTION_SCHEMA = TESLA_VEHICLE_BASE_ACTION_SCHEMA
TESLA_FORCE_UPDATE_ACTION_SCHEMA = TESLA_VEHICLE_BASE_ACTION_SCHEMA
TESLA_START_DRIVING_ACTION_SCHEMA = TESLA_VEHICLE_BASE_ACTION_SCHEMA
TESLA_SET_CHARGING_ACTION_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.use_id(TeslaBLEVehicle),
    cv.Required("state"): cv.templatable(cv.boolean),
})
TESLA_SET_CHARGING_AMPS_ACTION_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.use_id(TeslaBLEVehicle),
    cv.Required("amps"): cv.templatable(cv.int_range(min=MIN_CHARGING_AMPS, max=MAX_CHARGING_AMPS)),
})
TESLA_SET_CHARGING_LIMIT_ACTION_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.use_id(TeslaBLEVehicle),
    cv.Required("limit"): cv.templatable(cv.int_range(min=MIN_CHARGING_LIMIT, max=MAX_CHARGING_LIMIT)),
})


# Helper: builds a simple action Pvariable that only forwards a TeslaBLEVehicle reference.
# Use for actions that don't need any extra parameters (e.g. wake, pair, regenerate_key).
async def _simple_vehicle_action(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, template_arg, paren)


@automation.register_action("tesla_ble_vehicle.wake", WakeAction, TESLA_WAKE_ACTION_SCHEMA, synchronous=False)
async def tesla_wake_to_code(config, action_id, template_arg, args):
    return await _simple_vehicle_action(config, action_id, template_arg, args)

@automation.register_action("tesla_ble_vehicle.pair", PairAction, TESLA_PAIR_ACTION_SCHEMA, synchronous=False)
async def tesla_pair_to_code(config, action_id, template_arg, args):
    return await _simple_vehicle_action(config, action_id, template_arg, args)

@automation.register_action("tesla_ble_vehicle.regenerate_key", RegenerateKeyAction, TESLA_REGENERATE_KEY_ACTION_SCHEMA, synchronous=False)
async def tesla_regenerate_key_to_code(config, action_id, template_arg, args):
    return await _simple_vehicle_action(config, action_id, template_arg, args)

@automation.register_action("tesla_ble_vehicle.force_update", ForceUpdateAction, TESLA_FORCE_UPDATE_ACTION_SCHEMA, synchronous=False)
async def tesla_force_update_to_code(config, action_id, template_arg, args):
    return await _simple_vehicle_action(config, action_id, template_arg, args)

@automation.register_action("tesla_ble_vehicle.set_charging", SetChargingAction, TESLA_SET_CHARGING_ACTION_SCHEMA, synchronous=False)
async def tesla_set_charging_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    template_ = await cg.templatable(config["state"], args, bool)
    cg.add(var.set_state(template_))
    return var

@automation.register_action("tesla_ble_vehicle.set_charging_amps", SetChargingAmpsAction, TESLA_SET_CHARGING_AMPS_ACTION_SCHEMA, synchronous=False)
async def tesla_set_charging_amps_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    template_ = await cg.templatable(config["amps"], args, int)
    cg.add(var.set_amps(template_))
    return var

@automation.register_action("tesla_ble_vehicle.set_charging_limit", SetChargingLimitAction, TESLA_SET_CHARGING_LIMIT_ACTION_SCHEMA, synchronous=False)
async def tesla_set_charging_limit_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    template_ = await cg.templatable(config["limit"], args, int)
    cg.add(var.set_limit(template_))
    return var

@automation.register_action(
    "tesla_ble_vehicle.start_driving",
    StartDrivingAction,
    TESLA_START_DRIVING_ACTION_SCHEMA,
    synchronous=False,
)
async def tesla_start_driving_to_code(config, action_id, template_arg, args):
    return await _simple_vehicle_action(config, action_id, template_arg, args)
