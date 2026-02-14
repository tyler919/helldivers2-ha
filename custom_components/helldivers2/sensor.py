"""Sensor platform for Helldivers 2 integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
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
# Value Functions - War Statistics
# =============================================================================

def get_total_players(data: dict[str, Any]) -> int:
    """Get total player count."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("playerCount", 0)
    return 0


def get_missions_won(data: dict[str, Any]) -> int:
    """Get total missions won."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("missionsWon", 0)
    return 0


def get_missions_lost(data: dict[str, Any]) -> int:
    """Get total missions lost."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("missionsLost", 0)
    return 0


def get_mission_success_rate(data: dict[str, Any]) -> int:
    """Get mission success rate."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("missionSuccessRate", 0)
    return 0


def get_terminid_kills(data: dict[str, Any]) -> int:
    """Get total Terminid kills."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("terminidKills", 0)
    return 0


def get_automaton_kills(data: dict[str, Any]) -> int:
    """Get total Automaton kills."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("automatonKills", 0)
    return 0


def get_illuminate_kills(data: dict[str, Any]) -> int:
    """Get total Illuminate kills."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("illuminateKills", 0)
    return 0


def get_total_deaths(data: dict[str, Any]) -> int:
    """Get total Helldiver deaths."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("deaths", 0)
    return 0


def get_friendly_kills(data: dict[str, Any]) -> int:
    """Get total friendly fire incidents."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("friendlies", 0)
    return 0


def get_bullets_fired(data: dict[str, Any]) -> int:
    """Get total bullets fired."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("bulletsFired", 0)
    return 0


def get_bullets_hit(data: dict[str, Any]) -> int:
    """Get total bullets hit."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("bulletsHit", 0)
    return 0


def get_accuracy(data: dict[str, Any]) -> int:
    """Get accuracy percentage."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        stats = war.get("statistics", {})
        if stats and isinstance(stats, dict):
            return stats.get("accuracy", 0)
    return 0


# =============================================================================
# Value Functions - Campaigns & Planets
# =============================================================================

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


def get_hottest_planet(data: dict[str, Any]) -> str:
    """Get planet with most players."""
    campaigns = data.get("campaigns", [])
    if not campaigns or not isinstance(campaigns, list):
        return "Unknown"

    hottest = None
    max_players = 0

    for campaign in campaigns:
        if isinstance(campaign, dict):
            planet = campaign.get("planet", {})
            if isinstance(planet, dict):
                stats = planet.get("statistics", {})
                if isinstance(stats, dict):
                    players = stats.get("playerCount", 0)
                    if players > max_players:
                        max_players = players
                        hottest = planet

    if hottest:
        return hottest.get("name", "Unknown")
    return "Unknown"


def get_hottest_planet_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get hottest planet attributes."""
    campaigns = data.get("campaigns", [])
    if not campaigns or not isinstance(campaigns, list):
        return {}

    hottest = None
    max_players = 0

    for campaign in campaigns:
        if isinstance(campaign, dict):
            planet = campaign.get("planet", {})
            if isinstance(planet, dict):
                stats = planet.get("statistics", {})
                if isinstance(stats, dict):
                    players = stats.get("playerCount", 0)
                    if players > max_players:
                        max_players = players
                        hottest = planet

    if hottest:
        stats = hottest.get("statistics", {}) if isinstance(hottest.get("statistics"), dict) else {}
        biome = hottest.get("biome", {}) if isinstance(hottest.get("biome"), dict) else {}
        hazards = hottest.get("hazards", [])
        hazard_names = [h.get("name", "") for h in hazards if isinstance(h, dict)]

        return {
            "players": stats.get("playerCount", 0),
            "liberation": hottest.get("liberation", 0),
            "owner": hottest.get("currentOwner", "Unknown"),
            "sector": hottest.get("sector", "Unknown"),
            "biome": biome.get("name", "Unknown"),
            "hazards": ", ".join(hazard_names) if hazard_names else "None",
            "mission_success_rate": stats.get("missionSuccessRate", 0),
        }
    return {}


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
                        "sector": planet.get("sector", "Unknown"),
                    })
        planets.sort(key=lambda x: x.get("players", 0), reverse=True)
    return {"active_campaigns": planets[:15]}


