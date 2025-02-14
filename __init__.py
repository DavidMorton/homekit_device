"""The HomeKit Device Aggregator integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.homekit.const import (
    ATTR_VALUE,
    CONF_FEATURE_LIST,
    DOMAIN as HOMEKIT_DOMAIN,
    FEATURE_ON_OFF,
    FEATURE_TEMPERATURE_CONTROL,
    FEATURE_TIMER,
    FEATURE_STATUS_FAULT,
    FEATURE_STATUS_ACTIVE,
    FEATURE_ROTATION_SPEED,
    FEATURE_SWING_MODE,
    FEATURE_BRIGHTNESS,
    FEATURE_COLOR,
    TYPE_KETTLE,
    TYPE_THERMOSTAT,
    TYPE_FAN,
    TYPE_LIGHTBULB,
    TYPE_HUMIDIFIER,
    TYPE_AIR_PURIFIER,
    TYPE_GARAGE_DOOR_OPENER,
    TYPE_SECURITY_SYSTEM,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_NAME,
    Platform,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    PERCENTAGE,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_DEVICE_TYPE,
    CONF_POWER_SWITCH,
    CONF_TEMP_SENSORS,
    CONF_TARGET_TEMP,
    CONF_CURRENT_TEMP,
    CONF_STATUS_SENSOR,
    CONF_COUNTDOWN,
    CONF_FAULT,
    CONF_KEEP_WARM,
    CONF_KEEP_WARM_TIME,
    CONF_SPEED_CONTROL,
    CONF_OSCILLATION,
    CONF_DIRECTION,
    CONF_BRIGHTNESS,
    CONF_COLOR_TEMP,
    CONF_RGB_CONTROL,
    CONF_CURRENT_HUMIDITY,
    CONF_TARGET_HUMIDITY,
    CONF_WATER_LEVEL,
    CONF_AIR_QUALITY,
    CONF_FILTER_LIFE,
    CONF_PM25,
    CONF_VOC,
    CONF_DOOR_POSITION,
    CONF_OBSTRUCTION,
    CONF_MOTION,
    CONF_LIGHT_SWITCH,
    CONF_ALARM_STATE,
    CONF_SENSORS,
    CONF_SIREN,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the HomeKit Device Aggregator component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HomeKit Device Aggregator from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    device_type = entry.data[CONF_DEVICE_TYPE]
    setup_functions = {
        "kettle": setup_kettle,
        "thermostat": setup_thermostat,
        "fan": setup_fan,
        "light": setup_light,
        "humidifier": setup_humidifier,
        "air_purifier": setup_air_purifier,
        "garage_door": setup_garage_door,
        "security_system": setup_security_system,
    }

    if device_type in setup_functions:
        await setup_functions[device_type](hass, entry)
    else:
        _LOGGER.error("Unsupported device type: %s", device_type)
        return False

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, [Platform.HOMEKIT]):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def setup_kettle(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a kettle device."""
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_POWER_SWITCH],
        CONF_FEATURE_LIST: [
            FEATURE_ON_OFF,
            FEATURE_TEMPERATURE_CONTROL,
            FEATURE_TIMER,
            FEATURE_STATUS_FAULT,
            FEATURE_STATUS_ACTIVE,
        ],
        # Temperature controls
        "temperature_sensor_entity_id": entry.data[CONF_CURRENT_TEMP],
        "target_temperature_entity_id": entry.data[CONF_TARGET_TEMP],
        # Timer and status
        "timer_entity_id": entry.data[CONF_COUNTDOWN],
        "fault_entity_id": entry.data[CONF_FAULT],
        # Keep warm features
        "keep_warm_entity_id": entry.data[CONF_KEEP_WARM],
        "keep_warm_time_entity_id": entry.data[CONF_KEEP_WARM_TIME],
    }

    await register_homekit_device(hass, entry, TYPE_KETTLE, accessory_config)

async def setup_thermostat(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a thermostat device."""
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_POWER_SWITCH],
        CONF_FEATURE_LIST: [
            FEATURE_ON_OFF,
            FEATURE_TEMPERATURE_CONTROL,
        ],
        "temperature_sensor_entity_id": entry.data[CONF_CURRENT_TEMP],
        "target_temperature_entity_id": entry.data[CONF_TARGET_TEMP],
        "temperature_sensors": entry.data.get(CONF_TEMP_SENSORS, []),
    }

    await register_homekit_device(hass, entry, TYPE_THERMOSTAT, accessory_config)

async def setup_fan(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a fan device."""
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_POWER_SWITCH],
        CONF_FEATURE_LIST: [
            FEATURE_ON_OFF,
            FEATURE_ROTATION_SPEED,
            FEATURE_SWING_MODE,
        ],
        "speed_entity_id": entry.data.get(CONF_SPEED_CONTROL),
        "oscillation_entity_id": entry.data.get(CONF_OSCILLATION),
        "direction_entity_id": entry.data.get(CONF_DIRECTION),
    }

    await register_homekit_device(hass, entry, TYPE_FAN, accessory_config)

