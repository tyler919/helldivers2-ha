/**
 * Helldivers 2 Galactic War Panel
 * Custom sidebar panel for Home Assistant
 */

class Helldivers2Panel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = {};
    this._data = {};
  }

  set hass(hass) {
    this._hass = hass;
    this._updateData();
    this._render();
  }

  set panel(panel) {
    this._config = panel.config || {};
  }

  _updateData() {
    if (!this._hass) return;

    // Get data from sensors (entity IDs use "helldivers_2" due to has_entity_name)
    const sensors = {
      totalPlayers: this._hass.states["sensor.helldivers_2_total_players"],
      activePlanets: this._hass.states["sensor.helldivers_2_active_planets"],
      avgLiberation: this._hass.states["sensor.helldivers_2_average_liberation"],
      hottestPlanet: this._hass.states["sensor.helldivers_2_hottest_planet"],
      majorOrder: this._hass.states["sensor.helldivers_2_major_order"],
      majorOrderProgress: this._hass.states["sensor.helldivers_2_major_order_progress"],
      majorOrderTimeLeft: this._hass.states["sensor.helldivers_2_major_order_expiration"],
      majorOrderReward: this._hass.states["sensor.helldivers_2_major_order_reward"],
      missionsWon: this._hass.states["sensor.helldivers_2_missions_won"],
      missionsLost: this._hass.states["sensor.helldivers_2_missions_lost"],
      successRate: this._hass.states["sensor.helldivers_2_mission_success_rate"],
      terminidKills: this._hass.states["sensor.helldivers_2_terminid_kills"],
      automatonKills: this._hass.states["sensor.helldivers_2_automaton_kills"],
      illuminateKills: this._hass.states["sensor.helldivers_2_illuminate_kills"],
      totalDeaths: this._hass.states["sensor.helldivers_2_total_deaths"],
      friendlyFire: this._hass.states["sensor.helldivers_2_friendly_kills"],
      terminidPlayers: this._hass.states["sensor.helldivers_2_terminid_players"],
      automatonPlayers: this._hass.states["sensor.helldivers_2_automaton_players"],
      illuminatePlayers: this._hass.states["sensor.helldivers_2_illuminate_players"],
      latestNews: this._hass.states["sensor.helldivers_2_latest_news"],
      latestPatch: this._hass.states["sensor.helldivers_2_latest_patch"],
      gameVersion: this._hass.states["sensor.helldivers_2_game_version"],
    };

    this._data = {};
    for (const [key, sensor] of Object.entries(sensors)) {
      if (sensor) {
        this._data[key] = {
          state: sensor.state,
          attributes: sensor.attributes || {},
        };
      }
    }
  }

  _formatNumber(num) {
    if (num === undefined || num === null || num === "unavailable" || num === "unknown") {
      return "---";
    }
    const n = parseInt(num);
    if (isNaN(n)) return num;
    return n.toLocaleString();
  }

  _render() {
    const d = this._data;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          padding: 16px;
          background: var(--primary-background-color, #111);
          color: var(--primary-text-color, #fff);
          min-height: 100vh;
          box-sizing: border-box;
          font-family: var(--paper-font-body1_-_font-family, 'Roboto', sans-serif);
        }

        .header {
          text-align: center;
          margin-bottom: 24px;
          padding: 16px;
          background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
          border-radius: 12px;
          border: 1px solid #ffd700;
        }

        .header h1 {
          margin: 0;
          font-size: 28px;
          color: #ffd700;
          text-transform: uppercase;
          letter-spacing: 2px;
        }

        .header .subtitle {
          color: #888;
          font-size: 14px;
          margin-top: 8px;
        }

        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 16px;
        }

        .card {
          background: var(--card-background-color, #1e1e1e);
          border-radius: 12px;
          padding: 16px;
          border: 1px solid var(--divider-color, #333);
        }

        .card-title {
          font-size: 14px;
          font-weight: 500;
          color: #888;
          text-transform: uppercase;
          letter-spacing: 1px;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .card-title ha-icon {
          --mdc-icon-size: 20px;
          color: #ffd700;
        }

        .big-stat {
          font-size: 48px;
          font-weight: bold;
          color: #ffd700;
          line-height: 1;
        }

        .stat-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid var(--divider-color, #333);
        }

        .stat-row:last-child {
          border-bottom: none;
        }

        .stat-label {
          color: #888;
          font-size: 14px;
        }

        .stat-value {
          font-weight: 500;
          font-size: 16px;
        }

        .faction-terminid { color: #ff9800; }
        .faction-automaton { color: #f44336; }
        .faction-illuminate { color: #9c27b0; }

        .major-order {
          background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
          border: 1px solid #ffd700;
        }

        .major-order-text {
          font-size: 14px;
          line-height: 1.5;
          margin-bottom: 16px;
          max-height: 80px;
          overflow: hidden;
        }

        .progress-bar {
          background: #333;
          border-radius: 8px;
          height: 24px;
          overflow: hidden;
          position: relative;
        }

        .progress-fill {
          background: linear-gradient(90deg, #ffd700, #ffaa00);
          height: 100%;
          transition: width 0.5s ease;
        }

        .progress-text {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 12px;
          font-weight: bold;
          color: #000;
          text-shadow: 0 0 4px #fff;
        }

        .news-item {
          padding: 12px;
          background: rgba(255,255,255,0.05);
          border-radius: 8px;
          margin-bottom: 8px;
          font-size: 13px;
          line-height: 1.4;
        }

        .planet-list {
          max-height: 300px;
          overflow-y: auto;
        }

        .planet-item {
          display: grid;
          grid-template-columns: 1fr auto auto;
          gap: 8px;
          padding: 8px 0;
          border-bottom: 1px solid var(--divider-color, #333);
          align-items: center;
        }

        .planet-name {
          font-weight: 500;
        }

        .planet-players {
          color: #ffd700;
          font-size: 14px;
        }

        .planet-liberation {
          font-size: 12px;
          color: #4caf50;
        }

        .version-info {
          text-align: center;
          margin-top: 24px;
          padding: 12px;
          background: rgba(255,255,255,0.05);
          border-radius: 8px;
          font-size: 12px;
          color: #666;
        }

        @media (max-width: 600px) {
          .grid {
            grid-template-columns: 1fr;
          }
          .big-stat {
            font-size: 36px;
          }
        }
      </style>

      <div class="header">
        <h1>Helldivers 2</h1>
        <div class="subtitle">Galactic War Status</div>
      </div>

      <div class="grid">
        <!-- Total Players -->
        <div class="card">
          <div class="card-title">
            <ha-icon icon="mdi:account-group"></ha-icon>
            Active Helldivers
          </div>
          <div class="big-stat">${this._formatNumber(d.totalPlayers?.state)}</div>
          <div style="margin-top: 16px;">
            <div class="stat-row">
              <span class="stat-label">Terminid Front</span>
              <span class="stat-value faction-terminid">${this._formatNumber(d.terminidPlayers?.state)}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Automaton Front</span>
              <span class="stat-value faction-automaton">${this._formatNumber(d.automatonPlayers?.state)}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Illuminate Front</span>
              <span class="stat-value faction-illuminate">${this._formatNumber(d.illuminatePlayers?.state)}</span>
            </div>
          </div>
        </div>

        <!-- Major Order -->
        <div class="card major-order">
          <div class="card-title">
            <ha-icon icon="mdi:clipboard-text"></ha-icon>
            Major Order
          </div>
          <div class="major-order-text">${d.majorOrder?.state || "No Active Order"}</div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${this._getProgressPercent()}%"></div>
            <div class="progress-text">${d.majorOrderProgress?.state || "---"}</div>
          </div>
          <div style="margin-top: 12px;">
            <div class="stat-row">
              <span class="stat-label">Time Remaining</span>
              <span class="stat-value">${d.majorOrderTimeLeft?.state || "---"}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Reward</span>
              <span class="stat-value" style="color: #ffd700;">${d.majorOrderReward?.state || "---"}</span>
            </div>
          </div>
        </div>

        <!-- War Statistics -->
        <div class="card">
          <div class="card-title">
            <ha-icon icon="mdi:chart-bar"></ha-icon>
            War Statistics
          </div>
          <div class="stat-row">
            <span class="stat-label">Missions Won</span>
            <span class="stat-value" style="color: #4caf50;">${this._formatNumber(d.missionsWon?.state)}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Missions Lost</span>
            <span class="stat-value" style="color: #f44336;">${this._formatNumber(d.missionsLost?.state)}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Success Rate</span>
            <span class="stat-value">${d.successRate?.state || "---"}%</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Helldiver Deaths</span>
            <span class="stat-value">${this._formatNumber(d.totalDeaths?.state)}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Friendly Fire</span>
            <span class="stat-value" style="color: #ff9800;">${this._formatNumber(d.friendlyFire?.state)}</span>
          </div>
        </div>

        <!-- Kill Counts -->
        <div class="card">
          <div class="card-title">
            <ha-icon icon="mdi:skull"></ha-icon>
            Enemy Kills
          </div>
          <div class="stat-row">
            <span class="stat-label">Terminid Kills</span>
            <span class="stat-value faction-terminid">${this._formatNumber(d.terminidKills?.state)}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Automaton Kills</span>
            <span class="stat-value faction-automaton">${this._formatNumber(d.automatonKills?.state)}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Illuminate Kills</span>
            <span class="stat-value faction-illuminate">${this._formatNumber(d.illuminateKills?.state)}</span>
          </div>
        </div>

        <!-- Hottest Planet -->
        <div class="card">
          <div class="card-title">
            <ha-icon icon="mdi:fire"></ha-icon>
            Hottest Planet
          </div>
          <div class="big-stat" style="font-size: 24px;">${d.hottestPlanet?.state || "Unknown"}</div>
          ${this._renderHottestPlanetInfo()}
        </div>

        <!-- Active Campaigns -->
        <div class="card">
          <div class="card-title">
            <ha-icon icon="mdi:earth"></ha-icon>
            Active Campaigns (${d.activePlanets?.state || 0})
          </div>
          <div class="planet-list">
            ${this._renderPlanetList()}
          </div>
        </div>

        <!-- Latest News -->
        <div class="card" style="grid-column: span 2;">
          <div class="card-title">
            <ha-icon icon="mdi:newspaper"></ha-icon>
            Super Earth Dispatches
          </div>
          ${this._renderNews()}
        </div>
      </div>

      <div class="version-info">
        Game Version: ${d.gameVersion?.state || "Unknown"} |
        Latest Patch: ${d.latestPatch?.state || "Unknown"} |
        Avg Liberation: ${d.avgLiberation?.state || "0"}%
      </div>
    `;
  }

  _getProgressPercent() {
    const progress = this._data.majorOrderProgress?.state || "";
    if (!progress || progress === "No Progress") return 0;

    const match = progress.match(/([\d,]+)\s*\/\s*([\d,]+)/);
    if (match) {
      const current = parseInt(match[1].replace(/,/g, ""));
      const total = parseInt(match[2].replace(/,/g, ""));
      if (total > 0) {
        return Math.min(100, Math.round((current / total) * 100));
      }
    }
    return 0;
  }

  _renderHottestPlanetInfo() {
    const attrs = this._data.hottestPlanet?.attributes || {};
    if (!attrs.players) return "";

    return `
      <div style="margin-top: 16px;">
        <div class="stat-row">
          <span class="stat-label">Players</span>
          <span class="stat-value">${this._formatNumber(attrs.players)}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Liberation</span>
          <span class="stat-value">${attrs.liberation?.toFixed(1) || 0}%</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Sector</span>
          <span class="stat-value">${attrs.sector || "Unknown"}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Biome</span>
          <span class="stat-value">${attrs.biome || "Unknown"}</span>
        </div>
        ${attrs.hazards ? `
        <div class="stat-row">
          <span class="stat-label">Hazards</span>
          <span class="stat-value" style="color: #f44336;">${attrs.hazards}</span>
        </div>
        ` : ""}
      </div>
    `;
  }

  _renderPlanetList() {
    const campaigns = this._data.activePlanets?.attributes?.active_campaigns || [];
    if (!campaigns.length) {
      return '<div style="color: #666;">No active campaigns</div>';
    }

    return campaigns.slice(0, 10).map(planet => `
      <div class="planet-item">
        <div class="planet-name">${planet.name}</div>
        <div class="planet-players">${this._formatNumber(planet.players)} players</div>
        <div class="planet-liberation">${planet.liberation?.toFixed(1) || 0}%</div>
      </div>
    `).join("");
  }

  _renderNews() {
    const news = this._data.latestNews?.attributes?.recent_news || [];
    if (!news.length) {
      return '<div class="news-item">No dispatches available</div>';
    }

    return news.slice(0, 3).map(item => `
      <div class="news-item">${item.message || "No content"}</div>
    `).join("");
  }
}

customElements.define("helldivers2-panel", Helldivers2Panel);
