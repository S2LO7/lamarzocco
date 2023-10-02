"""Base class for the La Marzocco entities."""

import asyncio

from dataclasses import dataclass

from homeassistant.core import callback
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    UPDATE_DELAY
)


@dataclass
class LaMarzoccoEntityDescriptionMixin:
    """Mixin for all LM entities"""
    extra_attributes: dict


@dataclass
class LaMarzoccoEntityDescription(
    EntityDescription,
    LaMarzoccoEntityDescriptionMixin
):
    """Description for all LM entities"""


@dataclass
class LaMarzoccoEntity(CoordinatorEntity):
    """Common elements for all entities."""

    entity_description: LaMarzoccoEntityDescription

    def __init__(self, coordinator, hass, entity_description):
        super().__init__(coordinator)
        self._hass = hass
        self.entity_description = entity_description
        self._lm_client = self.coordinator.data

    @property
    def name(self):
        """Return the name of the switch."""
        return (
            f"{self._lm_client.machine_name} " + self.entity_description.name
        )

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._lm_client.serial_number}_" + self.entity_description.key

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN, self._lm_client.serial_number)},
            "name": self._lm_client.machine_name,
            "manufacturer": "La Marzocco",
            "model": self._lm_client.true_model_name,
            "sw_version": self._lm_client.firmware_version,
        }

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""

        def bool_to_str(value):
            """ Convert boolean values to strings to improve display in Lovelace. """
            return str(value) if isinstance(value, bool) else value

        def tuple_to_str(key):
            """ Convert tuple keys to strings  """
            if isinstance(key, tuple):
                key = "_".join(key)
            return key

        data = self._lm_client.current_status
        attr = self.entity_description.extra_attributes[self._lm_client.model_name]
        if attr is None:
            return {}

        keys = [
            tuple_to_str(key) for key in attr
        ]
        return {key: bool_to_str(data[key]) for key in keys if key in data}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._lm_client = self.coordinator.data
        self.async_write_ha_state()

    async def _update_ha_state(self):
        """ Write the intermediate value returned from the action to HA state before actually refreshing"""
        self.async_write_ha_state()
        # wait for a bit before getting a new state, to let the machine settle in to any state changes
        await asyncio.sleep(UPDATE_DELAY)
        await self.coordinator.async_request_refresh()