async def setup_light(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a light device."""
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_POWER_SWITCH],
        CONF_FEATURE_LIST: [
            FEATURE_ON_OFF,
            FEATURE_BRIGHTNESS,
            FEATURE_COLOR,
        ],
        "brightness_entity_id": entry.data.get(CONF_BRIGHTNESS),
        "color_temp_entity_id": entry.data.get(CONF_COLOR_TEMP),
        "rgb_entity_id": entry.data.get(CONF_RGB_CONTROL),
    }

    await register_homekit_device(hass, entry, TYPE_LIGHTBULB, accessory_config)

async def setup_humidifier(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a humidifier device."""
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_POWER_SWITCH],
        CONF_FEATURE_LIST: [FEATURE_ON_OFF],
        "current_humidity_entity_id": entry.data[CONF_CURRENT_HUMIDITY],
        "target_humidity_entity_id": entry.data[CONF_TARGET_HUMIDITY],
        "water_level_entity_id": entry.data.get(CONF_WATER_LEVEL),
    }

    await register_homekit_device(hass, entry, TYPE_HUMIDIFIER, accessory_config)

async def setup_air_purifier(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up an air purifier device."""
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_POWER_SWITCH],
        CONF_FEATURE_LIST: [FEATURE_ON_OFF],
        "air_quality_entity_id": entry.data[CONF_AIR_QUALITY],
        "filter_life_entity_id": entry.data.get(CONF_FILTER_LIFE),
        "pm25_entity_id": entry.data.get(CONF_PM25),
        "voc_entity_id": entry.data.get(CONF_VOC),
    }

    await register_homekit_device(hass, entry, TYPE_AIR_PURIFIER, accessory_config)

async def setup_garage_door(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a garage door device."""
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_POWER_SWITCH],
        CONF_FEATURE_LIST: [FEATURE_ON_OFF],
        "position_entity_id": entry.data[CONF_DOOR_POSITION],
        "obstruction_entity_id": entry.data.get(CONF_OBSTRUCTION),
        "motion_entity_id": entry.data.get(CONF_MOTION),
        "light_entity_id": entry.data.get(CONF_LIGHT_SWITCH),
    }

    await register_homekit_device(hass, entry, TYPE_GARAGE_DOOR_OPENER, accessory_config)

async def setup_security_system(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a security system device."""
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_ALARM_STATE],
        CONF_FEATURE_LIST: [FEATURE_ON_OFF],
        "sensors": entry.data.get(CONF_SENSORS, []),
        "siren_entity_id": entry.data.get(CONF_SIREN),
    }

    await register_homekit_device(hass, entry, TYPE_SECURITY_SYSTEM, accessory_config)

async def register_homekit_device(hass: HomeAssistant, entry: ConfigEntry, device_type: str, config: dict) -> None:
    """Register a device with HomeKit."""
    # Create a unique identifier for the device
    unique_id = f"{DOMAIN}_{entry.entry_id}"

    # Register the device with HomeKit
    hass.async_create_task(
        hass.services.async_call(
            HOMEKIT_DOMAIN,
            "add_accessory",
            {
                "name": config[CONF_NAME],
                "entity_id": config["entity_id"],
                "category": device_type,
                "config": config,
            },
        )
    )

    # Set up state change listeners for all relevant entities
    entities_to_track = [config["entity_id"]]
    for key, value in config.items():
        if isinstance(value, str) and key.endswith("_entity_id"):
            entities_to_track.append(value)
        elif isinstance(value, list) and key in ["sensors", "temperature_sensors"]:
            entities_to_track.extend(value)

    @callback
    async def async_handle_state_change(entity_id: str, old_state: str, new_state: str) -> None:
        """Handle state changes for the device's entities."""
        if not new_state:
            return

        # Map entity states to HomeKit characteristics based on entity type
        characteristic = None
        value = new_state.state

        if entity_id == config["entity_id"]:
            characteristic = "on"
            value = new_state.state == STATE_ON
        elif "temperature" in entity_id:
            characteristic = "current-temperature"
            try:
                value = float(new_state.state)
            except ValueError:
                _LOGGER.warning("Invalid temperature value: %s", new_state.state)
                return

        if characteristic:
            await hass.services.async_call(
                HOMEKIT_DOMAIN,
                "change_state",
                {
                    "entity_id": unique_id,
                    "characteristic": characteristic,
                    ATTR_VALUE: value,
                },
            )

    # Register state change listeners
    for entity_id in entities_to_track:
        if entity_id:  # Only register if entity is configured
            hass.helpers.event.async_track_state_change(
                entity_id,
                async_handle_state_change,
            )
