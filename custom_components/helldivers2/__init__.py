"""The Helldivers 2 integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import Helldivers2Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Panel configuration
PANEL_URL = "helldivers2"
PANEL_TITLE = "Helldivers 2"
PANEL_ICON = "mdi:shield-sword"
PANEL_NAME = "helldivers2-panel"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Helldivers 2 from a config entry."""
    update_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = Helldivers2Coordinator(hass, update_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register the frontend panel
    await _async_register_panel(hass)

    return True


async def _async_register_panel(hass: HomeAssistant) -> None:
    """Register the Helldivers 2 panel."""
    # Get the path to the frontend files
    frontend_path = Path(__file__).parent / "frontend"

    # Register static path for serving the JS file
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                f"/helldivers2_panel",
                str(frontend_path),
                cache_headers=False,
            )
        ]
    )

    # Register the panel
    frontend.async_register_built_in_panel(
        hass,
        component_name=PANEL_NAME,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        frontend_url_path=PANEL_URL,
        config={},
        require_admin=False,
        module_url="/helldivers2_panel/helldivers2-panel.js",
    )

    _LOGGER.debug("Helldivers 2 panel registered")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: Helldivers2Coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

        # Remove the panel
        frontend.async_remove_panel(hass, PANEL_URL)
        _LOGGER.debug("Helldivers 2 panel removed")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
