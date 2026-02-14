"""Sensor platform for Helldivers 2 integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Helldivers2Coordinator


@dataclass(frozen=True)
class Helldivers2SensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[dict[str, Any]], Any]
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None


@dataclass(frozen=True)
class Helldivers2SensorEntityDescription(
    SensorEntityDescription, Helldivers2SensorEntityDescriptionMixin
):
    """Describes a Helldivers 2 sensor entity."""


# =============================================================================
# Value Functions
# =============================================================================

def get_total_players(data: dict[str, Any]) -> int:
    """Get total player count."""
    # Try stats first, then status
    players = data.get("stats", {}).get("total_players", 0)
    if not players:
        status = data.get("status")
        if status and isinstance(status, dict):
            players = status.get("player_count", 0)
    return players or 0


def get_active_planets(data: dict[str, Any]) -> int:
    """Get active planet count."""
    return data.get("stats", {}).get("active_planets", 0)


def get_avg_liberation(data: dict[str, Any]) -> float:
    """Get average liberation percentage."""
    return data.get("stats", {}).get("liberation_avg", 0)


def get_major_order_title(data: dict[str, Any]) -> str:
    """Get current major order title."""
    orders = data.get("major_orders")
    if orders and isinstance(orders, list) and len(orders) > 0:
        order = orders[0]
        if isinstance(order, dict):
            return order.get("title", order.get("brief", "No Active Order"))[:255]
    return "No Active Order"


def get_major_order_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get major order attributes."""
    orders = data.get("major_orders")
    if orders and isinstance(orders, list) and len(orders) > 0:
        order = orders[0]
        if isinstance(order, dict):
            return {
                "description": order.get("description", order.get("brief", "")),
                "reward_amount": order.get("reward", {}).get("amount", 0) if isinstance(order.get("reward"), dict) else 0,
                "reward_type": order.get("reward", {}).get("type", "") if isinstance(order.get("reward"), dict) else "",
                "expires": order.get("expires", order.get("expiration", "")),
                "progress": order.get("progress", []),
            }
    return {}


def get_latest_news(data: dict[str, Any]) -> str:
    """Get latest news headline."""
    news = data.get("news")
    if news and isinstance(news, list) and len(news) > 0:
        item = news[-1] if isinstance(news[-1], dict) else news[0]
        if isinstance(item, dict):
            return item.get("message", item.get("title", "No News"))[:255]
    return "No News"


def get_news_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get news attributes."""
    news = data.get("news")
    items = []
    if news and isinstance(news, list):
        for item in news[-5:]:
            if isinstance(item, dict):
                items.append({
                    "message": item.get("message", item.get("title", "")),
                    "published": item.get("published", item.get("timestamp", "")),
                })
    return {"recent_news": items}


def get_store_expiration(data: dict[str, Any]) -> str:
    """Get store rotation expiration."""
    store = data.get("store_rotation")
    if store and isinstance(store, dict):
        return store.get("expiration", store.get("expires", "Unknown"))
    return "Unknown"


def get_store_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get store rotation attributes."""
    store = data.get("store_rotation")
    if store and isinstance(store, dict):
        items = store.get("items", [])
        return {
            "items": items[:10] if isinstance(items, list) else [],
            "item_count": len(items) if isinstance(items, list) else 0,
        }
    return {"items": [], "item_count": 0}


def get_top_player(data: dict[str, Any]) -> str:
    """Get top player name."""
    leaderboard = data.get("player_leaderboard")
    if leaderboard and isinstance(leaderboard, list) and len(leaderboard) > 0:
        player = leaderboard[0]
        if isinstance(player, dict):
            return player.get("name", player.get("player_name", "Unknown"))
    return "Unknown"


def get_player_leaderboard_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get player leaderboard attributes."""
    leaderboard = data.get("player_leaderboard")
    if leaderboard and isinstance(leaderboard, list):
        top_10 = []
        for i, player in enumerate(leaderboard[:10]):
            if isinstance(player, dict):
                top_10.append({
                    "rank": i + 1,
                    "name": player.get("name", player.get("player_name", "Unknown")),
                    "score": player.get("score", player.get("kills", 0)),
                })
        return {"top_players": top_10}
    return {"top_players": []}


def get_top_clan(data: dict[str, Any]) -> str:
    """Get top clan name."""
    leaderboard = data.get("clan_leaderboard")
    if leaderboard and isinstance(leaderboard, list) and len(leaderboard) > 0:
        clan = leaderboard[0]
        if isinstance(clan, dict):
            return clan.get("name", clan.get("clan_name", "Unknown"))
    return "Unknown"


def get_clan_leaderboard_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get clan leaderboard attributes."""
    leaderboard = data.get("clan_leaderboard")
    if leaderboard and isinstance(leaderboard, list):
        top_10 = []
        for i, clan in enumerate(leaderboard[:10]):
            if isinstance(clan, dict):
                top_10.append({
                    "rank": i + 1,
                    "name": clan.get("name", clan.get("clan_name", "Unknown")),
                    "score": clan.get("score", clan.get("exp", 0)),
                    "members": clan.get("members", clan.get("member_count", 0)),
                })
        return {"top_clans": top_10}
    return {"top_clans": []}


def get_election_status(data: dict[str, Any]) -> str:
    """Get election status."""
    candidates = data.get("election_candidates")
    if candidates and isinstance(candidates, list) and len(candidates) > 0:
        return f"{len(candidates)} Candidates"
    return "No Election"


