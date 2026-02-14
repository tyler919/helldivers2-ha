"""Data coordinator for Helldivers 2 integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_MAJOR_ORDERS,
    API_WAR_CAMPAIGN,
    API_WAR_NEWS,
    API_WAR_STATUS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    FACTION_NAMES,
)

_LOGGER = logging.getLogger(__name__)


class Helldivers2Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage fetching Helldivers 2 data."""

    def __init__(self, hass: HomeAssistant, update_interval: int = DEFAULT_SCAN_INTERVAL) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self._session: aiohttp.ClientSession | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Helldivers 2 API."""
        try:
            if self._session is None:
                self._session = aiohttp.ClientSession()

            async with asyncio.timeout(30):
                # Fetch all data concurrently
                war_status, campaign, major_orders, news = await asyncio.gather(
                    self._fetch_json(API_WAR_STATUS),
                    self._fetch_json(API_WAR_CAMPAIGN),
                    self._fetch_json(API_MAJOR_ORDERS),
                    self._fetch_json(API_WAR_NEWS),
                    return_exceptions=True,
                )

            # Process data
            data: dict[str, Any] = {
                "war_status": war_status if not isinstance(war_status, Exception) else {},
                "campaign": campaign if not isinstance(campaign, Exception) else [],
                "major_orders": major_orders if not isinstance(major_orders, Exception) else [],
                "news": news if not isinstance(news, Exception) else [],
            }

            # Calculate aggregated stats
            data["stats"] = self._calculate_stats(data)

            return data

        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout fetching Helldivers 2 data") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching Helldivers 2 data: {err}") from err

    async def _fetch_json(self, url: str) -> Any:
        """Fetch JSON data from a URL."""
        assert self._session is not None
        async with self._session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    def _calculate_stats(self, data: dict[str, Any]) -> dict[str, Any]:
        """Calculate aggregated statistics from the raw data."""
        stats: dict[str, Any] = {
            "total_players": 0,
            "active_planets": 0,
            "planets_by_faction": {},
            "players_by_faction": {},
            "liberation_avg": 0,
        }

        campaign = data.get("campaign", [])
        if not campaign or not isinstance(campaign, list):
            return stats

        stats["active_planets"] = len(campaign)

        total_liberation = 0
        faction_planets: dict[int, int] = {}
        faction_players: dict[int, int] = {}

        for planet in campaign:
            if not isinstance(planet, dict):
                continue

            # Player count
            players = planet.get("players", 0) or 0
            stats["total_players"] += players

            # Liberation percentage
            liberation = planet.get("liberation", 0) or 0
            total_liberation += liberation

            # Faction stats
            faction = planet.get("faction")
            if faction:
                faction_planets[faction] = faction_planets.get(faction, 0) + 1
                faction_players[faction] = faction_players.get(faction, 0) + players

        # Calculate average liberation
        if stats["active_planets"] > 0:
            stats["liberation_avg"] = round(total_liberation / stats["active_planets"], 2)

        # Convert faction IDs to names
        stats["planets_by_faction"] = {
            FACTION_NAMES.get(k, f"Unknown ({k})"): v
            for k, v in faction_planets.items()
        }
        stats["players_by_faction"] = {
            FACTION_NAMES.get(k, f"Unknown ({k})"): v
            for k, v in faction_players.items()
        }

        return stats

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._session:
            await self._session.close()
            self._session = None
