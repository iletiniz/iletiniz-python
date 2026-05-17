"""Sağlık kontrolü kaynağı."""

from __future__ import annotations

from typing import Optional

from iletiniz._http import HttpClient
from iletiniz.types import HealthResponse, RequestOptions


class HealthResource:
    """`/v1/health` endpoint'i."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def check(self, options: Optional[RequestOptions] = None) -> HealthResponse:
        """API ve veritabanının erişilebilirliğini kontrol eder."""
        return self._http.request("GET", "/v1/health", options=options)  # type: ignore[no-any-return]
