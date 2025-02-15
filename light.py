"""Platform for light integration."""
from __future__ import annotations

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_LIGHT_SWITCH,
)
from .entity import HomeKitDeviceEntity

class HomeKitDeviceLight(HomeKitDeviceEntity, LightEntity):
    """Representation of a HomeKit Device light."""

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the light on."""
        await self.hass.services.async_call(
            "light", "turn_on",
            {"entity_id": self._source_entity, **kwargs}
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the light off."""
        await self.hass.services.async_call(
            "light", "turn_off",
            {"entity_id": self._source_entity}
        )

    async def async_update_from_source(self, state) -> None:
        """Update the entity from the source entity state."""
        self._attr_is_on = state.state == "on"
        if "brightness" in state.attributes:
            self._attr_brightness = state.attributes["brightness"]
        if "color_temp" in state.attributes:
            self._attr_color_temp = state.attributes["color_temp"]
        if "rgb_color" in state.attributes:
            self._attr_rgb_color = state.attributes["rgb_color"]
        self.async_write_ha_state()

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HomeKit Device lights."""
    device_type = hass.data[DOMAIN][config_entry.entry_id]["device_type"]
    base_name = config_entry.data.get(CONF_NAME, "Smart Device")
    entities = []

    # Device-specific lights
    if device_type == "garage_door":
        if light_switch := config_entry.data.get(CONF_LIGHT_SWITCH):
            entities.append(
                HomeKitDeviceLight(
                    hass,
                    config_entry.entry_id,
                    f"{base_name} Light",
                    light_switch,
                )
            )

    if entities:
        async_add_entities(entities)
