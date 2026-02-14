"""Constants for the Helldivers 2 integration."""

DOMAIN = "helldivers2"

# API URLs - Using Diveharder API (more comprehensive)
API_BASE_URL = "https://api.diveharder.com"
API_ALL = f"{API_BASE_URL}/v1/all"
API_STATUS = f"{API_BASE_URL}/v1/status"
API_WAR_INFO = f"{API_BASE_URL}/v1/war_info"
API_PLANET_STATS = f"{API_BASE_URL}/v1/planet_stats"
API_MAJOR_ORDER = f"{API_BASE_URL}/v1/major_order"
API_PERSONAL_ORDER = f"{API_BASE_URL}/v1/personal_order"
API_NEWS_FEED = f"{API_BASE_URL}/v1/news_feed"
API_UPDATES = f"{API_BASE_URL}/v1/updates"
API_STORE_ROTATION = f"{API_BASE_URL}/v1/store_rotation"
API_PLANETS = f"{API_BASE_URL}/v1/planets"
API_WARBONDS = f"{API_BASE_URL}/v1/warbonds"
API_FACTIONS = f"{API_BASE_URL}/v1/factions"
API_ITEMS = f"{API_BASE_URL}/v1/items"
API_PLAYER_LEADERBOARD = f"{API_BASE_URL}/v1/player_leaderboard"
API_CLAN_LEADERBOARD = f"{API_BASE_URL}/v1/clan_leaderboard"
API_COMMEND_LEADERBOARD = f"{API_BASE_URL}/v1/commend_leaderboard"
API_ELECTION_CANDIDATES = f"{API_BASE_URL}/v1/election_candidates"
API_ELECTION_POLICIES = f"{API_BASE_URL}/v1/election_policies"

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
