"""Platform for switch integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_POWER_SWITCH,
)
from .entity import HomeKitDeviceSwitch

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HomeKit Device switches."""
    # Get the power switch entity
    power_switch = config_entry.data.get(CONF_POWER_SWITCH)
    if power_switch:
        async_add_entities([
            HomeKitDeviceSwitch(
                hass,
                config_entry.entry_id,
                config_entry.data.get(CONF_NAME, "Smart Device"),
                power_switch,
            )
        ])
