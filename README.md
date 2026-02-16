# Helldivers 2 Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/tyler919/helldivers2-ha)](https://github.com/tyler919/helldivers2-ha/releases)
[![License](https://img.shields.io/github/license/tyler919/helldivers2-ha)](LICENSE)

Track the Helldivers 2 Galactic War status directly in Home Assistant! Monitor player counts, planet liberation, major orders, war statistics, and more.

![Helldivers 2](https://img.shields.io/badge/For%20Super%20Earth!-FFD700?style=for-the-badge)

## Features

- **Custom Sidebar Dashboard** - Beautiful dedicated panel in Home Assistant sidebar
- **26+ Sensors** - Comprehensive tracking of all war statistics
- **Real-time Updates** - Configurable update interval (30-600 seconds)
- **Debug Logging** - Optional detailed logging for troubleshooting
- **Automatic Error Reporting** - Optional GitHub issue reporting for errors
- **Retry Logic** - Automatic retries with exponential backoff for API reliability

### What You Can Track

- **War Statistics** - Missions won/lost, success rate, bullets fired, accuracy
- **Kill Counts** - Terminid, Automaton, and Illuminate kills
- **Player Distribution** - See where Helldivers are fighting
- **Major Orders** - Current objectives, progress, time remaining, rewards
- **Active Campaigns** - All contested planets with liberation progress
- **Hottest Planet** - Most active planet with player count and details
- **Super Earth Dispatches** - Latest in-game news
- **Game Info** - Current version and latest patch notes

## Screenshots

The integration includes a custom sidebar panel with:
- Active Helldiver count by faction
- Major Order progress with countdown timer
- War statistics (missions, deaths, friendly fire)
- Enemy kill counts
- Hottest planet details
- Active campaign list
- Super Earth dispatches

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/tyler919/helldivers2-ha`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "Helldivers 2" and install
8. Restart Home Assistant
9. Go to Settings > Devices & Services > Add Integration > Helldivers 2

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/helldivers2` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant
4. Go to Settings > Devices & Services > Add Integration > Helldivers 2

## Configuration

The integration is configured via the UI. Options include:

| Option | Description | Default |
|--------|-------------|---------|
| **Update Interval** | How often to fetch new data (30-600 seconds) | 60 seconds |
| **Enable Debug Logging** | Log detailed API responses for troubleshooting | Off |
| **Enable Error Reporting** | Automatically report errors to GitHub | Off |
| **GitHub Token** | Personal access token for error reporting | - |

To change options after setup: Settings > Devices & Services > Helldivers 2 > Configure

## Sensors

All sensors are prefixed with `sensor.helldivers_2_`

### Core Stats
| Sensor | Description |
|--------|-------------|
| `total_players` | Total active players across all planets |
| `active_planets` | Number of planets currently being contested |
| `average_liberation` | Average liberation % across all active planets |
| `hottest_planet` | Planet with most players (includes detailed attributes) |

### War Statistics
| Sensor | Description |
|--------|-------------|
| `missions_won` | Total missions won |
| `missions_lost` | Total missions lost |
| `mission_success_rate` | Overall success rate % |
| `total_deaths` | Total Helldiver deaths |
| `friendly_kills` | Friendly fire incidents |
| `bullets_fired` | Total bullets fired |
| `accuracy` | Overall accuracy % |

### Kill Counts
| Sensor | Description |
|--------|-------------|
| `terminid_kills` | Total Terminid kills |
| `automaton_kills` | Total Automaton kills |
| `illuminate_kills` | Total Illuminate kills |

### Major Orders
| Sensor | Description |
|--------|-------------|
| `major_order` | Current major order briefing |
| `major_order_progress` | Progress toward objective |
| `major_order_expiration` | Time remaining |
| `major_order_reward` | Reward amount and type |

### Faction Stats
| Sensor | Description |
|--------|-------------|
| `terminid_players` | Players on Terminid front |
| `automaton_players` | Players on Automaton front |
| `illuminate_players` | Players on Illuminate front |
| `terminid_planets` | Active Terminid planets |
| `automaton_planets` | Active Automaton planets |
| `illuminate_planets` | Active Illuminate planets |

### News & Updates
| Sensor | Description |
|--------|-------------|
| `latest_news` | Most recent Super Earth dispatch |
| `latest_patch` | Latest game patch title |
| `game_version` | Current game client version |

## Custom Dashboard Panel

The integration automatically adds a "Helldivers 2" panel to your Home Assistant sidebar. This dashboard displays:

- Real-time player counts by faction
- Major order progress with visual progress bar
- War statistics overview
- Enemy kill counts
- Hottest planet with details (sector, biome, hazards)
- Active campaign list (top 10 by player count)
- Recent Super Earth dispatches

## Example Lovelace Cards

### Simple Status Card
```yaml
type: entities
title: Helldivers 2 Status
entities:
  - entity: sensor.helldivers_2_total_players
    name: Active Helldivers
  - entity: sensor.helldivers_2_major_order
    name: Major Order
  - entity: sensor.helldivers_2_hottest_planet
    name: Hottest Planet
```

### Faction Overview
```yaml
type: horizontal-stack
cards:
  - type: entity
    entity: sensor.helldivers_2_terminid_players
    name: Terminids
    icon: mdi:bug
  - type: entity
    entity: sensor.helldivers_2_automaton_players
    name: Automatons
    icon: mdi:robot
  - type: entity
    entity: sensor.helldivers_2_illuminate_players
    name: Illuminate
    icon: mdi:alien
```

## Troubleshooting

### Dashboard Not Showing Data
1. Hard refresh your browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. Clear browser cache
3. Try an incognito/private window
4. Check Developer Tools > States for sensors starting with `helldivers_2`

### API Timeouts
The integration includes automatic retry logic (2 retries with exponential backoff). If you see frequent timeouts:
1. Enable debug logging in the integration options
2. Check Home Assistant logs for details
3. The helldivers2.dev API may be experiencing high load

### Debug Logging
To enable detailed logging:
1. Go to Settings > Devices & Services > Helldivers 2 > Configure
2. Enable "Enable debug logging"
3. Restart Home Assistant
4. Check Settings > System > Logs (filter by "helldivers2")

## API Credits

This integration uses the [helldivers2.dev API](https://api.helldivers2.dev), a community-driven API for Helldivers 2 data.

## Disclaimer

This is a fan-made integration and is not affiliated with, endorsed by, or connected to Arrowhead Game Studios or Sony Interactive Entertainment.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Issues and pull requests are welcome! Please report bugs at [GitHub Issues](https://github.com/tyler919/helldivers2-ha/issues).

---

**For Super Earth!**
