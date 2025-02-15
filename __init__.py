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
from homeassistant.components.homekit import DOMAIN as HOMEKIT_DOMAIN
from homeassistant.components.homekit.const import (
    CONF_HOMEKIT_MODE,
    HOMEKIT_MODE_ACCESSORY,
)
from homeassistant.helpers import device_registry as dr
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
)
from .accessory import HomeKitKettle

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
    if device_type == "kettle":
        await setup_kettle(hass, entry)
    else:
        _LOGGER.error("Unsupported device type: %s", device_type)
        return False

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove the device from HomeKit
    await remove_homekit_device(hass, entry)

    hass.data[DOMAIN].pop(entry.entry_id)
    return True

async def setup_kettle(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up a kettle device."""
    # Create HomeKit configuration for the kettle
    homekit_config = {
        "name": entry.data[CONF_NAME],
        "mode": HOMEKIT_MODE_ACCESSORY,
        "filter": {
            "include_entities": [
                entry.data[CONF_POWER_SWITCH],  # Required
            ]
        },
    }

    # Add optional entities if configured
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
            homekit_config["filter"]["include_entities"].append(entry.data[entity_key])

    # Register our custom accessory with HomeKit
    hass.data[HOMEKIT_DOMAIN]["accessories"][entry.entry_id] = {
        "accessory_class": HomeKitKettle,
        "config": entry.data,
    }

    # Create a HomeKit config entry for this device
    homekit_entry_data = {
        "name": entry.data[CONF_NAME],
        "port": None,  # Let HomeKit choose a port
        "mode": HOMEKIT_MODE_ACCESSORY,
        "filter": homekit_config["filter"],
        "entity_config": {},
    }

    # Create the HomeKit config entry
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            HOMEKIT_DOMAIN,
            context={"source": DOMAIN},
            data=homekit_entry_data,
        )
    )

async def remove_homekit_device(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove the device from HomeKit."""
    if HOMEKIT_DOMAIN in hass.data and "accessories" in hass.data[HOMEKIT_DOMAIN]:
        hass.data[HOMEKIT_DOMAIN]["accessories"].pop(entry.entry_id, None)
