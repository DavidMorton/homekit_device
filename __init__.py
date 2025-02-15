"""The HomeKit Device Aggregator integration."""
from __future__ import annotations

import logging
from typing import Final
import importlib

from homeassistant.components.homekit import (
    DOMAIN as HOMEKIT_DOMAIN,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_DEVICE_TYPE

_LOGGER: Final = logging.getLogger(__name__)

PLATFORMS: Final = [
    Platform.SWITCH,
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.BINARY_SENSOR,
    Platform.LIGHT,
]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the HomeKit Device Aggregator integration."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HomeKit Device Aggregator from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    device_type = entry.data.get(CONF_DEVICE_TYPE, "Unknown")
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "device_type": device_type,
        "entities": set(),
    }

    # Import platform modules
    for platform in PLATFORMS:
        platform_module = f".{platform}"
        await hass.async_add_executor_job(
            importlib.import_module, platform_module, __package__
        )

    # Register device
    # Register device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="HomeKit Device Aggregator",
        model=device_type.title(),
        suggested_area="Kitchen" if device_type == "kettle" else None,
    )


    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove config entry from a device."""
    return True
