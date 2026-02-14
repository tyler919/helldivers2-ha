# Helldivers 2 Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/tyler919/helldivers2-ha)](https://github.com/tyler919/helldivers2-ha/releases)
[![License](https://img.shields.io/github/license/tyler919/helldivers2-ha)](LICENSE)

Track the Helldivers 2 Galactic War status directly in Home Assistant! Monitor player counts, planet liberation, major orders, and more.

![Helldivers 2](https://img.shields.io/badge/For%20Super%20Earth!-FFD700?style=for-the-badge)

## Features

- **Total Player Count** - See how many Helldivers are fighting across the galaxy
- **Active Planets** - Track all active campaign planets with liberation progress
- **Major Orders** - View current major orders and objectives
- **Latest News** - Get in-game news updates
- **Store Rotation** - Track current store items and expiration
- **Leaderboards** - View top players and clans
- **Elections** - Monitor election candidates and status
- **Faction Breakdown** - See player distribution across fronts:
  - Terminid Front (bugs)
  - Automaton Front (robots)
  - Illuminate Front (squids)

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
9. Go to Settings → Devices & Services → Add Integration → Helldivers 2

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/helldivers2` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration → Helldivers 2

## Configuration

The integration is configured via the UI. You can set:

- **Update Interval** - How often to fetch new data (default: 60 seconds, min: 30 seconds)

## Sensors

| Sensor | Description |
|--------|-------------|
| `sensor.helldivers2_total_players` | Total active players across all planets |
| `sensor.helldivers2_active_planets` | Number of planets currently being contested |
| `sensor.helldivers2_average_liberation` | Average liberation % across all active planets |
| `sensor.helldivers2_major_order` | Current major order title |
| `sensor.helldivers2_latest_news` | Most recent in-game news |
| `sensor.helldivers2_store_rotation` | Store rotation expiration time |
| `sensor.helldivers2_top_player` | Current top player on the leaderboard |
| `sensor.helldivers2_top_clan` | Current top clan on the leaderboard |
| `sensor.helldivers2_election_status` | Current election status |
| `sensor.helldivers2_terminid_players` | Players fighting Terminids |
| `sensor.helldivers2_automaton_players` | Players fighting Automatons |
| `sensor.helldivers2_illuminate_players` | Players fighting Illuminate |
| `sensor.helldivers2_terminid_planets` | Active Terminid planets |
| `sensor.helldivers2_automaton_planets` | Active Automaton planets |
| `sensor.helldivers2_illuminate_planets` | Active Illuminate planets |

## Example Dashboard Card

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: "# Helldivers 2 Galactic War"

  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.helldivers2_total_players
        name: Total Players
        icon: mdi:account-group
      - type: entity
        entity: sensor.helldivers2_active_planets
        name: Active Planets
        icon: mdi:earth

  - type: entities
    title: Faction Status
    entities:
      - entity: sensor.helldivers2_terminid_players
        name: Terminid Front
        icon: mdi:bug
      - entity: sensor.helldivers2_automaton_players
        name: Automaton Front
        icon: mdi:robot
      - entity: sensor.helldivers2_illuminate_players
        name: Illuminate Front
        icon: mdi:alien

  - type: entity
    entity: sensor.helldivers2_major_order
    name: Major Order
    icon: mdi:clipboard-text

  - type: entity
    entity: sensor.helldivers2_latest_news
    name: Latest Dispatch
    icon: mdi:newspaper
```

## API Credits

This integration uses the [Diveharder API](https://api.diveharder.com), a comprehensive community-driven API for Helldivers 2 data.

## Disclaimer

This is a fan-made integration and is not affiliated with, endorsed by, or connected to Arrowhead Game Studios or Sony Interactive Entertainment.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**For Super Earth!** 🌍
