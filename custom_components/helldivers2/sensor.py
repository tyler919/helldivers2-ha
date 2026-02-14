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


def get_total_players(data: dict[str, Any]) -> int:
    """Get total player count."""
    return data.get("stats", {}).get("total_players", 0)


def get_active_planets(data: dict[str, Any]) -> int:
    """Get active planet count."""
    return data.get("stats", {}).get("active_planets", 0)


def get_avg_liberation(data: dict[str, Any]) -> float:
    """Get average liberation percentage."""
    return data.get("stats", {}).get("liberation_avg", 0)


def get_major_order_title(data: dict[str, Any]) -> str:
    """Get current major order title."""
    orders = data.get("major_orders", [])
    if orders and isinstance(orders, list) and len(orders) > 0:
        order = orders[0]
        if isinstance(order, dict):
            return order.get("title", "No Active Order")
    return "No Active Order"


def get_major_order_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get major order attributes."""
    orders = data.get("major_orders", [])
    if orders and isinstance(orders, list) and len(orders) > 0:
        order = orders[0]
        if isinstance(order, dict):
            return {
                "description": order.get("description", ""),
                "reward_amount": order.get("reward", {}).get("amount", 0),
                "reward_type": order.get("reward", {}).get("type", ""),
                "expires": order.get("expires", ""),
            }
    return {}


def get_latest_news(data: dict[str, Any]) -> str:
    """Get latest news headline."""
    news = data.get("news", [])
    if news and isinstance(news, list) and len(news) > 0:
        # News is oldest to newest, so get the last item
        item = news[-1]
        if isinstance(item, dict):
            return item.get("message", "No News")[:255]
    return "No News"


def get_news_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Get news attributes."""
    news = data.get("news", [])
    items = []
    if news and isinstance(news, list):
        for item in news[-5:]:  # Last 5 news items
            if isinstance(item, dict):
                items.append({
                    "message": item.get("message", ""),
                    "published": item.get("published", ""),
                })
    return {"recent_news": items}


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
    campaign = data.get("campaign", [])
    planets = []
    if campaign and isinstance(campaign, list):
        for planet in campaign[:10]:  # Top 10 planets
            if isinstance(planet, dict):
                planets.append({
                    "name": planet.get("name", "Unknown"),
                    "players": planet.get("players", 0),
                    "liberation": planet.get("liberation", 0),
                    "faction": planet.get("faction", "Unknown"),
                })
    return {"active_campaigns": planets}


SENSOR_DESCRIPTIONS: tuple[Helldivers2SensorEntityDescription, ...] = (
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
