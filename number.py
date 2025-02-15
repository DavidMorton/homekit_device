"""Platform for number integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_TARGET_TEMP,
    CONF_KEEP_WARM_TIME,
    CONF_SPEED_CONTROL,
    CONF_BRIGHTNESS,
    CONF_COLOR_TEMP,
    CONF_TARGET_HUMIDITY,
)
from .entity import HomeKitDeviceNumber

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HomeKit Device numbers."""
    device_type = hass.data[DOMAIN][config_entry.entry_id]["device_type"]
    base_name = config_entry.data.get(CONF_NAME, "Smart Device")
    entities = []

    # Device-specific number controls
    if device_type == "kettle":
        if target_temp := config_entry.data.get(CONF_TARGET_TEMP):
            entities.append(
                HomeKitDeviceNumber(
                    hass,
                    config_entry.entry_id,
                    f"{base_name} Target Temperature",
                    target_temp,
                    min_value=0,
                    max_value=100,
                    step=1,
                )
            )
        if keep_warm_time := config_entry.data.get(CONF_KEEP_WARM_TIME):
            entities.append(
                HomeKitDeviceNumber(
                    hass,
                    config_entry.entry_id,
                    f"{base_name} Keep Warm Time",
                    keep_warm_time,
                    min_value=0,
                    max_value=120,
                    step=1,
                )
            )

    elif device_type == "fan":
        if speed_control := config_entry.data.get(CONF_SPEED_CONTROL):
            entities.append(
                HomeKitDeviceNumber(
                    hass,
                    config_entry.entry_id,
                    f"{base_name} Speed",
                    speed_control,
                    min_value=0,
                    max_value=100,
                    step=1,
                )
            )

    elif device_type == "light":
        if brightness := config_entry.data.get(CONF_BRIGHTNESS):
            entities.append(
                HomeKitDeviceNumber(
                    hass,
                    config_entry.entry_id,
                    f"{base_name} Brightness",
                    brightness,
                    min_value=0,
                    max_value=100,
                    step=1,
                )
            )
        if color_temp := config_entry.data.get(CONF_COLOR_TEMP):
            entities.append(
                HomeKitDeviceNumber(
                    hass,
                    config_entry.entry_id,
                    f"{base_name} Color Temperature",
                    color_temp,
                    min_value=2000,
                    max_value=6500,
                    step=100,
                )
            )

    elif device_type == "humidifier":
        if target_humidity := config_entry.data.get(CONF_TARGET_HUMIDITY):
            entities.append(
                HomeKitDeviceNumber(
                    hass,
                    config_entry.entry_id,
                    f"{base_name} Target Humidity",
                    target_humidity,
                    min_value=0,
                    max_value=100,
                    step=1,
                )
            )

    if entities:
        async_add_entities(entities)
