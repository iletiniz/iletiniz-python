"""Iletiniz API üst-düzey istemcisi."""

from __future__ import annotations

import os
import re
from typing import Optional

from iletiniz._http import HttpClient, Transport, UrllibTransport
from iletiniz.errors import IletinizError
from iletiniz.resources.health import HealthResource
from iletiniz.resources.messages import MessagesResource

_DEFAULT_BASE_URL = "https://api.iletiniz.com"
_DEFAULT_TIMEOUT_MS = 30_000
_DEFAULT_MAX_RETRIES = 2
_SDK_VERSION = "0.1.0"
_API_KEY_RE = re.compile(r"^iltz_(?:live|test)_[A-Za-z0-9_-]+$")


class IletinizClient:
    """Iletiniz API'sine erişim sağlayan ana istemci."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_ms: int = _DEFAULT_TIMEOUT_MS,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        default_headers: Optional[dict[str, str]] = None,
        transport: Optional[Transport] = None,
    ) -> None:
        resolved_key = api_key or os.environ.get("ILETINIZ_API_KEY")
        if not resolved_key:
            raise IletinizError(
                "API anahtarı gerekli. `IletinizClient(api_key=...)` "
                "veya ILETINIZ_API_KEY ortam değişkeni kullanın."
            )
        if not _API_KEY_RE.match(resolved_key):
            raise IletinizError(
                "Geçersiz API anahtar formatı. "
                "Beklenen: 'iltz_live_…' veya 'iltz_test_…'."
            )

        resolved_base_url = (
            base_url or os.environ.get("ILETINIZ_BASE_URL") or _DEFAULT_BASE_URL
        )

        merged_headers: dict[str, str] = {
            "User-Agent": f"iletiniz-python/{_SDK_VERSION}",
        }
        if default_headers:
            merged_headers.update(default_headers)

        http = HttpClient(
            base_url=resolved_base_url,
            api_key=resolved_key,
            timeout_ms=timeout_ms,
            max_retries=max_retries,
            default_headers=merged_headers,
            transport=transport or UrllibTransport(),
        )

        self.messages: MessagesResource = MessagesResource(http)
        self.health: HealthResource = HealthResource(http)
