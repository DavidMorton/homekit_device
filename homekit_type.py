"""HomeKit device type definitions."""
from homeassistant.components.homekit.const import (
    CATEGORY_KETTLE,
    CHAR_HEATING_COOLING_CURRENT,
    CHAR_HEATING_COOLING_TARGET,
    CHAR_ON,
    CHAR_TEMPERATURE_CURRENT,
    CHAR_TEMPERATURE_TARGET,
    SERV_SWITCH,
    SERV_THERMOSTAT,
)
from homeassistant.const import (
    DEVICE_CLASS_POWER,
    UnitOfTemperature,
)

KETTLE_DEVICE_TYPE = {
    "category": CATEGORY_KETTLE,
    "services": [
        {
            "name": "Kettle",
            "service": SERV_THERMOSTAT,
            "primary": True,
            "chars": [
                {
                    "name": "Current Temperature",
                    "char": CHAR_TEMPERATURE_CURRENT,
                    "unit": UnitOfTemperature.CELSIUS,
                    "device_class": "temperature",
                    "min_value": 0,
                    "max_value": 100,
                },
                {
                    "name": "Target Temperature",
                    "char": CHAR_TEMPERATURE_TARGET,
                    "unit": UnitOfTemperature.CELSIUS,
                    "min_value": 0,
                    "max_value": 100,
                    "step_value": 1,
                },
                {
                    "name": "Current Operation",
                    "char": CHAR_HEATING_COOLING_CURRENT,
                    "valid_values": [0, 1],  # 0: Off, 1: Heat
                },
                {
                    "name": "Target Operation",
                    "char": CHAR_HEATING_COOLING_TARGET,
                    "valid_values": [0, 1],  # 0: Off, 1: Heat
                },
            ],
        },
        {
            "name": "Power",
            "service": SERV_SWITCH,
            "linked": True,
            "chars": [
                {
                    "name": "Power State",
                    "char": CHAR_ON,
                    "device_class": DEVICE_CLASS_POWER,
                },
            ],
        },
    ],
}

DEVICE_TYPES = {
    "kettle": KETTLE_DEVICE_TYPE,
}

def get_device_type(device_type: str) -> dict:
    """Get the HomeKit device type configuration."""
    return DEVICE_TYPES.get(device_type, {})
