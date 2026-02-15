"""Data coordinator for Helldivers 2 integration."""
from __future__ import annotations

import asyncio
import logging
import traceback
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_WAR,
    API_PLANETS,
    API_CAMPAIGNS,
    API_ASSIGNMENTS,
    API_DISPATCHES,
    API_STEAM,
    API_HEADERS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class Helldivers2Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage fetching Helldivers 2 data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
            config_entry=entry,
        )
        self._session: aiohttp.ClientSession | None = None
        # Timeout per endpoint (seconds)
        self._timeout = aiohttp.ClientTimeout(total=20, connect=10)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Helldivers 2 API."""
        from . import debug_log, debug_log_data

        try:
            if self._session is None:
                self._session = aiohttp.ClientSession(headers=API_HEADERS)
                debug_log(self.hass, "Created new aiohttp session with headers: %s", API_HEADERS)

            debug_log(self.hass, "Starting API data fetch...")

            async with asyncio.timeout(60):
                # Fetch all data concurrently
                results = await asyncio.gather(
                    self._fetch_json(API_WAR),
                    self._fetch_json(API_PLANETS),
                    self._fetch_json(API_CAMPAIGNS),
                    self._fetch_json(API_ASSIGNMENTS),
                    self._fetch_json(API_DISPATCHES),
                    self._fetch_json(API_STEAM),
                    return_exceptions=True,
                )

            # Unpack results
            (
                war,
                planets,
                campaigns,
                assignments,
                dispatches,
                steam,
            ) = results

            # Log any errors from individual API calls
            endpoint_names = ["war", "planets", "campaigns", "assignments", "dispatches", "steam"]
            for name, result in zip(endpoint_names, results):
                if isinstance(result, Exception):
                    debug_log(self.hass, "API endpoint '%s' failed: %s", name, str(result))

            # Process data
            data: dict[str, Any] = {
                "war": war if not isinstance(war, Exception) else {},
                "planets": planets if not isinstance(planets, Exception) else [],
                "campaigns": campaigns if not isinstance(campaigns, Exception) else [],
                "assignments": assignments if not isinstance(assignments, Exception) else [],
                "dispatches": dispatches if not isinstance(dispatches, Exception) else [],
                "steam": steam if not isinstance(steam, Exception) else [],
            }

            # Debug log raw API responses
            debug_log_data(self.hass, "API Response - war", data["war"])
            debug_log_data(self.hass, "API Response - assignments (major orders)", data["assignments"])
            debug_log_data(self.hass, "API Response - dispatches (news)", data["dispatches"])
            debug_log(self.hass, "API Response - campaigns count: %d", len(data["campaigns"]) if isinstance(data["campaigns"], list) else 0)
            debug_log(self.hass, "API Response - planets count: %d", len(data["planets"]) if isinstance(data["planets"], list) else 0)

            # Calculate aggregated stats
            data["stats"] = self._calculate_stats(data)
            debug_log_data(self.hass, "Calculated stats", data["stats"])

            debug_log(self.hass, "Data fetch completed successfully")
            return data

        except asyncio.TimeoutError as err:
            debug_log(self.hass, "API request timed out after 60 seconds")
            await self._report_api_error("TimeoutError", "Timeout fetching Helldivers 2 data")
            raise UpdateFailed("Timeout fetching Helldivers 2 data") from err
        except aiohttp.ClientError as err:
            debug_log(self.hass, "API client error: %s", str(err))
            await self._report_api_error("ClientError", str(err), traceback.format_exc())
            raise UpdateFailed(f"Error fetching Helldivers 2 data: {err}") from err

    async def _fetch_json(self, url: str, retries: int = 2) -> Any:
        """Fetch JSON data from a URL with retry logic."""
        assert self._session is not None
        last_error = None

        for attempt in range(retries + 1):
            try:
                async with self._session.get(url, timeout=self._timeout) as response:
                    if response.status == 204:
                        return None
                    response.raise_for_status()
                    return await response.json()
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                last_error = err
                if attempt < retries:
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(2 ** attempt)
                    _LOGGER.debug("Retrying %s (attempt %d/%d)", url, attempt + 2, retries + 1)
                continue

        # All retries failed
        raise last_error if last_error else aiohttp.ClientError("Unknown error")

    def _calculate_stats(self, data: dict[str, Any]) -> dict[str, Any]:
        """Calculate aggregated statistics from the raw data."""
        stats: dict[str, Any] = {
            "total_players": 0,
            "active_planets": 0,
            "planets_by_faction": {},
            "players_by_faction": {},
            "liberation_avg": 0,
        }

        # Get war stats
        war = data.get("war")
        if war and isinstance(war, dict):
            war_stats = war.get("statistics", {})
            if isinstance(war_stats, dict):
                stats["total_players"] = war_stats.get("playerCount", 0)

        # Get planet stats from campaigns
        campaigns = data.get("campaigns")
        planets = data.get("planets")

        if campaigns and isinstance(campaigns, list):
            stats["active_planets"] = len(campaigns)

            total_liberation = 0
            faction_planets: dict[str, int] = {}
            faction_players: dict[str, int] = {}

            # Create planet lookup
            planet_lookup = {}
            if planets and isinstance(planets, list):
                for planet in planets:
                    if isinstance(planet, dict):
                        planet_lookup[planet.get("index")] = planet

            for campaign in campaigns:
                if isinstance(campaign, dict):
                    planet_idx = campaign.get("planet", {}).get("index") if isinstance(campaign.get("planet"), dict) else None
                    planet = campaign.get("planet", {})

                    if isinstance(planet, dict):
                        players = planet.get("statistics", {}).get("playerCount", 0) if isinstance(planet.get("statistics"), dict) else 0
                        liberation = planet.get("liberation", 0)
                        total_liberation += liberation if liberation else 0

                        # Get faction/owner
                        owner = planet.get("currentOwner", "Unknown")
                        if owner:
                            faction_planets[owner] = faction_planets.get(owner, 0) + 1
                            faction_players[owner] = faction_players.get(owner, 0) + players

            if stats["active_planets"] > 0:
                stats["liberation_avg"] = round(total_liberation / stats["active_planets"], 2)

            stats["planets_by_faction"] = faction_planets
            stats["players_by_faction"] = faction_players

        return stats

    async def _report_api_error(
        self,
        error_type: str,
        error_message: str,
        error_traceback: str | None = None,
    ) -> None:
        """Report API errors to GitHub if error reporting is enabled."""
        try:
            from . import get_error_reporter
            reporter = get_error_reporter(self.hass)
            if reporter:
                await reporter.report_error(
                    error_type=f"API_{error_type}",
                    error_message=error_message,
                    traceback=error_traceback,
                    additional_info={
                        "component": "coordinator",
                        "ha_version": self.hass.config.version,
                    },
                )
        except Exception as e:
            _LOGGER.debug("Failed to report API error: %s", e)

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._session:
            await self._session.close()
            self._session = None
