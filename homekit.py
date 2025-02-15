"""Support for HomeKit devices."""
from __future__ import annotations

import logging
from typing import Any, Final

from homeassistant.components.homekit import (
    DOMAIN as HOMEKIT_DOMAIN,
    KNOWN_DEVICES,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_DEVICE_TYPE,
)
from .accessory import ACCESSORY_TYPES

_LOGGER: Final = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up HomeKit integration from a config entry."""
    _LOGGER.debug("Setting up HomeKit integration for %s", config_entry.title)

    device_type = config_entry.data[CONF_DEVICE_TYPE]
    if device_type not in ACCESSORY_TYPES:
        _LOGGER.error(
            "Device type %s not supported. Supported types: %s",
            device_type,
            ", ".join(ACCESSORY_TYPES.keys())
        )
        return False

    # Create the appropriate accessory based on device type
    accessory_class = ACCESSORY_TYPES[device_type]
    entity = accessory_class(
        config_entry.entry_id,
        f"{DOMAIN}_{config_entry.entry_id}",
    )

    # Store config in entity
    entity._config = config_entry.data

    # Add entity to Home Assistant
    async_add_entities([entity])

    # Register the entity with HomeKit
    if HOMEKIT_DOMAIN not in hass.data:
        hass.data[HOMEKIT_DOMAIN] = {}
    if "pending" not in hass.data[HOMEKIT_DOMAIN]:
        hass.data[HOMEKIT_DOMAIN]["pending"] = []

    hass.data[HOMEKIT_DOMAIN]["pending"].append(entity)

    # Make sure this device is removed from HomeKit when the config entry is removed
    config_entry.async_on_unload(
        lambda: hass.data[HOMEKIT_DOMAIN]["pending"].remove(entity)
        if entity in hass.data[HOMEKIT_DOMAIN]["pending"]
        else None
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This will be handled by Home Assistant's entity registry
    return True

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    # Remove from KNOWN_DEVICES to allow re-adding
    unique_id = f"{DOMAIN}_{entry.entry_id}"
    KNOWN_DEVICES.discard(unique_id)
