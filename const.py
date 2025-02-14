"""Constants for the HomeKit Device Aggregator integration."""
DOMAIN = "homekit_device"
CONF_ENTITIES = "entities"
CONF_NAME = "name"
CONF_DEVICE_TYPE = "device_type"

# HomeKit Accessory Categories
CATEGORY_KETTLE = 27  # HomeKit category for kettles
CATEGORY_THERMOSTAT = 9
CATEGORY_FAN = 3
CATEGORY_LIGHTBULB = 5
CATEGORY_HUMIDIFIER = 29
CATEGORY_AIR_PURIFIER = 28
CATEGORY_GARAGE_DOOR = 4
CATEGORY_SECURITY_SYSTEM = 7

# HomeKit Features and Characteristics
CHAR_ON = "on"
CHAR_ACTIVE = "active"
CHAR_CURRENT_TEMP = "current-temperature"
CHAR_TARGET_TEMP = "target-temperature"
CHAR_CURRENT_STATE = "current-state"
CHAR_TARGET_STATE = "target-state"
CHAR_FAULT = "status-fault"
CHAR_REMAINING_TIME = "remaining-duration"

# Device Features
FEATURE_ON_OFF = "on_off"
FEATURE_TEMPERATURE = "temperature"
FEATURE_TIMER = "timer"
FEATURE_STATUS = "status"
FEATURE_KEEP_WARM = "keep_warm"

# Supported HomeKit device types
DEVICE_TYPES = {
    "kettle": "A smart kettle with temperature control and power state",
    "thermostat": "A thermostat with multiple temperature sensors",
    "fan": "A fan with multiple controls (speed, oscillation, etc.)",
    "light": "A light with multiple controls (brightness, colour, etc.)",
    "humidifier": "A humidifier with humidity sensing and control",
    "air_purifier": "An air purifier with air quality monitoring",
    "garage_door": "A garage door with multiple sensors",
    "security_system": "A security system with multiple sensors and controls"
}

# Configuration keys for all device types
CONF_POWER_SWITCH = "power_switch"
CONF_STATUS_SENSOR = "status_sensor"

# Kettle specific configs
CONF_CURRENT_TEMP = "current_temperature"
CONF_TARGET_TEMP = "target_temperature"
CONF_COUNTDOWN = "countdown_timer"
CONF_FAULT = "fault_status"
CONF_KEEP_WARM = "keep_warm_mode"
CONF_KEEP_WARM_TIME = "keep_warm_idle_time"

# Temperature related configs
CONF_TEMP_SENSORS = "temperature_sensors"  # For multiple temp sensors

# Fan related configs
CONF_SPEED_CONTROL = "speed_control"
CONF_OSCILLATION = "oscillation"
CONF_DIRECTION = "direction"

# Light related configs
CONF_BRIGHTNESS = "brightness"
CONF_COLOR_TEMP = "color_temperature"
CONF_RGB_CONTROL = "rgb_control"
CONF_EFFECT_LIST = "effect_list"

# Humidifier related configs
CONF_CURRENT_HUMIDITY = "current_humidity"
CONF_TARGET_HUMIDITY = "target_humidity"
CONF_WATER_LEVEL = "water_level"

# Air purifier related configs
CONF_AIR_QUALITY = "air_quality"
CONF_FILTER_LIFE = "filter_life"
CONF_PM25 = "pm25"
CONF_VOC = "voc"

# Garage door related configs
CONF_DOOR_POSITION = "door_position"
CONF_OBSTRUCTION = "obstruction_detected"
CONF_MOTION = "motion_sensor"
CONF_LIGHT_SWITCH = "light_switch"

# Security system related configs
CONF_ALARM_STATE = "alarm_state"
CONF_SENSORS = "sensors"  # List of security sensors
CONF_SIREN = "siren"
CONF_KEYPAD = "keypad"

# Default values
DEFAULT_NAME = "Aggregated Device"
