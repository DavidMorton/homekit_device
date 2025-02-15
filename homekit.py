"""Support for HomeKit devices."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.homekit import (
    DOMAIN as HOMEKIT_DOMAIN,
    HomeKit,
)
from homeassistant.components.homekit.const import (
    CONF_ENTRY_INDEX,
)
from homeassistant.components.homekit.models import HomeKitEntryData
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    EVENT_HOMEASSISTANT_STARTED,
)
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_DEVICE_TYPE,
)
from .accessory import ACCESSORY_TYPES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Any,
) -> bool:
    """Set up HomeKit integration from a config entry."""
    _LOGGER.debug("Setting up HomeKit integration for %s", config_entry.data[CONF_NAME])

    device_type = config_entry.data[CONF_DEVICE_TYPE]
    if device_type not in ACCESSORY_TYPES:
        _LOGGER.error(
            "Device type %s not supported. Supported types: %s",
            device_type,
            ", ".join(ACCESSORY_TYPES.keys())
        )
        return False

    # Get the HomeKit entry data
    entry_data = HomeKitEntryData()
    entry_data.config_entry = config_entry
    entry_data.homekit = HomeKit(hass, HOMEKIT_DOMAIN, entry_data, CONF_ENTRY_INDEX)

    # Create the appropriate accessory based on device type
    accessory_class = ACCESSORY_TYPES[device_type]
    accessory = accessory_class(
        entry_data.homekit.driver,
        config_entry.data[CONF_NAME],
        config_entry.entry_id,
        entry_data.aid,
        config_entry.data,
    )

    # Add the accessory to HomeKit
    entry_data.accessories[(accessory.category, accessory.aid)] = accessory

    # Start HomeKit when Home Assistant is ready
    async def _async_start_homekit(_):
        """Start HomeKit."""
        await entry_data.homekit.async_start()

    hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STARTED, _async_start_homekit
    )

    return True
