"""HomeKit accessories for HomeKit Device Aggregator."""
from __future__ import annotations

import logging
from typing import Any, Final

from homeassistant.components.homekit import (
    KNOWN_DEVICES,
    HomeKitEntity,
)
from homeassistant.components.homekit.const import (
    CATEGORY_KETTLE,
    CATEGORY_FAN,
    CHAR_ACTIVE,
    CHAR_CURRENT_TEMPERATURE,
    CHAR_TARGET_TEMPERATURE,
    CHAR_HEATING_THRESHOLD_TEMPERATURE,
    CHAR_ON,
    CHAR_ROTATION_SPEED,
    CHAR_SWING_MODE,
    PROP_MAX_VALUE,
    PROP_MIN_VALUE,
    PROP_STEP_VALUE,
    SERV_THERMOSTAT,
    SERV_FANV2,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    UnitOfTemperature,
)
from homeassistant.core import State, callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_POWER_SWITCH,
    CONF_CURRENT_TEMP,
    CONF_TARGET_TEMP,
    CONF_COUNTDOWN,
    CONF_FAULT,
    CONF_KEEP_WARM,
    CONF_KEEP_WARM_TIME,
    CONF_SPEED_CONTROL,
    CONF_OSCILLATION,
)

_LOGGER: Final = logging.getLogger(__name__)


class HomeKitDeviceEntity(HomeKitEntity):
    """Base class for HomeKit device entities."""

    def __init__(self, entry_id: str, unique_id: str) -> None:
        """Initialize the entity."""
        super().__init__(unique_id)
        self._entry_id = entry_id
        self._attr_unique_id = unique_id
        self._attr_should_poll = False

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": self.name,
            "manufacturer": "HomeKit Device Aggregator",
            "model": self.__class__.__name__,
            "via_device": (DOMAIN, self._entry_id),
        }


class KettleAccessory(HomeKitDeviceEntity):
    """Representation of a HomeKit kettle accessory."""

    @property
    def category(self) -> int:
        """Return the HomeKit category."""
        return CATEGORY_KETTLE

    def get_services(self) -> list:
        """Define services."""
        services = []

        # Thermostat service (used for kettle functionality)
        serv_thermostat = self.add_preload_service(SERV_THERMOSTAT)

        # Power characteristics
        self.char_on = serv_thermostat.configure_char(
            CHAR_ON, value=False, setter_callback=self.set_state
        )
        self.char_active = serv_thermostat.configure_char(CHAR_ACTIVE, value=False)

        # Temperature characteristics
        if self._config.get(CONF_CURRENT_TEMP):
            self.char_current_temp = serv_thermostat.configure_char(
                CHAR_CURRENT_TEMPERATURE,
                value=0,
                properties={
                    PROP_MIN_VALUE: 0,
                    PROP_MAX_VALUE: 100,
                    PROP_STEP_VALUE: 0.1,
                },
            )

        if self._config.get(CONF_TARGET_TEMP):
            self.char_target_temp = serv_thermostat.configure_char(
                CHAR_TARGET_TEMPERATURE,
                value=100,
                properties={
                    PROP_MIN_VALUE: 0,
                    PROP_MAX_VALUE: 100,
                    PROP_STEP_VALUE: 1,
                },
                setter_callback=self.set_target_temperature,
            )

        services.append(serv_thermostat)
        return services

    async def set_state(self, value: bool) -> None:
        """Set kettle state."""
        if not self.available:
            return

        service = SERVICE_TURN_ON if value else SERVICE_TURN_OFF
        await self.hass.services.async_call(
            "switch",
            service,
            {ATTR_ENTITY_ID: self._config[CONF_POWER_SWITCH]},
            blocking=True,
        )

    async def set_target_temperature(self, value: float) -> None:
        """Set target temperature."""
        if not self.available or CONF_TARGET_TEMP not in self._config:
            return

        await self.hass.services.async_call(
            "number",
            "set_value",
            {
                ATTR_ENTITY_ID: self._config[CONF_TARGET_TEMP],
                "value": value,
            },
            blocking=True,
        )

    @callback
    def async_update_state(self, new_state: State) -> None:
        """Update entity state."""
        if new_state.entity_id == self._config[CONF_POWER_SWITCH]:
            is_on = new_state.state == STATE_ON
            self.char_on.set_value(is_on)
            self.char_active.set_value(is_on)

        elif (
            CONF_CURRENT_TEMP in self._config
            and new_state.entity_id == self._config[CONF_CURRENT_TEMP]
        ):
            try:
                temp = float(new_state.state)
                self.char_current_temp.set_value(temp)
            except (ValueError, TypeError):
                _LOGGER.warning("Invalid temperature value: %s", new_state.state)

        elif (
            CONF_TARGET_TEMP in self._config
            and new_state.entity_id == self._config[CONF_TARGET_TEMP]
        ):
            try:
                temp = float(new_state.state)
                self.char_target_temp.set_value(temp)
            except (ValueError, TypeError):
                _LOGGER.warning("Invalid target temperature value: %s", new_state.state)


