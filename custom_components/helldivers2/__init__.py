"""The Helldivers 2 integration."""
from __future__ import annotations

import logging
import traceback
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
    CONF_ERROR_REPORTING,
    CONF_GITHUB_TOKEN,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import Helldivers2Coordinator
from .issue_reporter import GitHubIssueReporter

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Panel configuration
PANEL_URL = "helldivers2"
PANEL_TITLE = "Helldivers 2"
PANEL_ICON = "mdi:shield-sword"
PANEL_NAME = "helldivers2-panel"
PANEL_REGISTERED = "helldivers2_panel_registered"
ISSUE_REPORTER = "helldivers2_issue_reporter"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Helldivers 2 from a config entry."""
    update_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL)

    # Initialize issue reporter if enabled
    error_reporting = entry.options.get(CONF_ERROR_REPORTING, False)
    github_token = entry.options.get(CONF_GITHUB_TOKEN, "")

    hass.data.setdefault(DOMAIN, {})

    if error_reporting and github_token:
        reporter = GitHubIssueReporter(github_token)
        hass.data[DOMAIN][ISSUE_REPORTER] = reporter
        _LOGGER.info("Error reporting enabled")
    else:
        hass.data[DOMAIN][ISSUE_REPORTER] = None

    try:
        coordinator = Helldivers2Coordinator(hass, update_interval)
        await coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN][entry.entry_id] = coordinator

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        entry.async_on_unload(entry.add_update_listener(async_reload_entry))

        # Register the frontend panel (only once)
        if not hass.data[DOMAIN].get(PANEL_REGISTERED):
            await _async_register_panel(hass)
            hass.data[DOMAIN][PANEL_REGISTERED] = True

        return True

    except Exception as e:
        await _report_error(hass, "SetupError", str(e), traceback.format_exc())
        raise


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
        await _report_error(hass, "PanelRegistrationError", str(e), traceback.format_exc())
        _LOGGER.error("Failed to register panel: %s", e)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
            coordinator: Helldivers2Coordinator = hass.data[DOMAIN].pop(entry.entry_id)
            await coordinator.async_shutdown()

            # Close issue reporter if exists
            reporter = hass.data[DOMAIN].get(ISSUE_REPORTER)
            if reporter:
                await reporter.close()
                hass.data[DOMAIN][ISSUE_REPORTER] = None

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

    except Exception as e:
        await _report_error(hass, "UnloadError", str(e), traceback.format_exc())
        raise


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def _report_error(
    hass: HomeAssistant,
    error_type: str,
    error_message: str,
    error_traceback: str | None = None,
    additional_info: dict[str, Any] | None = None,
) -> None:
    """Report an error to GitHub if error reporting is enabled."""
    try:
        reporter = hass.data.get(DOMAIN, {}).get(ISSUE_REPORTER)
        if reporter:
            info = additional_info or {}
            info["ha_version"] = hass.config.version
            await reporter.report_error(
                error_type=error_type,
                error_message=error_message,
                traceback=error_traceback,
                additional_info=info,
            )
    except Exception as e:
        _LOGGER.debug("Failed to report error: %s", e)


# Export the report_error function for use by other modules
def get_error_reporter(hass: HomeAssistant) -> GitHubIssueReporter | None:
    """Get the error reporter instance."""
    return hass.data.get(DOMAIN, {}).get(ISSUE_REPORTER)
