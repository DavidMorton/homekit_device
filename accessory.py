"""HomeKit accessory for HomeKit Device Aggregator."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.homekit.accessories import HomeAccessory
from homeassistant.components.homekit.const import (
    CATEGORY_KETTLE,
    CHAR_ACTIVE,
    CHAR_CURRENT_TEMPERATURE,
    CHAR_TARGET_TEMPERATURE,
    CHAR_HEATING_THRESHOLD_TEMPERATURE,
    CHAR_ON,
    SERV_THERMOSTAT,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
    UnitOfTemperature,
)
from homeassistant.core import State, callback
from homeassistant.helpers.event import async_track_state_change

from .const import (
    DOMAIN,
    CONF_POWER_SWITCH,
    CONF_CURRENT_TEMP,
    CONF_TARGET_TEMP,
    CONF_COUNTDOWN,
    CONF_FAULT,
    CONF_KEEP_WARM,
    CONF_KEEP_WARM_TIME,
)

_LOGGER = logging.getLogger(__name__)

class KettleAccessory(HomeAccessory):
    """Kettle accessory that groups multiple entities."""

    def __init__(self, driver, name, entry_id, aid, config):
        """Initialize a Kettle accessory object."""
        super().__init__(driver, name, aid=aid)

        self.entry_id = entry_id
        self.config = config

        # Set up as a thermostat service since HomeKit doesn't have a specific kettle service
        serv_thermostat = self.add_preload_service(SERV_THERMOSTAT)

        # Power characteristic
        self.char_on = serv_thermostat.configure_char(
            CHAR_ON, value=False
        )
        self.char_active = serv_thermostat.configure_char(
            CHAR_ACTIVE, value=False
        )

        # Temperature characteristics
        if CONF_CURRENT_TEMP in config:
            self.char_current_temp = serv_thermostat.configure_char(
                CHAR_CURRENT_TEMPERATURE, value=0
            )

        if CONF_TARGET_TEMP in config:
            self.char_target_temp = serv_thermostat.configure_char(
                CHAR_TARGET_TEMPERATURE, value=100
            )
            self.char_heating_threshold = serv_thermostat.configure_char(
                CHAR_HEATING_THRESHOLD_TEMPERATURE, value=0
            )

        self.category = CATEGORY_KETTLE

    @callback
    def run(self):
        """Handle accessory driver started event."""
        if CONF_POWER_SWITCH in self.config:
            async_track_state_change(
                self.driver.hass,
                self.config[CONF_POWER_SWITCH],
                self._async_update_power_state,
            )

        if CONF_CURRENT_TEMP in self.config:
            async_track_state_change(
                self.driver.hass,
                self.config[CONF_CURRENT_TEMP],
                self._async_update_current_temp,
            )

        if CONF_TARGET_TEMP in self.config:
            async_track_state_change(
                self.driver.hass,
                self.config[CONF_TARGET_TEMP],
                self._async_update_target_temp,
            )

    @callback
    def _async_update_power_state(self, entity_id: str, old_state: State, new_state: State):
        """Handle power state changes."""
        if not new_state:
            return

        is_on = new_state.state == STATE_ON
        self.char_on.set_value(is_on)
        self.char_active.set_value(is_on)

    @callback
    def _async_update_current_temp(self, entity_id: str, old_state: State, new_state: State):
        """Handle current temperature changes."""
        if not new_state:
            return

        try:
            temp = float(new_state.state)
            self.char_current_temp.set_value(temp)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid temperature value: %s", new_state.state)

    @callback
    def _async_update_target_temp(self, entity_id: str, old_state: State, new_state: State):
        """Handle target temperature changes."""
        if not new_state:
            return

        try:
            temp = float(new_state.state)
            self.char_target_temp.set_value(temp)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid target temperature value: %s", new_state.state)
