"""HomeKit accessory for HomeKit Device Aggregator."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.homekit import (
    ATTR_VALUE,
    HomeKit,
    HomeKitAccessory,
)
from homeassistant.components.homekit.const import (
    CATEGORY_KETTLE,
    PROP_CELSIUS,
    PROP_MAX_VALUE,
    PROP_MIN_VALUE,
    PROP_STEP_VALUE,
    SERV_KETTLE,
    CHAR_ON,
    CHAR_ACTIVE,
    CHAR_CURRENT_TEMPERATURE,
    CHAR_TARGET_TEMPERATURE,
    CHAR_STATUS_FAULT,
    CHAR_REMAINING_DURATION,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
    UnitOfTemperature,
)
from homeassistant.core import State, callback
from homeassistant.helpers.event import async_track_state_change
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
)

_LOGGER = logging.getLogger(__name__)

class HomeKitKettle(HomeKitAccessory):
    """HomeKit Kettle accessory."""

    def __init__(self, hass, driver, name, entry_id, aid, config):
        """Initialize a HomeKit kettle accessory."""
        super().__init__(driver, name, aid=aid)

        self._hass = hass
        self._entry_id = entry_id
        self._config = config
        self._aid = aid

        # Set up services
        serv_kettle = self.add_preload_service(SERV_KETTLE)

        # Power characteristic
        self.char_on = serv_kettle.configure_char(
            CHAR_ON, value=False
        )
        self.char_active = serv_kettle.configure_char(
            CHAR_ACTIVE, value=False
        )

        # Temperature characteristics
        if CONF_CURRENT_TEMP in config:
            self.char_current_temp = serv_kettle.configure_char(
                CHAR_CURRENT_TEMPERATURE,
                value=0,
                properties={
                    PROP_CELSIUS: True,
                    PROP_MIN_VALUE: 0,
                    PROP_MAX_VALUE: 100,
                    PROP_STEP_VALUE: 0.1,
                },
            )

        if CONF_TARGET_TEMP in config:
            self.char_target_temp = serv_kettle.configure_char(
                CHAR_TARGET_TEMPERATURE,
                value=100,
                properties={
                    PROP_CELSIUS: True,
                    PROP_MIN_VALUE: 0,
                    PROP_MAX_VALUE: 100,
                    PROP_STEP_VALUE: 1,
                },
            )

        # Status characteristics
        if CONF_FAULT in config:
            self.char_fault = serv_kettle.configure_char(
                CHAR_STATUS_FAULT, value=False
            )

        if CONF_COUNTDOWN in config:
            self.char_remaining = serv_kettle.configure_char(
                CHAR_REMAINING_DURATION, value=0
            )

        # Set up listeners
        self._setup_listeners()

    def _setup_listeners(self):
        """Set up listeners for state changes."""
        async def _state_changed(entity_id: str, old_state: State, new_state: State):
            """Handle state changes."""
            if new_state is None:
                return

            if entity_id == self._config[CONF_POWER_SWITCH]:
                is_on = new_state.state == STATE_ON
                self.char_on.set_value(is_on)
                self.char_active.set_value(is_on)

            elif entity_id == self._config.get(CONF_CURRENT_TEMP):
                try:
                    temp = float(new_state.state)
                    self.char_current_temp.set_value(temp)
                except (ValueError, AttributeError):
                    pass

            elif entity_id == self._config.get(CONF_TARGET_TEMP):
                try:
                    temp = float(new_state.state)
                    self.char_target_temp.set_value(temp)
                except (ValueError, AttributeError):
                    pass

            elif entity_id == self._config.get(CONF_FAULT):
                self.char_fault.set_value(new_state.state != "none")

            elif entity_id == self._config.get(CONF_COUNTDOWN):
                try:
                    remaining = int(float(new_state.state))
                    self.char_remaining.set_value(remaining)
                except (ValueError, AttributeError):
                    pass

        # Set up state change listeners
        entities_to_track = [self._config[CONF_POWER_SWITCH]]
        optional_entities = [
            CONF_CURRENT_TEMP,
            CONF_TARGET_TEMP,
            CONF_COUNTDOWN,
            CONF_FAULT,
            CONF_KEEP_WARM,
            CONF_KEEP_WARM_TIME,
        ]

        for entity_key in optional_entities:
            if entity_key in self._config and self._config[entity_key]:
                entities_to_track.append(self._config[entity_key])

        for entity_id in entities_to_track:
            if entity_id:
                async_track_state_change(
                    self._hass,
                    entity_id,
                    _state_changed
                )

        # Set initial states
        for entity_id in entities_to_track:
            if entity_id and (state := self._hass.states.get(entity_id)):
                _state_changed(entity_id, None, state)

    @callback
    def run(self):
        """Handle accessory driver started event.
        Run inside the HAP-python event loop.
        """
        super().run()

    async def stop(self):
        """Handle accessory driver stop event."""
        await super().stop()
