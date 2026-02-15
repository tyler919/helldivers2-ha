"""GitHub issue reporter for automatic error reporting."""
from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from .const import GITHUB_REPO_OWNER, GITHUB_REPO_NAME

_LOGGER = logging.getLogger(__name__)

# Rate limiting: max 1 issue per error type per hour
RATE_LIMIT_SECONDS = 3600
# Cache of recently reported issues to avoid duplicates
_reported_issues: dict[str, datetime] = {}


class GitHubIssueReporter:
    """Report errors to GitHub issues."""

    def __init__(self, github_token: str) -> None:
        """Initialize the reporter."""
        self._token = github_token
        self._session: aiohttp.ClientSession | None = None
        self._headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Helldivers2-HA-Integration",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self._session

    def _generate_issue_hash(self, error_type: str, error_message: str) -> str:
        """Generate a hash for deduplication."""
        # Use first line of error and type for hash
        first_line = error_message.split("\n")[0][:100]
        content = f"{error_type}:{first_line}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _is_rate_limited(self, issue_hash: str) -> bool:
        """Check if this error was recently reported."""
        if issue_hash in _reported_issues:
            last_reported = _reported_issues[issue_hash]
            if datetime.now() - last_reported < timedelta(seconds=RATE_LIMIT_SECONDS):
                return True
        return False

    async def _check_existing_issue(self, issue_hash: str) -> bool:
        """Check if an issue with this hash already exists."""
        session = await self._get_session()
        url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/issues"
        params = {
            "state": "open",
            "labels": "auto-reported",
            "per_page": 100,
        }

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    issues = await response.json()
                    for issue in issues:
                        if f"[{issue_hash}]" in issue.get("title", ""):
                            return True
        except Exception as e:
            _LOGGER.debug("Error checking existing issues: %s", e)

        return False

    async def report_error(
        self,
        error_type: str,
        error_message: str,
        traceback: str | None = None,
        additional_info: dict[str, Any] | None = None,
    ) -> bool:
        """Report an error to GitHub issues.

        Returns True if issue was created, False otherwise.
        """
        if not self._token:
            _LOGGER.debug("No GitHub token configured, skipping error report")
            return False

        # Generate hash for deduplication
        issue_hash = self._generate_issue_hash(error_type, error_message)

        # Check rate limiting
        if self._is_rate_limited(issue_hash):
            _LOGGER.debug("Error recently reported, skipping (rate limited)")
            return False

        # Check if issue already exists
        if await self._check_existing_issue(issue_hash):
            _LOGGER.debug("Issue already exists on GitHub, skipping")
            return False

        # Build issue body
        body = self._build_issue_body(
            error_type, error_message, traceback, additional_info, issue_hash
        )

        # Create the issue
        title = f"[Auto] [{issue_hash}] {error_type}: {error_message[:80]}"

        success = await self._create_issue(title, body)

        if success:
            _reported_issues[issue_hash] = datetime.now()
            _LOGGER.info("Error reported to GitHub: %s", title[:80])

        return success

    def _build_issue_body(
        self,
        error_type: str,
        error_message: str,
        traceback: str | None,
        additional_info: dict[str, Any] | None,
        issue_hash: str,
    ) -> str:
        """Build the issue body."""
        body = f"""## Auto-Reported Error

**Error Type:** `{error_type}`
**Issue Hash:** `{issue_hash}`
**Reported At:** {datetime.now().isoformat()}

### Error Message
```
{error_message}
```
"""

        if traceback:
            body += f"""
### Traceback
```python
{traceback}
```
"""

        if additional_info:
            body += "\n### Additional Information\n"
            for key, value in additional_info.items():
                body += f"- **{key}:** {value}\n"

        body += """
---
*This issue was automatically created by the Helldivers 2 Home Assistant integration.*
*If this is a duplicate or not a bug, please close this issue.*
"""

        return body

    async def _create_issue(self, title: str, body: str) -> bool:
        """Create a GitHub issue."""
        session = await self._get_session()
        url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/issues"

        data = {
            "title": title,
            "body": body,
            "labels": ["auto-reported", "bug"],
        }

        try:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    _LOGGER.debug("Created issue #%s", result.get("number"))
                    return True
                else:
                    error_text = await response.text()
                    _LOGGER.warning(
                        "Failed to create issue: %s - %s", response.status, error_text
                    )
                    return False
        except Exception as e:
            _LOGGER.warning("Error creating GitHub issue: %s", e)
            return False

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
