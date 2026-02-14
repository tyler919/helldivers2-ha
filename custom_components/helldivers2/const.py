"""Constants for the Helldivers 2 integration."""

DOMAIN = "helldivers2"

# API URLs
API_BASE_URL = "https://helldiverstrainingmanual.com/api/v1"
API_WAR_STATUS = f"{API_BASE_URL}/war/status"
API_WAR_CAMPAIGN = f"{API_BASE_URL}/war/campaign"
API_WAR_INFO = f"{API_BASE_URL}/war/info"
API_MAJOR_ORDERS = f"{API_BASE_URL}/war/major-orders"
API_WAR_NEWS = f"{API_BASE_URL}/war/news"
API_PLANETS = f"{API_BASE_URL}/planets"

# Update interval (seconds)
DEFAULT_SCAN_INTERVAL = 60

# Faction IDs
FACTION_HUMANS = 1
FACTION_TERMINIDS = 2
FACTION_AUTOMATONS = 3
FACTION_ILLUMINATE = 4

FACTION_NAMES = {
    FACTION_HUMANS: "Humans",
    FACTION_TERMINIDS: "Terminids",
    FACTION_AUTOMATONS: "Automatons",
    FACTION_ILLUMINATE: "Illuminate",
}

# Configuration
CONF_UPDATE_INTERVAL = "update_interval"
