"""The HomeKit Device Aggregator integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_NAME,
    CONF_NAME,
    Platform,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import Entity
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
    CATEGORY_KETTLE,
    CATEGORY_THERMOSTAT,
    CATEGORY_FAN,
    CATEGORY_LIGHTBULB,
    CATEGORY_HUMIDIFIER,
    CATEGORY_AIR_PURIFIER,
    CATEGORY_GARAGE_DOOR,
    CATEGORY_SECURITY_SYSTEM,
    CHAR_ON,
    CHAR_ACTIVE,
    CHAR_CURRENT_TEMP,
    CHAR_TARGET_TEMP,
    CHAR_CURRENT_STATE,
    CHAR_TARGET_STATE,
    CHAR_FAULT,
    CHAR_REMAINING_TIME,
)

_LOGGER = logging.getLogger(__name__)

HOMEKIT_BRIDGE_DOMAIN = "homekit"

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
        ATTR_NAME: entry.data[CONF_NAME],
        ATTR_ENTITY_ID: entry.data[CONF_POWER_SWITCH],
        "category": CATEGORY_KETTLE,
        "features": [
            {
                "type": CHAR_ON,
                "entity_id": entry.data[CONF_POWER_SWITCH],
            },
            {
                "type": CHAR_CURRENT_TEMP,
                "entity_id": entry.data[CONF_CURRENT_TEMP],
            },
            {
                "type": CHAR_TARGET_TEMP,
                "entity_id": entry.data[CONF_TARGET_TEMP],
            },
            {
                "type": CHAR_REMAINING_TIME,
                "entity_id": entry.data[CONF_COUNTDOWN],
            },
            {
                "type": CHAR_FAULT,
                "entity_id": entry.data[CONF_FAULT],
            },
            {
                "type": CHAR_ACTIVE,
                "entity_id": entry.data[CONF_KEEP_WARM],
            },
        ],
    }

    await register_homekit_device(hass, entry, accessory_config)

async def setup_thermostat(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a thermostat device."""
    accessory_config = {
        ATTR_NAME: entry.data[CONF_NAME],
        ATTR_ENTITY_ID: entry.data[CONF_POWER_SWITCH],
        "category": CATEGORY_THERMOSTAT,
        "features": [
            {
                "type": CHAR_ON,
                "entity_id": entry.data[CONF_POWER_SWITCH],
            },
            {
                "type": CHAR_CURRENT_TEMP,
                "entity_id": entry.data[CONF_CURRENT_TEMP],
            },
            {
                "type": CHAR_TARGET_TEMP,
                "entity_id": entry.data[CONF_TARGET_TEMP],
            },
        ],
    }

    await register_homekit_device(hass, entry, accessory_config)

async def setup_fan(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a fan device."""
    accessory_config = {
        ATTR_NAME: entry.data[CONF_NAME],
        ATTR_ENTITY_ID: entry.data[CONF_POWER_SWITCH],
        "category": CATEGORY_FAN,
        "features": [
            {
                "type": CHAR_ON,
                "entity_id": entry.data[CONF_POWER_SWITCH],
            },
        ],
    }

    await register_homekit_device(hass, entry, accessory_config)

async def setup_light(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a light device."""
    accessory_config = {
        ATTR_NAME: entry.data[CONF_NAME],
        ATTR_ENTITY_ID: entry.data[CONF_POWER_SWITCH],
        "category": CATEGORY_LIGHTBULB,
        "features": [
            {
                "type": CHAR_ON,
                "entity_id": entry.data[CONF_POWER_SWITCH],
            },
        ],
    }

    await register_homekit_device(hass, entry, accessory_config)

async def setup_humidifier(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a humidifier device."""
    accessory_config = {
        ATTR_NAME: entry.data[CONF_NAME],
        ATTR_ENTITY_ID: entry.data[CONF_POWER_SWITCH],
        "category": CATEGORY_HUMIDIFIER,
        "features": [
            {
                "type": CHAR_ON,
                "entity_id": entry.data[CONF_POWER_SWITCH],
            },
        ],
    }

    await register_homekit_device(hass, entry, accessory_config)

async def setup_air_purifier(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up an air purifier device."""
    accessory_config = {
        ATTR_NAME: entry.data[CONF_NAME],
        ATTR_ENTITY_ID: entry.data[CONF_POWER_SWITCH],
        "category": CATEGORY_AIR_PURIFIER,
        "features": [
            {
                "type": CHAR_ON,
                "entity_id": entry.data[CONF_POWER_SWITCH],
            },
        ],
    }

    await register_homekit_device(hass, entry, accessory_config)

async def setup_garage_door(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a garage door device."""
    accessory_config = {
        ATTR_NAME: entry.data[CONF_NAME],
        ATTR_ENTITY_ID: entry.data[CONF_POWER_SWITCH],
        "category": CATEGORY_GARAGE_DOOR,
        "features": [
            {
                "type": CHAR_ON,
                "entity_id": entry.data[CONF_POWER_SWITCH],
            },
        ],
    }

    await register_homekit_device(hass, entry, accessory_config)

async def setup_security_system(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a security system device."""
    accessory_config = {
        ATTR_NAME: entry.data[CONF_NAME],
        ATTR_ENTITY_ID: entry.data[CONF_ALARM_STATE],
        "category": CATEGORY_SECURITY_SYSTEM,
        "features": [
            {
                "type": CHAR_CURRENT_STATE,
                "entity_id": entry.data[CONF_ALARM_STATE],
            },
        ],
    }

    await register_homekit_device(hass, entry, accessory_config)

async def register_homekit_device(hass: HomeAssistant, entry: ConfigEntry, config: dict) -> None:
    """Register a device with HomeKit."""
    # Create a unique identifier for the device
    unique_id = f"{DOMAIN}_{entry.entry_id}"

    # Register the device with HomeKit Bridge
    await hass.services.async_call(
        HOMEKIT_BRIDGE_DOMAIN,
        "add_accessory",
        {
            "name": config[ATTR_NAME],
            "entity_id": config[ATTR_ENTITY_ID],
            "category": config["category"],
            "config": config,
        },
    )

    # Set up state change listeners for all relevant entities
    entities_to_track = []
    for feature in config.get("features", []):
        if "entity_id" in feature:
            entities_to_track.append(feature["entity_id"])

    @callback
    async def async_handle_state_change(entity_id: str, old_state: str, new_state: str) -> None:
        """Handle state changes for the device's entities."""
        if not new_state:
            return

        # Find the feature that corresponds to this entity
        feature = next(
            (f for f in config.get("features", []) if f.get("entity_id") == entity_id),
            None,
        )
        if not feature:
            return

        # Map the state to the appropriate HomeKit characteristic
        value = new_state.state
        if feature["type"] == CHAR_ON:
            value = new_state.state == STATE_ON
        elif feature["type"] in [CHAR_CURRENT_TEMP, CHAR_TARGET_TEMP]:
            try:
                value = float(new_state.state)
            except ValueError:
                _LOGGER.warning("Invalid temperature value: %s", new_state.state)
                return

        # Update the HomeKit characteristic
        await hass.services.async_call(
            HOMEKIT_BRIDGE_DOMAIN,
            "change_state",
            {
                "entity_id": unique_id,
                "characteristic": feature["type"],
                "value": value,
            },
        )

    # Register state change listeners
    for entity_id in entities_to_track:
        if entity_id:  # Only register if entity is configured
            hass.helpers.event.async_track_state_change(
                entity_id,
                async_handle_state_change,
            )
