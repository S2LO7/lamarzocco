import logging
from datetime import timedelta

from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)

from lmcloud.exceptions import AuthFail, RequestNotSuccessful

from .const import (
    BREW_ACTIVE,
    CONF_USE_WEBSOCKET
)

SCAN_INTERVAL = timedelta(seconds=30)
UPDATE_DELAY = 2

_LOGGER = logging.getLogger(__name__)


class LmApiCoordinator(DataUpdateCoordinator):
    """Class to handle fetching data from the La Marzocco API centrally"""

    @property
    def lm(self):
        return self._lm

    def __init__(self, hass, config_entry, lm):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="La Marzocco API coordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=SCAN_INTERVAL
        )
        self._lm = lm
        self._initialized = False
        self._websocket_initialized = False
        self._config_entry = config_entry
        self._use_websocket = self._config_entry.options.get(CONF_USE_WEBSOCKET, False)

    async def _async_update_data(self):
        try:
            _LOGGER.debug("Update coordinator: Updating data")
            if not self._initialized:
                await self._lm.hass_init()

            elif self._initialized and not self._websocket_initialized and self._use_websocket:
                # only initialize websockets after the first update
                _LOGGER.debug("Initializing WebSockets.")
                self.hass.async_create_task(
                    self._lm._lm_local_api.websocket_connect(
                        callback=self._on_data_received,
                        use_sigterm_handler=False
                    )
                )
                self._websocket_initialized = True

            await self._lm.update_local_machine_status()

        except AuthFail as ex:
            msg = "Authentication failed. \
                            Maybe one of your credential details was invalid or you changed your password."
            _LOGGER.error(msg)
            raise ConfigEntryAuthFailed(msg) from ex
        except (RequestNotSuccessful, Exception) as ex:
            _LOGGER.error(ex)
            raise UpdateFailed("Querying API failed. Error: %s", ex)
        _LOGGER.debug("Current status: %s", str(self._lm.current_status))
        self._initialized = True
        return self._lm

    @callback
    def _on_data_received(self, property_updated, update):
        """ callback which gets called whenever the websocket receives data """

        if not property_updated or not self._initialized:
            return

        _LOGGER.debug("Received data from websocket, property updated: %s", str(property_updated))
        if property_updated:
            if property_updated != BREW_ACTIVE:
                self._lm._current_status[property_updated] = update
            else:
                self._lm._brew_active = update

        self.data = self._lm
        self.async_update_listeners()
