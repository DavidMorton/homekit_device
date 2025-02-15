"""Platform entities for HomeKit Device Aggregator."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.select import SelectEntity
from homeassistant.const import (
    ATTR_NAME,
    STATE_ON,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    STATE_OFF,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.event import async_track_state_change
from homeassistant.components.homekit.const import (
    ATTR_DISPLAY_NAME,
    CONF_FEATURE_LIST,
    CHAR_TEMPERATURE_CURRENT,
    CHAR_TEMPERATURE_TARGET,
    CONF_LINKED_BATTERY_SENSOR,
    CHAR_HEATING_COOLING_CURRENT,
    CONF_LOW_BATTERY_THRESHOLD,
)

from .const import DOMAIN, CONF_NAME, CONF_DEVICE_TYPE

class HomeKitDeviceEntity:
    """Representation of a HomeKit Device entity."""

    def __init__(self, hass: HomeAssistant, entry_id: str, name: str, entity_id: str) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._entry_id = entry_id
        self._name = name
        self._source_entity = entity_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{entity_id}"
        self._attr_name = name
        self._attr_has_entity_name = True
        self.device_type = self.hass.data[DOMAIN][entry_id]["device_type"]
        device_name = self.hass.data[DOMAIN][entry_id]["config"][CONF_NAME]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry_id}")},
            name=device_name,
            manufacturer="HomeKit Device Aggregator",
            model=self.device_type.title(),
            suggested_area="Kitchen" if self.device_type == "kettle" else None,
            via_device=(DOMAIN, f"{DOMAIN}_{entry_id}"),
        )
        self._attr_should_poll = False

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to register update signal handler."""
        async def _update_from_source(entity_id, old_state, new_state):
            if new_state is None:
                return
            await self.async_update_from_source(new_state)

        self.async_on_remove(
            async_track_state_change(
                self.hass,
                self._source_entity,
                _update_from_source
            )
        )

        # Set initial state
        if state := self.hass.states.get(self._source_entity):
            await self.async_update_from_source(state)

    async def async_update_from_source(self, state) -> None:
        """Update the entity from the source entity state."""
        raise NotImplementedError

class HomeKitDeviceSwitch(HomeKitDeviceEntity, SwitchEntity):
    """Representation of a HomeKit Device switch."""

    _attr_device_class = "switch"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.hass.services.async_call(
            "switch", "turn_on", {"entity_id": self._source_entity}
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        await self.hass.services.async_call(
            "switch", "turn_off", {"entity_id": self._source_entity}
        )

    async def async_update_from_source(self, state) -> None:
        """Update the entity from the source entity state."""
        self._attr_is_on = state.state == STATE_ON
        self.async_write_ha_state()

class HomeKitDeviceSensor(HomeKitDeviceEntity, SensorEntity):
    """Representation of a HomeKit Device sensor."""

    def __init__(self, hass: HomeAssistant, entry_id: str, name: str, entity_id: str, unit: str | None = None) -> None:
        """Initialize the sensor."""
        super().__init__(hass, entry_id, name, entity_id)
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE if unit == TEMP_CELSIUS else None

        # Set HomeKit characteristics for temperature sensors
        if self._attr_device_class == DEVICE_CLASS_TEMPERATURE:
            self._attr_entity_category = None  # Show in HomeKit
            self._attr_translation_key = "temperature"
            self._attr_homekit_char = CHAR_TEMPERATURE_CURRENT

    async def async_update_from_source(self, state) -> None:
        """Update the entity from the source entity state."""
        self._attr_native_value = state.state
        self.async_write_ha_state()

class HomeKitDeviceSelect(HomeKitDeviceEntity, SelectEntity):
    """Representation of a HomeKit Device select."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        name: str,
        entity_id: str,
        options: list[str],
    ) -> None:
        """Initialize the select."""
        super().__init__(hass, entry_id, name, entity_id)
        self._attr_options = options

        # Set HomeKit characteristics for keep warm functionality
        if "Keep Warm" in name and self.device_type == "kettle":
            self._attr_entity_category = None  # Show in HomeKit
            self._attr_translation_key = "keep_warm"
            self._attr_homekit_char = CHAR_HEATING_COOLING_CURRENT
            self._attr_icon = "mdi:kettle-steam"

    async def async_select_option(self, option: str) -> None:
        """Update the current value."""
        await self.hass.services.async_call(
            "select", "select_option",
            {"entity_id": self._source_entity, "option": option}
        )

    async def async_update_from_source(self, state) -> None:
        """Update the entity from the source entity state."""
        if "Keep Warm" in self._name and self.device_type == "kettle":
            # Convert keep warm state to HomeKit format
            self._attr_current_option = "On" if state.state != "Off" else "Off"
        else:
            self._attr_current_option = state.state
        self.async_write_ha_state()
