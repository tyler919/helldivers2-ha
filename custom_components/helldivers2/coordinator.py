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
    API_STATUS,
    API_MAJOR_ORDER,
    API_NEWS_FEED,
    API_PLANET_STATS,
    API_STORE_ROTATION,
    API_PLANETS,
    API_PLAYER_LEADERBOARD,
    API_CLAN_LEADERBOARD,
    API_ELECTION_CANDIDATES,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
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
                results = await asyncio.gather(
                    self._fetch_json(API_STATUS),
                    self._fetch_json(API_PLANET_STATS),
                    self._fetch_json(API_MAJOR_ORDER),
                    self._fetch_json(API_NEWS_FEED),
                    self._fetch_json(API_STORE_ROTATION),
                    self._fetch_json(API_PLANETS),
                    self._fetch_json(API_PLAYER_LEADERBOARD),
                    self._fetch_json(API_CLAN_LEADERBOARD),
                    self._fetch_json(API_ELECTION_CANDIDATES),
                    return_exceptions=True,
                )

            # Unpack results
            (
                status,
                planet_stats,
                major_orders,
                news,
                store_rotation,
                planets,
                player_leaderboard,
                clan_leaderboard,
                election_candidates,
            ) = results

            # Process data
            data: dict[str, Any] = {
                "status": status if not isinstance(status, Exception) else {},
                "planet_stats": planet_stats if not isinstance(planet_stats, Exception) else {},
                "major_orders": major_orders if not isinstance(major_orders, Exception) else [],
                "news": news if not isinstance(news, Exception) else [],
                "store_rotation": store_rotation if not isinstance(store_rotation, Exception) else {},
                "planets": planets if not isinstance(planets, Exception) else [],
                "player_leaderboard": player_leaderboard if not isinstance(player_leaderboard, Exception) else [],
                "clan_leaderboard": clan_leaderboard if not isinstance(clan_leaderboard, Exception) else [],
                "election_candidates": election_candidates if not isinstance(election_candidates, Exception) else [],
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
            if response.status == 204:
                return None
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

        # Get planet stats
        planet_stats = data.get("planet_stats")
        if planet_stats and isinstance(planet_stats, dict):
            planets_data = planet_stats.get("planets", [])
            if isinstance(planets_data, list):
                active_planets = [p for p in planets_data if isinstance(p, dict) and p.get("players", 0) > 0]
                stats["active_planets"] = len(active_planets)

                total_liberation = 0
                faction_planets: dict[str, int] = {}
                faction_players: dict[str, int] = {}

                for planet in active_planets:
                    players = planet.get("players", 0) or 0
                    stats["total_players"] += players

                    liberation = planet.get("liberation", 0) or 0
                    total_liberation += liberation

                    faction = planet.get("owner")
                    if faction:
                        faction_planets[faction] = faction_planets.get(faction, 0) + 1
                        faction_players[faction] = faction_players.get(faction, 0) + players

                if stats["active_planets"] > 0:
                    stats["liberation_avg"] = round(total_liberation / stats["active_planets"], 2)

                stats["planets_by_faction"] = faction_planets
                stats["players_by_faction"] = faction_players

        # Fallback to status data if planet_stats doesn't have what we need
        status = data.get("status")
        if status and isinstance(status, dict) and stats["total_players"] == 0:
            stats["total_players"] = status.get("player_count", 0) or 0

        return stats

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._session:
            await self._session.close()
            self._session = None
