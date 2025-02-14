"""The HomeKit Device Aggregator integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_NAME,
    Platform,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
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
    CONF_TEMP_SENSOR,
    CONF_TARGET_TEMP,
    CONF_CURRENT_TEMP,
    CONF_STATUS_SENSOR,
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

    # Register the device with HomeKit
    device_type = entry.data[CONF_DEVICE_TYPE]
    if device_type == "kettle":
        await setup_kettle(hass, entry)
    # Add more device types here...

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, [Platform.HOMEKIT]):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def setup_kettle(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a kettle device."""
    from homeassistant.components.homekit.const import (
        ATTR_VALUE,
        CONF_FEATURE_LIST,
        CONF_LINKED_BATTERY_SENSOR,
        CONF_LOW_BATTERY_THRESHOLD,
        DOMAIN as HOMEKIT_DOMAIN,
        FEATURE_ON_OFF,
        FEATURE_TEMPERATURE_CONTROL,
        TYPE_KETTLE,
    )

    # Create the HomeKit accessory configuration
    accessory_config = {
        CONF_NAME: entry.data[CONF_NAME],
        "entity_id": entry.data[CONF_POWER_SWITCH],
        CONF_FEATURE_LIST: [
            FEATURE_ON_OFF,
            FEATURE_TEMPERATURE_CONTROL,
        ],
        "temperature_sensor_entity_id": entry.data[CONF_CURRENT_TEMP],
        "target_temperature_entity_id": entry.data[CONF_TARGET_TEMP],
    }

    if CONF_STATUS_SENSOR in entry.data:
        accessory_config["status_entity_id"] = entry.data[CONF_STATUS_SENSOR]

    # Create a unique identifier for the device
    unique_id = f"{DOMAIN}_{entry.entry_id}"

    # Register the device with HomeKit
    hass.async_create_task(
        hass.services.async_call(
            HOMEKIT_DOMAIN,
            "add_accessory",
            {
                "name": entry.data[CONF_NAME],
                "entity_id": entry.data[CONF_POWER_SWITCH],
                "category": TYPE_KETTLE,
                "config": accessory_config,
            },
        )
    )

    # Set up state change listeners
    @callback
    async def async_handle_state_change(entity_id: str, old_state: str, new_state: str) -> None:
        """Handle state changes for the kettle's entities."""
        if not new_state:
            return

        if entity_id == entry.data[CONF_POWER_SWITCH]:
            # Update HomeKit power state
            await hass.services.async_call(
                HOMEKIT_DOMAIN,
                "change_state",
                {
                    "entity_id": unique_id,
                    "characteristic": "on",
                    ATTR_VALUE: new_state.state == "on",
                },
            )
        elif entity_id == entry.data[CONF_CURRENT_TEMP]:
            # Update HomeKit temperature
            try:
                temp = float(new_state.state)
                await hass.services.async_call(
                    HOMEKIT_DOMAIN,
                    "change_state",
                    {
                        "entity_id": unique_id,
                        "characteristic": "current-temperature",
                        ATTR_VALUE: temp,
                    },
                )
            except ValueError:
                _LOGGER.warning("Invalid temperature value: %s", new_state.state)

    # Register state change listeners
    for entity_id in [
        entry.data[CONF_POWER_SWITCH],
        entry.data[CONF_CURRENT_TEMP],
        entry.data[CONF_TARGET_TEMP],
    ]:
        hass.helpers.event.async_track_state_change(
            entity_id,
            async_handle_state_change,
        )