def get_election_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get election attributes."""
    candidates = data.get("election_candidates")
    if candidates and isinstance(candidates, list):
        return {"candidates": candidates[:10]}
    return {"candidates": []}


def get_faction_players(faction: str) -> Callable[[dict[str, Any]], int]:
    """Get player count for a specific faction."""
    def _get_players(data: dict[str, Any]) -> int:
        return data.get("stats", {}).get("players_by_faction", {}).get(faction, 0)
    return _get_players


def get_faction_planets(faction: str) -> Callable[[dict[str, Any]], int]:
    """Get planet count for a specific faction."""
    def _get_planets(data: dict[str, Any]) -> int:
        return data.get("stats", {}).get("planets_by_faction", {}).get(faction, 0)
    return _get_planets


def get_campaign_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get campaign attributes with planet details."""
    planet_stats = data.get("planet_stats")
    planets = []
    if planet_stats and isinstance(planet_stats, dict):
        planets_data = planet_stats.get("planets", [])
        if isinstance(planets_data, list):
            active = [p for p in planets_data if isinstance(p, dict) and p.get("players", 0) > 0]
            for planet in sorted(active, key=lambda x: x.get("players", 0), reverse=True)[:15]:
                planets.append({
                    "name": planet.get("name", "Unknown"),
                    "players": planet.get("players", 0),
                    "liberation": planet.get("liberation", 0),
                    "owner": planet.get("owner", "Unknown"),
                })
    return {"active_campaigns": planets}


# =============================================================================
# Sensor Definitions
# =============================================================================

SENSOR_DESCRIPTIONS: tuple[Helldivers2SensorEntityDescription, ...] = (
    # Core Stats
    Helldivers2SensorEntityDescription(
        key="total_players",
        name="Total Players",
        icon="mdi:account-group",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="players",
        value_fn=get_total_players,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="active_planets",
        name="Active Planets",
        icon="mdi:earth",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="planets",
        value_fn=get_active_planets,
        attr_fn=get_campaign_attrs,
    ),
    Helldivers2SensorEntityDescription(
        key="average_liberation",
        name="Average Liberation",
        icon="mdi:progress-check",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        value_fn=get_avg_liberation,
        attr_fn=None,
    ),
    # Orders & News
    Helldivers2SensorEntityDescription(
        key="major_order",
        name="Major Order",
        icon="mdi:clipboard-text",
        value_fn=get_major_order_title,
        attr_fn=get_major_order_attrs,
    ),
    Helldivers2SensorEntityDescription(
        key="latest_news",
        name="Latest News",
        icon="mdi:newspaper",
        value_fn=get_latest_news,
        attr_fn=get_news_attrs,
    ),
    # Store
    Helldivers2SensorEntityDescription(
        key="store_rotation",
        name="Store Rotation",
        icon="mdi:store",
        value_fn=get_store_expiration,
        attr_fn=get_store_attrs,
    ),
    # Leaderboards
    Helldivers2SensorEntityDescription(
        key="top_player",
        name="Top Player",
        icon="mdi:trophy",
        value_fn=get_top_player,
        attr_fn=get_player_leaderboard_attrs,
    ),
    Helldivers2SensorEntityDescription(
        key="top_clan",
        name="Top Clan",
        icon="mdi:account-group-outline",
        value_fn=get_top_clan,
        attr_fn=get_clan_leaderboard_attrs,
    ),
    # Elections
    Helldivers2SensorEntityDescription(
        key="election_status",
        name="Election Status",
        icon="mdi:vote",
        value_fn=get_election_status,
        attr_fn=get_election_attrs,
    ),
    # Faction Players
    Helldivers2SensorEntityDescription(
        key="terminid_players",
        name="Terminid Front Players",
        icon="mdi:bug",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="players",
        value_fn=get_faction_players("Terminids"),
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="automaton_players",
        name="Automaton Front Players",
        icon="mdi:robot",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="players",
        value_fn=get_faction_players("Automatons"),
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="illuminate_players",
        name="Illuminate Front Players",
        icon="mdi:alien",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="players",
        value_fn=get_faction_players("Illuminate"),
        attr_fn=None,
    ),
    # Faction Planets
    Helldivers2SensorEntityDescription(
        key="terminid_planets",
        name="Terminid Front Planets",
        icon="mdi:bug",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="planets",
        value_fn=get_faction_planets("Terminids"),
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="automaton_planets",
        name="Automaton Front Planets",
        icon="mdi:robot",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="planets",
        value_fn=get_faction_planets("Automatons"),
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="illuminate_planets",
        name="Illuminate Front Planets",
        icon="mdi:alien",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="planets",
        value_fn=get_faction_planets("Illuminate"),
        attr_fn=None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Helldivers 2 sensors based on a config entry."""
    coordinator: Helldivers2Coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        Helldivers2Sensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class Helldivers2Sensor(CoordinatorEntity[Helldivers2Coordinator], SensorEntity):
    """Representation of a Helldivers 2 sensor."""

    entity_description: Helldivers2SensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Helldivers2Coordinator,
        description: Helldivers2SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"helldivers2_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "helldivers2")},
            "name": "Helldivers 2",
            "manufacturer": "Arrowhead Game Studios",
            "model": "Galactic War",
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if self.coordinator.data is None or self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator.data)
