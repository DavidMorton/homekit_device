"""Constants for the HomeKit Device Aggregator integration."""
DOMAIN = "homekit_device"
CONF_ENTITIES = "entities"
CONF_NAME = "name"
CONF_DEVICE_TYPE = "device_type"

# Supported HomeKit device types
DEVICE_TYPES = {
    "kettle": "A smart kettle with temperature control and power state",
    "thermostat": "A thermostat with multiple temperature sensors",
    "fan": "A fan with multiple controls (speed, oscillation, etc.)",
    "light": "A light with multiple controls (brightness, colour, etc.)"
}

# Configuration keys
CONF_TEMP_SENSOR = "temperature_sensor"
CONF_POWER_SWITCH = "power_switch"
CONF_TARGET_TEMP = "target_temperature"
CONF_CURRENT_TEMP = "current_temperature"
CONF_STATUS_SENSOR = "status_sensor"

# Default values
DEFAULT_NAME = "Aggregated Device"
