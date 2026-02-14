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
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("playerCount", 0)
    return 0


def get_active_planets(data: dict[str, Any]) -> int:
    """Get active planet count."""
    campaigns = data.get("campaigns", [])
    return len(campaigns) if isinstance(campaigns, list) else 0


def get_avg_liberation(data: dict[str, Any]) -> float:
    """Get average liberation percentage."""
    campaigns = data.get("campaigns", [])
    if not campaigns or not isinstance(campaigns, list):
        return 0

    total = 0
    count = 0
    for campaign in campaigns:
        if isinstance(campaign, dict):
            planet = campaign.get("planet", {})
            if isinstance(planet, dict):
                lib = planet.get("liberation", 0)
                if lib:
                    total += lib
                    count += 1

    return round(total / count, 2) if count > 0 else 0


def get_major_order_title(data: dict[str, Any]) -> str:
    """Get current major order title."""
    assignments = data.get("assignments", [])
    if assignments and isinstance(assignments, list) and len(assignments) > 0:
        order = assignments[0]
        if isinstance(order, dict):
            briefing = order.get("briefing", "")
            if briefing:
                return briefing[:255]
            title = order.get("title", "No Active Order")
            return title[:255] if title else "No Active Order"
    return "No Active Order"


def get_major_order_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get major order attributes."""
    assignments = data.get("assignments", [])
    if assignments and isinstance(assignments, list) and len(assignments) > 0:
        order = assignments[0]
        if isinstance(order, dict):
            return {
                "description": order.get("description", ""),
                "briefing": order.get("briefing", ""),
                "expiration": order.get("expiration", ""),
                "progress": order.get("progress", []),
                "reward_type": order.get("reward", {}).get("type", "") if isinstance(order.get("reward"), dict) else "",
                "reward_amount": order.get("reward", {}).get("amount", 0) if isinstance(order.get("reward"), dict) else 0,
            }
    return {}


def get_latest_news(data: dict[str, Any]) -> str:
    """Get latest news headline."""
    dispatches = data.get("dispatches", [])
    if dispatches and isinstance(dispatches, list) and len(dispatches) > 0:
        item = dispatches[0]
        if isinstance(item, dict):
            message = item.get("message", "No News")
            return message[:255] if message else "No News"
    return "No News"


def get_news_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get news attributes."""
    dispatches = data.get("dispatches", [])
    items = []
    if dispatches and isinstance(dispatches, list):
        for item in dispatches[:5]:
            if isinstance(item, dict):
                items.append({
                    "message": item.get("message", ""),
                    "published": item.get("published", ""),
                })
    return {"recent_news": items}


def get_faction_players(faction: str) -> Callable[[dict[str, Any]], int]:
    """Get player count for a specific faction."""
    def _get_players(data: dict[str, Any]) -> int:
        campaigns = data.get("campaigns", [])
        total = 0
        if campaigns and isinstance(campaigns, list):
            for campaign in campaigns:
                if isinstance(campaign, dict):
                    planet = campaign.get("planet", {})
                    if isinstance(planet, dict):
                        owner = planet.get("currentOwner", "")
                        if owner == faction:
                            stats = planet.get("statistics", {})
                            if isinstance(stats, dict):
                                total += stats.get("playerCount", 0)
        return total
    return _get_players


def get_faction_planets(faction: str) -> Callable[[dict[str, Any]], int]:
    """Get planet count for a specific faction."""
    def _get_planets(data: dict[str, Any]) -> int:
        campaigns = data.get("campaigns", [])
        count = 0
        if campaigns and isinstance(campaigns, list):
            for campaign in campaigns:
                if isinstance(campaign, dict):
                    planet = campaign.get("planet", {})
                    if isinstance(planet, dict):
                        owner = planet.get("currentOwner", "")
                        if owner == faction:
                            count += 1
        return count
    return _get_planets


def get_campaign_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get campaign attributes with planet details."""
    campaigns = data.get("campaigns", [])
    planets = []
    if campaigns and isinstance(campaigns, list):
        for campaign in campaigns:
            if isinstance(campaign, dict):
                planet = campaign.get("planet", {})
                if isinstance(planet, dict):
                    stats = planet.get("statistics", {}) if isinstance(planet.get("statistics"), dict) else {}
                    planets.append({
                        "name": planet.get("name", "Unknown"),
                        "players": stats.get("playerCount", 0),
                        "liberation": planet.get("liberation", 0),
                        "owner": planet.get("currentOwner", "Unknown"),
                    })
        # Sort by player count
        planets.sort(key=lambda x: x.get("players", 0), reverse=True)
    return {"active_campaigns": planets[:15]}


def get_war_stats_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get war statistics attributes."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return {
                "missions_won": stats.get("missionsWon", 0),
                "missions_lost": stats.get("missionsLost", 0),
                "mission_success_rate": stats.get("missionSuccessRate", 0),
                "terminid_kills": stats.get("terminidKills", 0),
                "automaton_kills": stats.get("automatonKills", 0),
                "illuminate_kills": stats.get("illuminateKills", 0),
                "bullets_fired": stats.get("bulletsFired", 0),
                "deaths": stats.get("deaths", 0),
                "friendlies": stats.get("friendlies", 0),
            }
    return {}


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
        attr_fn=get_war_stats_attrs,
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
        value_fn=get_faction_players("Automaton"),
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
        value_fn=get_faction_planets("Automaton"),
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
