"""Config flow for Helldivers 2 integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    API_WAR,
    API_HEADERS,
    CONF_UPDATE_INTERVAL,
    CONF_ERROR_REPORTING,
    CONF_GITHUB_TOKEN,
    CONF_DEBUG_LOGGING,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class Helldivers2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Helldivers 2."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        # Check if already configured
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            # Test API connection
            try:
                async with aiohttp.ClientSession(headers=API_HEADERS) as session:
                    async with session.get(API_WAR, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        response.raise_for_status()
                        await response.json()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                # Validate GitHub token if error reporting is enabled
                if user_input.get(CONF_ERROR_REPORTING) and user_input.get(CONF_GITHUB_TOKEN):
                    token_valid = await self._validate_github_token(user_input[CONF_GITHUB_TOKEN])
                    if not token_valid:
                        errors["base"] = "invalid_github_token"

                if not errors:
                    return self.async_create_entry(
                        title="Helldivers 2",
                        data={},
                        options={
                            CONF_UPDATE_INTERVAL: user_input.get(
                                CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                            CONF_ERROR_REPORTING: user_input.get(CONF_ERROR_REPORTING, False),
                            CONF_GITHUB_TOKEN: user_input.get(CONF_GITHUB_TOKEN, ""),
                            CONF_DEBUG_LOGGING: user_input.get(CONF_DEBUG_LOGGING, False),
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=30,
                            max=600,
                            step=10,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_ERROR_REPORTING,
                        default=False,
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_GITHUB_TOKEN,
                        default="",
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        )
                    ),
                    vol.Optional(
                        CONF_DEBUG_LOGGING,
                        default=False,
                    ): selector.BooleanSelector(),
                }
            ),
            errors=errors,
            description_placeholders={
                "github_token_url": "https://github.com/settings/tokens/new?scopes=public_repo",
            },
        )

    async def _validate_github_token(self, token: str) -> bool:
        """Validate the GitHub token."""
        if not token:
            return False

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get("https://api.github.com/user", timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception:
            return False

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> Helldivers2OptionsFlow:
        """Get the options flow for this handler."""
        return Helldivers2OptionsFlow(config_entry)


class Helldivers2OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Helldivers 2."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate GitHub token if error reporting is enabled
            if user_input.get(CONF_ERROR_REPORTING) and user_input.get(CONF_GITHUB_TOKEN):
                token_valid = await self._validate_github_token(user_input[CONF_GITHUB_TOKEN])
                if not token_valid:
                    errors["base"] = "invalid_github_token"

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=30,
                            max=600,
                            step=10,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_ERROR_REPORTING,
                        default=self.config_entry.options.get(CONF_ERROR_REPORTING, False),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_GITHUB_TOKEN,
                        default=self.config_entry.options.get(CONF_GITHUB_TOKEN, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        )
                    ),
                    vol.Optional(
                        CONF_DEBUG_LOGGING,
                        default=self.config_entry.options.get(CONF_DEBUG_LOGGING, False),
                    ): selector.BooleanSelector(),
                }
            ),
            errors=errors,
            description_placeholders={
                "github_token_url": "https://github.com/settings/tokens/new?scopes=public_repo",
            },
        )

    async def _validate_github_token(self, token: str) -> bool:
        """Validate the GitHub token."""
        if not token:
            return False

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get("https://api.github.com/user", timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception:
            return False