class FanAccessory(HomeKitDeviceEntity):
    """Representation of a HomeKit fan accessory."""

    @property
    def category(self) -> int:
        """Return the HomeKit category."""
        return CATEGORY_FAN

    def get_services(self) -> list:
        """Define services."""
        services = []

        # Fan service
        serv_fan = self.add_preload_service(SERV_FANV2)

        # Basic characteristics
        self.char_on = serv_fan.configure_char(
            CHAR_ON, value=False, setter_callback=self.set_state
        )
        self.char_active = serv_fan.configure_char(CHAR_ACTIVE, value=False)

        # Optional characteristics
        if self._config.get(CONF_SPEED_CONTROL):
            self.char_speed = serv_fan.configure_char(
                CHAR_ROTATION_SPEED,
                value=0,
                properties={
                    PROP_MIN_VALUE: 0,
                    PROP_MAX_VALUE: 100,
                    PROP_STEP_VALUE: 1,
                },
                setter_callback=self.set_speed,
            )

        if self._config.get(CONF_OSCILLATION):
            self.char_swing = serv_fan.configure_char(
                CHAR_SWING_MODE, value=0, setter_callback=self.set_swing
            )

        services.append(serv_fan)
        return services

    async def set_state(self, value: bool) -> None:
        """Set fan state."""
        if not self.available:
            return

        service = SERVICE_TURN_ON if value else SERVICE_TURN_OFF
        await self.hass.services.async_call(
            "switch",
            service,
            {ATTR_ENTITY_ID: self._config[CONF_POWER_SWITCH]},
            blocking=True,
        )

    async def set_speed(self, value: int) -> None:
        """Set fan speed."""
        if not self.available or CONF_SPEED_CONTROL not in self._config:
            return

        await self.hass.services.async_call(
            "number",
            "set_value",
            {
                ATTR_ENTITY_ID: self._config[CONF_SPEED_CONTROL],
                "value": value,
            },
            blocking=True,
        )

    async def set_swing(self, value: int) -> None:
        """Set swing mode."""
        if not self.available or CONF_OSCILLATION not in self._config:
            return

        service = SERVICE_TURN_ON if value else SERVICE_TURN_OFF
        await self.hass.services.async_call(
            "switch",
            service,
            {ATTR_ENTITY_ID: self._config[CONF_OSCILLATION]},
            blocking=True,
        )

    @callback
    def async_update_state(self, new_state: State) -> None:
        """Update entity state."""
        if new_state.entity_id == self._config[CONF_POWER_SWITCH]:
            is_on = new_state.state == STATE_ON
            self.char_on.set_value(is_on)
            self.char_active.set_value(is_on)

        elif (
            CONF_SPEED_CONTROL in self._config
            and new_state.entity_id == self._config[CONF_SPEED_CONTROL]
        ):
            try:
                speed = float(new_state.state)
                self.char_speed.set_value(speed)
            except (ValueError, TypeError):
                _LOGGER.warning("Invalid speed value: %s", new_state.state)

        elif (
            CONF_OSCILLATION in self._config
            and new_state.entity_id == self._config[CONF_OSCILLATION]
        ):
            self.char_swing.set_value(new_state.state == STATE_ON)


ACCESSORY_TYPES: Final[dict[str, type[HomeKitDeviceEntity]]] = {
    "kettle": KettleAccessory,
    "fan": FanAccessory,
}