# =============================================================================
# Value Functions - Major Orders
# =============================================================================

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
            reward = order.get("reward", {})
            return {
                "description": order.get("description", ""),
                "briefing": order.get("briefing", ""),
                "expiration": order.get("expiration", ""),
                "progress": order.get("progress", []),
                "reward_type": reward.get("type", "") if isinstance(reward, dict) else "",
                "reward_amount": reward.get("amount", 0) if isinstance(reward, dict) else 0,
            }
    return {}


def get_major_order_progress(data: dict[str, Any]) -> str:
    """Get major order progress."""
    assignments = data.get("assignments", [])
    if assignments and isinstance(assignments, list) and len(assignments) > 0:
        order = assignments[0]
        if isinstance(order, dict):
            progress = order.get("progress", [])
            tasks = order.get("tasks", [])

            if progress and isinstance(progress, list) and len(progress) > 0:
                current = progress[0] if progress else 0

                # Try to get target from tasks
                target = 0
                if tasks and isinstance(tasks, list) and len(tasks) > 0:
                    task = tasks[0]
                    if isinstance(task, dict):
                        values = task.get("values", [])
                        if isinstance(values, list) and len(values) > 2:
                            target = values[2]  # Usually the target is at index 2

                if target > 0:
                    return f"{current:,} / {target:,}"
                return f"{current:,}"
    return "No Progress"


def get_major_order_expiration(data: dict[str, Any]) -> str:
    """Get major order time remaining."""
    assignments = data.get("assignments", [])
    if assignments and isinstance(assignments, list) and len(assignments) > 0:
        order = assignments[0]
        if isinstance(order, dict):
            expiration = order.get("expiration", "")
            if expiration:
                try:
                    exp_time = datetime.fromisoformat(expiration.replace("Z", "+00:00"))
                    now = datetime.now(exp_time.tzinfo)
                    delta = exp_time - now
                    if delta.total_seconds() > 0:
                        days = delta.days
                        hours = delta.seconds // 3600
                        minutes = (delta.seconds % 3600) // 60
                        if days > 0:
                            return f"{days}d {hours}h"
                        return f"{hours}h {minutes}m"
                except (ValueError, TypeError):
                    return expiration[:19]
    return "No Order"


def get_major_order_reward(data: dict[str, Any]) -> str:
    """Get major order reward."""
    assignments = data.get("assignments", [])
    if assignments and isinstance(assignments, list) and len(assignments) > 0:
        order = assignments[0]
        if isinstance(order, dict):
            reward = order.get("reward", {})
            if isinstance(reward, dict):
                amount = reward.get("amount", 0)
                reward_type = reward.get("type", 1)
                type_name = "Medals" if reward_type == 1 else "Super Credits" if reward_type == 2 else "Reward"
                return f"{amount} {type_name}"
    return "None"


# =============================================================================
# Value Functions - News & Dispatches
# =============================================================================

def get_latest_news(data: dict[str, Any]) -> str:
    """Get latest news headline."""
    dispatches = data.get("dispatches", [])
    if dispatches and isinstance(dispatches, list) and len(dispatches) > 0:
        item = dispatches[0]
        if isinstance(item, dict):
            message = item.get("message", "No News")
            # Strip HTML-like tags
            import re
            clean = re.sub(r'<[^>]+>', '', message)
            return clean[:255] if clean else "No News"
    return "No News"


