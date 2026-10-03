"""The Helldivers 2 integration."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components.frontend import (
    async_register_built_in_panel,
    async_remove_panel,
)
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_UPDATE_INTERVAL,
    CONF_DEBUG_LOGGING,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LEGACY_REPORTER_OPTIONS,
)
from .coordinator import Helldivers2Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Panel configuration
PANEL_URL = "helldivers2"
PANEL_TITLE = "Helldivers 2"
PANEL_ICON = "mdi:shield-sword"
PANEL_NAME = "helldivers2-panel"
PANEL_REGISTERED = "helldivers2_panel_registered"
DEBUG_ENABLED = "helldivers2_debug_enabled"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Helldivers 2 from a config entry."""
    # The built-in GitHub reporter was removed (use gh_issue_reporter instead).
    # Drop its stored options so the old PAT doesn't linger in .storage. This
    # runs before the update listener is added, so it doesn't trigger a reload.
    if any(key in entry.options for key in LEGACY_REPORTER_OPTIONS):
        hass.config_entries.async_update_entry(
            entry,
            options={
                k: v for k, v in entry.options.items()
                if k not in LEGACY_REPORTER_OPTIONS
            },
        )
        _LOGGER.info("Removed legacy GitHub error-reporting options")

    update_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL)
    debug_logging = entry.options.get(CONF_DEBUG_LOGGING, False)

    hass.data.setdefault(DOMAIN, {})

    # Store debug setting
    hass.data[DOMAIN][DEBUG_ENABLED] = debug_logging
    if debug_logging:
        _LOGGER.info("Debug logging enabled for Helldivers 2 integration")

    coordinator = Helldivers2Coordinator(hass, entry, update_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register the frontend panel (only once)
    if not hass.data[DOMAIN].get(PANEL_REGISTERED):
        await _async_register_panel(hass)
        hass.data[DOMAIN][PANEL_REGISTERED] = True

    return True



async def _async_register_panel(hass: HomeAssistant) -> None:
    """Register the Helldivers 2 panel."""
    try:
        # Get the path to the frontend files
        frontend_path = Path(__file__).parent / "frontend"

        # Register static path for serving the JS file
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    "/helldivers2_panel",
                    str(frontend_path),
                    cache_headers=False,
                )
            ]
        )

        # Register the panel using the direct import
        async_register_built_in_panel(
            hass,
            component_name="custom",
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            frontend_url_path=PANEL_URL,
            config={
                "_panel_custom": {
                    "name": PANEL_NAME,
                    "module_url": "/helldivers2_panel/helldivers2-panel.js",
                }
            },
            require_admin=False,
        )

        _LOGGER.info("Helldivers 2 panel registered")
    except Exception as e:
        _LOGGER.error("Failed to register panel: %s", e)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: Helldivers2Coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

        # Only remove panel if no other entries exist
        remaining_entries = [
            e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id
        ]
        if not remaining_entries and hass.data[DOMAIN].get(PANEL_REGISTERED):
            async_remove_panel(hass, PANEL_URL)
            hass.data[DOMAIN][PANEL_REGISTERED] = False
            _LOGGER.info("Helldivers 2 panel removed")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


def is_debug_enabled(hass: HomeAssistant) -> bool:
    """Check if debug logging is enabled."""
    return hass.data.get(DOMAIN, {}).get(DEBUG_ENABLED, False)


def debug_log(hass: HomeAssistant, message: str, *args: Any) -> None:
    """Log a debug message if debug logging is enabled."""
    if is_debug_enabled(hass):
        _LOGGER.warning("[DEBUG] " + message, *args)


def debug_log_data(hass: HomeAssistant, label: str, data: Any) -> None:
    """Log data in a formatted way if debug logging is enabled."""
    if is_debug_enabled(hass):
        import json
        try:
            if isinstance(data, (dict, list)):
                # Truncate large data
                data_str = json.dumps(data, indent=2, default=str)
                if len(data_str) > 5000:
                    data_str = data_str[:5000] + "\n... (truncated)"
                _LOGGER.warning("[DEBUG] %s:\n%s", label, data_str)
            else:
                _LOGGER.warning("[DEBUG] %s: %s", label, data)
        except Exception as e:
            _LOGGER.warning("[DEBUG] %s: (failed to serialize: %s)", label, e)
