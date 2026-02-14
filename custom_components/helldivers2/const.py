"""Constants for the Helldivers 2 integration."""

DOMAIN = "helldivers2"

# API URLs - Using helldivers2.dev API
API_BASE_URL = "https://api.helldivers2.dev/api/v1"
API_WAR = f"{API_BASE_URL}/war"
API_PLANETS = f"{API_BASE_URL}/planets"
API_CAMPAIGNS = f"{API_BASE_URL}/campaigns"
API_ASSIGNMENTS = f"{API_BASE_URL}/assignments"
API_DISPATCHES = f"{API_BASE_URL}/dispatches"
API_STEAM = f"{API_BASE_URL}/steam"

# Required API headers
API_HEADERS = {
    "X-Super-Client": "helldivers2-ha",
    "X-Super-Contact": "github.com/tyler919/helldivers2-ha",
}

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
