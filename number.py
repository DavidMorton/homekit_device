"""Platform for number integration."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.homekit.const import (
    CHAR_TEMPERATURE_TARGET,
)

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_TARGET_TEMP,
)
from .entity import HomeKitDeviceEntity

class HomeKitDeviceNumber(HomeKitDeviceEntity, NumberEntity):
    """Representation of a HomeKit Device number."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = "temperature"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        name: str,
        entity_id: str,
    ) -> None:
        """Initialize the number."""
        super().__init__(hass, entry_id, name, entity_id)
        self._attr_translation_key = "temperature"
        self._attr_homekit_char = CHAR_TEMPERATURE_TARGET

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.hass.services.async_call(
            "input_number", "set_value",
            {"entity_id": self._source_entity, "value": value}
        )

    async def async_update_from_source(self, state) -> None:
        """Update the entity from the source entity state."""
        try:
            self._attr_native_value = float(state.state)
            self.async_write_ha_state()
        except ValueError:
            pass

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
                )
            )

    if entities:
        async_add_entities(entities)
