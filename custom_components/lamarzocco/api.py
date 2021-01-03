import asyncio
import errno
import logging
from datetime import datetime
from socket import error as SocketError

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from lmdirect import LMDirect
from lmdirect.msgs import DATE_RECEIVED, FIRMWARE_VER, POWER, UPDATE_AVAILABLE

from .const import DOMAIN, POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)


class LaMarzocco(LMDirect):
    """Keep data for La Marzocco entities."""

    def __init__(self, hass, config_entry=None, data=None):
        """Initialise the LaMarzocco entity data."""
        self._hass = hass
        self._current_status = {}
        self._polling_task = None
        self._config_entry = config_entry
        self._device_version = None

        """Start with the machine in standby if we haven't received accurate data yet"""
        self._current_status[POWER] = 0

        super().__init__(config_entry.data if config_entry else data)

    async def init_data(self, hass):
        """Register the callback to receive updates"""
        self.register_callback(self.update_callback)

        self._run = True

        """Start polling for status"""
        self._polling_task = hass.loop.create_task(self.fetch_data())

    async def close(self):
        """Stop the reeive and send loops"""
        self._run = False

        if self._polling_task:
            self._polling_task.cancel()

        await super().close()

    @callback
    def update_callback(self, **kwargs):
        """Callback when new data is available"""
        self._current_status.update(kwargs.get("current_status"))
        self._current_status[DATE_RECEIVED] = datetime.now().replace(microsecond=0)
        self._current_status[UPDATE_AVAILABLE] = self._update_available

        if not self._device_version and FIRMWARE_VER in self._current_status:
            self._hass.loop.create_task(
                self._update_device_info(self._current_status[FIRMWARE_VER])
            )
            self._device_version = self._current_status[FIRMWARE_VER]

    async def _update_device_info(self, firmware_version):
        """Update the device with the firmware version"""

        _LOGGER.debug(f"Updating firmware version to {firmware_version}")
        device_registry = await dr.async_get_registry(self._hass)
        device_entry = device_registry.async_get_device(
            {(DOMAIN, self.serial_number)}, set()
        )
        device_registry.async_update_device(
            device_entry.id, sw_version=firmware_version
        )

    async def fetch_data(self):
        while self._run:
            """Fetch data from API - (current weather and forecast)."""
            _LOGGER.debug("Fetching data")
            try:
                """Request latest status"""
                await self.request_status()
            except SocketError as e:
                if e.errno != errno.ECONNRESET:
                    raise
                else:
                    _LOGGER.debug("Connection error: {}".format(e))
            await asyncio.sleep(POLLING_INTERVAL)
