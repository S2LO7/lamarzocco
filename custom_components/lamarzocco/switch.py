"""Switch platform for La Marzocco espresso machines."""
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import (
    DATE_RECEIVED,
    DOMAIN,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    MODEL_LMU,
    MON,
    TUE,
    WED,
    THU,
    FRI,
    SAT,
    SUN,
)

from .entity import LaMarzoccoEntity, LaMarzoccoEntityDescription
from .lm_client import LaMarzoccoClient
from .services import async_setup_entity_services

DOSE = "dose"
ATTR_MAP_MAIN_GS3_AV = [
    (DOSE, "k1"),
    (DOSE, "k2"),
    (DOSE, "k3"),
    (DOSE, "k4"),
    (DOSE, "k5"),
]

ON = "on"
OFF = "off"
AUTO = "auto"
TIME = "time"

ATTR_MAP_AUTO_ON_OFF = [
    DATE_RECEIVED,
    (MON, AUTO),
    (MON, ON, TIME),
    (MON, OFF, TIME),
    (TUE, AUTO),
    (TUE, ON, TIME),
    (TUE, OFF, TIME),
    (WED, AUTO),
    (WED, ON, TIME),
    (WED, OFF, TIME),
    (THU, AUTO),
    (THU, ON, TIME),
    (THU, OFF, TIME),
    (FRI, AUTO),
    (FRI, ON, TIME),
    (FRI, OFF, TIME),
    (SAT, AUTO),
    (SAT, ON, TIME),
    (SAT, OFF, TIME),
    (SUN, AUTO),
    (SUN, ON, TIME),
    (SUN, OFF, TIME),
]

TON = "ton"
TOFF = "toff"
PREBREWING = "prebrewing"
PREINFUSION = "preinfusion"

ATTR_MAP_PREBREW_GS3_AV = [
    DATE_RECEIVED,
    (PREBREWING, TON, "k1"),
    (PREBREWING, TON, "k2"),
    (PREBREWING, TON, "k3"),
    (PREBREWING, TON, "k4"),
    (PREBREWING, TOFF, "k1"),
    (PREBREWING, TOFF, "k2"),
    (PREBREWING, TOFF, "k3"),
    (PREBREWING, TOFF, "k4"),
]

ATTR_MAP_PREINFUSION_GS3_AV = [
    DATE_RECEIVED,
    (PREINFUSION, "k1"),
    (PREINFUSION, "k2"),
    (PREINFUSION, "k3"),
    (PREINFUSION, "k4"),
]

ATTR_MAP_PREINFUSION_LM = [
    DATE_RECEIVED,
    (PREINFUSION, "k1"),
]

ATTR_MAP_PREBREW_LM = [
    DATE_RECEIVED,
    (PREBREWING, TON, "k1"),
    (PREBREWING, TOFF, "k1"),
]


@dataclass
class LaMarzoccoSwitchEntityDescriptionMixin:
    """Description of an La Marzocco Switch"""
    control_fn: Callable[[LaMarzoccoClient, bool], Coroutine[Any, Any, None]]
    is_on_fn: Callable[[LaMarzoccoClient], bool]


@dataclass
class LaMarzoccoSwitchEntityDescription(
    SwitchEntityDescription,
    LaMarzoccoEntityDescription,
    LaMarzoccoSwitchEntityDescriptionMixin
):
    """Description of an La Marzocco Switch"""


ENTITIES: tuple[LaMarzoccoSwitchEntityDescription, ...] = (
    LaMarzoccoSwitchEntityDescription(
        key="main",
        name="Main",
        icon="mdi:coffee-maker",
        control_fn=lambda client, state: client.set_power(state),
        is_on_fn=lambda client: client.current_status["power"],
        extra_attributes={
            MODEL_GS3_AV: ATTR_MAP_MAIN_GS3_AV,
            MODEL_GS3_MP: None,
            MODEL_LM: None,
            MODEL_LMU: None,
        }
    ),
    LaMarzoccoSwitchEntityDescription(
        key="auto_on_off",
        name="Auto On Off",
        icon="mdi:alarm",
        control_fn=lambda client, state: client.set_auto_on_off_global(state),
        is_on_fn=lambda client: client.current_status["global_auto"] == "Enabled",
        extra_attributes={
            MODEL_GS3_AV: ATTR_MAP_AUTO_ON_OFF,
            MODEL_GS3_MP: ATTR_MAP_AUTO_ON_OFF,
            MODEL_LM: ATTR_MAP_AUTO_ON_OFF,
            MODEL_LMU: ATTR_MAP_AUTO_ON_OFF
        }
    ),
    LaMarzoccoSwitchEntityDescription(
        key="prebrew",
        name="Prebrew",
        icon="mdi:location-enter",
        control_fn=lambda client, state: client.set_prebrewing_enable(state),
        is_on_fn=lambda client: client.current_status["enable_prebrewing"],
        extra_attributes={
            MODEL_GS3_AV: ATTR_MAP_PREBREW_GS3_AV,
            MODEL_LM: ATTR_MAP_PREBREW_LM,
            MODEL_LMU: ATTR_MAP_PREBREW_LM,
        }
    ),
    LaMarzoccoSwitchEntityDescription(
        key="preinfusion",
        name="Preinfusion",
        icon="mdi:location-enter",
        control_fn=lambda client, state: client.set_preinfusion_enable(state),
        is_on_fn=lambda client: client.current_status["enable_preinfusion"],
        extra_attributes={
            MODEL_GS3_AV: ATTR_MAP_PREINFUSION_GS3_AV,
            MODEL_LM: ATTR_MAP_PREINFUSION_LM,
            MODEL_LMU: ATTR_MAP_PREINFUSION_LM,
        }
    ),
    LaMarzoccoSwitchEntityDescription(
        key="steam_boiler_enable",
        name="Steam Boiler Enable",
        icon="mdi:water-boiler",
        control_fn=lambda client, state: client.set_steam_boiler_enable(state),
        is_on_fn=lambda client: client.current_status["steam_boiler_enable"],
        extra_attributes={
            MODEL_GS3_AV: None,
            MODEL_GS3_MP: None,
            MODEL_LM: None,
            MODEL_LMU: None,
        }
    )
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up switch entities and services."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        LaMarzoccoSwitchEntity(coordinator, hass, description)
        for description in ENTITIES
        if coordinator.lm.model_name in description.extra_attributes.keys()
    )

    await async_setup_entity_services(coordinator.lm)


class LaMarzoccoSwitchEntity(LaMarzoccoEntity, SwitchEntity):
    """Switches representing espresso machine power, prebrew, and auto on/off."""

    def __init__(self, coordinator, hass, entity_description):
        """Initialise switches."""
        super().__init__(coordinator, hass, entity_description)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn device on."""
        await self.entity_description.control_fn(self._lm_client, True)
        await self._update_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn device off."""
        await self.entity_description.control_fn(self._lm_client, False)
        await self._update_ha_state()

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self.entity_description.is_on_fn(self._lm_client)
