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
from homeassistant.helpers import device_registry as dr, entity_registry as er
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
    CATEGORY_KETTLE,
    CATEGORY_THERMOSTAT,
    CATEGORY_FAN,
    CATEGORY_LIGHTBULB,
    CATEGORY_HUMIDIFIER,
    CATEGORY_AIR_PURIFIER,
    CATEGORY_GARAGE_DOOR,
    CATEGORY_SECURITY_SYSTEM,
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
    # Create a unique identifier for the device
    unique_id = f"{DOMAIN}_{entry.entry_id}"

    # Register the device in Home Assistant
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, unique_id)},
        name=entry.data[CONF_NAME],
        manufacturer="HomeKit Device Aggregator",
        model="Smart Kettle",
    )

    # Get the entity registry
    entity_registry = er.async_get(hass)

    # Create a list of entities to include in HomeKit
    entities_to_include = [entry.data[CONF_POWER_SWITCH]]  # Power switch is required

    # Add optional entities if they were configured
    optional_entities = [
        CONF_CURRENT_TEMP,
        CONF_TARGET_TEMP,
        CONF_COUNTDOWN,
        CONF_FAULT,
        CONF_KEEP_WARM,
        CONF_KEEP_WARM_TIME,
    ]

    for entity_key in optional_entities:
        if entity_key in entry.data and entry.data[entity_key]:
            entities_to_include.append(entry.data[entity_key])

    # Create HomeKit configuration
    homekit_config = {
        "filter": {
            "include_entities": entities_to_include
        },
        "entity_config": {
            entry.data[CONF_POWER_SWITCH]: {
                "type": "switch",
                "linked_battery_sensor": None,
                "low_battery_threshold": 20,
            }
        }
    }

    # Add entity-specific configurations
    if CONF_CURRENT_TEMP in entry.data and entry.data[CONF_CURRENT_TEMP]:
        homekit_config["entity_config"][entry.data[CONF_CURRENT_TEMP]] = {
            "type": "sensor",
            "device_class": "temperature"
        }

    if CONF_TARGET_TEMP in entry.data and entry.data[CONF_TARGET_TEMP]:
        homekit_config["entity_config"][entry.data[CONF_TARGET_TEMP]] = {
            "type": "number",
            "device_class": "temperature"
        }

    # Update HomeKit configuration
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(
            entry, "homekit"
        )
    )

    # Set up state change listeners for all relevant entities
    @callback
    async def async_handle_state_change(entity_id: str, old_state: str, new_state: str) -> None:
        """Handle state changes for the device's entities."""
        if not new_state:
            return

        # Update the entity's state in Home Assistant
        await hass.states.async_set(
            entity_id,
            new_state.state,
            new_state.attributes
        )

    # Register state change listeners
    for entity_id in entities_to_include:
        if entity_id:  # Only register if entity is configured
            hass.helpers.event.async_track_state_change(
                entity_id,
                async_handle_state_change,
            )

# Other device setup functions would be similar, but with device-specific configurations
async def setup_thermostat(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a thermostat device."""
    _LOGGER.info("Thermostat setup not yet implemented")

async def setup_fan(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a fan device."""
    _LOGGER.info("Fan setup not yet implemented")

async def setup_light(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a light device."""
    _LOGGER.info("Light setup not yet implemented")

async def setup_humidifier(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a humidifier device."""
    _LOGGER.info("Humidifier setup not yet implemented")

async def setup_air_purifier(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up an air purifier device."""
    _LOGGER.info("Air purifier setup not yet implemented")

async def setup_garage_door(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a garage door device."""
    _LOGGER.info("Garage door setup not yet implemented")

async def setup_security_system(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a security system device."""
    _LOGGER.info("Security system setup not yet implemented")
