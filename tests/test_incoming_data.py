"""Test La Marzocco integration with different incoming messages."""
import logging
from copy import deepcopy

import lmdirect
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.setup import async_setup_component
from lmdirect.msgs import GATEWAY_DRINK_MAP, UPDATE_AVAILABLE
from pytest_homeassistant_custom_component.async_mock import patch
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lamarzocco.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_KEY,
    CONF_MACHINE_NAME,
    CONF_MODEL_NAME,
    CONF_SERIAL_NUMBER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

ENTRY_ID = 1


async def setup_lm_machine(hass):
    await async_setup_component(hass, DOMAIN, {})

    DATA = {
        CONF_HOST: "1.2.3.4",
        CONF_CLIENT_ID: "aabbcc",
        CONF_CLIENT_SECRET: "bbccdd",
        CONF_USERNAME: "username",
        CONF_PASSWORD: "password",
        CONF_SERIAL_NUMBER: "aabbcc",
        CONF_MODEL_NAME: "aaaaa",
        CONF_MACHINE_NAME: "bbbbb",
        CONF_KEY: "12345678901234567890123456789012",
    }

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=deepcopy(DATA),
        entry_id=ENTRY_ID,
    )

    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.entry_id in hass.data[DOMAIN]

    machine = hass.data[DOMAIN][config_entry.entry_id]
    assert machine is not None

    return machine


async def unload_lm_machine(hass):
    assert await hass.config_entries.async_unload(ENTRY_ID)
    assert not hass.data[DOMAIN]


STATUS_DATA = "status_data"
CONFIG_DATA = "config_data"
AUTO_ON_OFF_DATA = "auto_on_off_data"
DATETIME_DATA = "datetime_data"
DRINKS_DATA = "drinks_data"
FLOW_DATA = "flow_data"
SERIAL_NUM_DATA = "serial_num_data"
TEMP_REPORT_DATA = "temp_report_data"

"""Structure reprsenting all tests to run."""
DATA = {
    STATUS_DATA: {
        "msg": "R400000200178020000000000000000000000000100000000000000010100001003B804D629",
        "resp": {
            "hot_water_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "firmware_ver": "1.20",
            "module_ser_num": "",
            "power": 1,
        },
    },
    CONFIG_DATA: {
        "msg": "R0000001F010000026E313903C204D7000B16212C0B16212C00780076006E008203E808B9",
        "resp": {
            "hot_water_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "coffee_set_temp": 96.2,
            "steam_set_temp": 123.9,
            "enable_prebrewing": 0,
            "prebrewing_ton_k1": 11,
            "prebrewing_ton_k2": 22,
            "prebrewing_ton_k3": 33,
            "prebrewing_ton_k4": 44,
            "prebrewing_toff_k1": 11,
            "prebrewing_toff_k2": 22,
            "prebrewing_toff_k3": 33,
            "prebrewing_toff_k4": 44,
            "dose_k1": 120,
            "dose_k2": 118,
            "dose_k3": 110,
            "dose_k4": 130,
            "dose_k5": 1000,
            "dose_tea": 8,
        },
    },
    AUTO_ON_OFF_DATA: {
        "msg": "R0310001DFF061106110611061106110611061100000000000000000000000000002F",
        "resp": {
            "hot_water_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "global_auto": "Enabled",
            "mon": "Enabled",
            "tue": "Enabled",
            "wed": "Enabled",
            "thu": "Enabled",
            "fri": "Enabled",
            "sat": "Enabled",
            "sun": "Enabled",
            "sun_on": 6,
            "sun_off": 17,
            "mon_on": 6,
            "mon_off": 17,
            "tue_on": 6,
            "tue_off": 17,
            "wed_on": 6,
            "wed_off": 17,
            "thu_on": 6,
            "thu_off": 17,
            "fri_on": 6,
            "fri_off": 17,
            "sat_on": 6,
            "sat_off": 17,
        },
    },
    DATETIME_DATA: {
        "msg": "R03000007001A0906020115A6",
        "resp": {
            "hot_water_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "second": 0,
            "minute": 26,
            "hour": 9,
            "dayofweek": 6,
            "day": 2,
            "month": 21,
        },
    },
    DRINKS_DATA: {
        "msg": "R0020002C0000014B00000098000001B1000000250000056A00000923000000180000000A00000AEE000000180000003A48",
        "resp": {
            "hot_water_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "drinks_k1": 331,
            "drinks_k2": 152,
            "drinks_k3": 433,
            "drinks_k4": 37,
            "continuous": 1386,
            "total_coffee": 2339,
            "hot_water": 24,
            "drink_mystery": 10,
            "total_drinks": 2798,
            "hot_water_2": 24,
            "drinks_tea": 58,
        },
    },
    FLOW_DATA: {
        "msg": "Z600000160000000000000000000000000401000A000E03B604D4E604",
        "resp": {
            "hot_water_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "flow_mystery": 1025,
            "flow_pulses": 10,
            "flow_seconds": 14,
        },
    },
    SERIAL_NUM_DATA: {
        "msg": "R010000115A000000000000000000000000000000004B",
        "resp": {
            "hot_water_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "machine_ser_num": "",
        },
    },
    TEMP_REPORT_DATA: {
        "msg": "R401C000403BC04D8B6",
        "resp": {
            "hot_water_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "coffee_temp": 95.6,
            "steam_temp": 124.0,
        },
    },
}


@patch.object(lmdirect.LMDirect, "_connect", autospec=True)
@patch.object(lmdirect.LMDirect, "_send_msg", autospec=True)
class TestMessages:
    """Class containing available tests.  Patches will be applied to all member functions."""

    async def test_status_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, [STATUS_DATA])

    async def test_config_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, [CONFIG_DATA])

    async def test_auto_on_off_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, [AUTO_ON_OFF_DATA])

    async def test_datetime_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, [DATETIME_DATA])

    async def test_drinks_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, [DRINKS_DATA])

    async def test_flow_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, [FLOW_DATA])

    async def test_serial_number_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, [SERIAL_NUM_DATA])

    async def test_temp_report_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, [TEMP_REPORT_DATA])

    async def test_send_all_data(self, mock_send_msg, mock_connect, hass):
        await self.send_items(mock_send_msg, hass, list(DATA.keys()))

    async def send_items(self, mock_send_msg, hass, items):
        """Inject data and compare results."""

        expected = {}
        result = {}

        async def add_data(self, *args, **kwargs):
            async def send_msg(self, *args, **kwargs):
                """Populate data structures with sample data."""
                nonlocal expected
                nonlocal result
                msg = DATA[kwargs["item"]]["msg"]
                resp = DATA[kwargs["item"]]["resp"]
                expected.update(resp)
                print(f"SENDING {msg} expecting {resp}")
                self._current_status.update(
                    {GATEWAY_DRINK_MAP[x]: 0 for x in range(-1, 5)}
                )
                self._current_status.update({UPDATE_AVAILABLE: "none"})
                await self.process_data(msg)

            [await send_msg(self, *args, item=x, **kwargs) for x in items]
            result.update(self._current_status)
            print(f"Result: {result}")
            print(f"Expected: {expected}")

        """Populate data every time the _send_msg API is called, simulating lots of incoming data."""
        mock_send_msg.side_effect = add_data

        await setup_lm_machine(hass)

        await hass.async_block_till_done()

        assert result == expected

        await unload_lm_machine(hass)