def get_news_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get news attributes."""
    import re
    dispatches = data.get("dispatches", [])
    items = []
    if dispatches and isinstance(dispatches, list):
        for item in dispatches[:10]:
            if isinstance(item, dict):
                message = item.get("message", "")
                clean = re.sub(r'<[^>]+>', '', message)
                items.append({
                    "message": clean,
                    "published": item.get("published", ""),
                })
    return {"recent_news": items}


# =============================================================================
# Value Functions - Steam/Patches
# =============================================================================

def get_latest_patch(data: dict[str, Any]) -> str:
    """Get latest patch title."""
    steam = data.get("steam", [])
    if steam and isinstance(steam, list) and len(steam) > 0:
        item = steam[0]
        if isinstance(item, dict):
            return item.get("title", "Unknown")[:255]
    return "Unknown"


def get_patch_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get patch attributes."""
    steam = data.get("steam", [])
    if steam and isinstance(steam, list) and len(steam) > 0:
        item = steam[0]
        if isinstance(item, dict):
            return {
                "author": item.get("author", ""),
                "published": item.get("publishedAt", ""),
                "url": item.get("url", ""),
            }
    return {}


def get_game_version(data: dict[str, Any]) -> str:
    """Get current game client version."""
    war = data.get("war", {})
    if war and isinstance(war, dict):
        return war.get("clientVersion", "Unknown")
    return "Unknown"


# =============================================================================
# Value Functions - Faction Stats
# =============================================================================

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
                "bullets_hit": stats.get("bulletsHit", 0),
                "deaths": stats.get("deaths", 0),
                "friendlies": stats.get("friendlies", 0),
                "accuracy": stats.get("accuracy", 0),
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
    Helldivers2SensorEntityDescription(
        key="hottest_planet",
        name="Hottest Planet",
        icon="mdi:fire",
        value_fn=get_hottest_planet,
        attr_fn=get_hottest_planet_attrs,
    ),

    # War Statistics
    Helldivers2SensorEntityDescription(
        key="missions_won",
        name="Missions Won",
        icon="mdi:trophy",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_missions_won,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="missions_lost",
        name="Missions Lost",
        icon="mdi:trophy-broken",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_missions_lost,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="mission_success_rate",
        name="Mission Success Rate",
        icon="mdi:percent",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        value_fn=get_mission_success_rate,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="terminid_kills",
        name="Terminid Kills",
        icon="mdi:bug",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_terminid_kills,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="automaton_kills",
        name="Automaton Kills",
        icon="mdi:robot",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_automaton_kills,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="illuminate_kills",
        name="Illuminate Kills",
        icon="mdi:alien",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_illuminate_kills,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="total_deaths",
        name="Total Deaths",
        icon="mdi:skull",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_total_deaths,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="friendly_kills",
        name="Friendly Fire Incidents",
        icon="mdi:account-alert",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_friendly_kills,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="bullets_fired",
        name="Bullets Fired",
        icon="mdi:ammunition",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_bullets_fired,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="accuracy",
        name="Accuracy",
        icon="mdi:target",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        value_fn=get_accuracy,
        attr_fn=None,
    ),

    # Major Order
    Helldivers2SensorEntityDescription(
        key="major_order",
        name="Major Order",
        icon="mdi:clipboard-text",
        value_fn=get_major_order_title,
        attr_fn=get_major_order_attrs,
    ),
    Helldivers2SensorEntityDescription(
        key="major_order_progress",
        name="Major Order Progress",
        icon="mdi:progress-clock",
        value_fn=get_major_order_progress,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="major_order_expiration",
        name="Major Order Time Left",
        icon="mdi:timer-sand",
        value_fn=get_major_order_expiration,
        attr_fn=None,
    ),
    Helldivers2SensorEntityDescription(
        key="major_order_reward",
        name="Major Order Reward",
        icon="mdi:medal",
        value_fn=get_major_order_reward,
        attr_fn=None,
    ),

    # News
    Helldivers2SensorEntityDescription(
        key="latest_news",
        name="Latest News",
        icon="mdi:newspaper",
        value_fn=get_latest_news,
        attr_fn=get_news_attrs,
    ),

    # Steam/Patches
    Helldivers2SensorEntityDescription(
        key="latest_patch",
        name="Latest Patch",
        icon="mdi:update",
        value_fn=get_latest_patch,
        attr_fn=get_patch_attrs,
    ),
    Helldivers2SensorEntityDescription(
        key="game_version",
        name="Game Version",
        icon="mdi:gamepad-variant",
        value_fn=get_game_version,
        attr_fn=None,
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
