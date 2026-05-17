"""HTTP transport ve retry/backoff yönetimi."""

from __future__ import annotations

import json
import random
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional, Protocol, Union

from iletiniz.errors import (
    IletinizConnectionError,
    IletinizTimeoutError,
    build_api_error,
)
from iletiniz.types import RequestOptions

_RETRYABLE_STATUSES: frozenset[int] = frozenset({408, 429})


@dataclass(frozen=True)
class HttpResponse:
    """Transport tarafından döndürülen ham HTTP yanıtı."""

    status: int
    body: bytes
    headers: dict[str, str]  # alt-case anahtarlar

    def get_header(self, name: str) -> Optional[str]:
        return self.headers.get(name.lower())


class Transport(Protocol):
    """Test ve özel HTTP istemcileri için injectable transport arayüzü."""

    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: Optional[bytes],
        timeout_ms: int,
    ) -> HttpResponse:
        """HTTP isteğini gönderir.

        - Timeout durumunda `IletinizTimeoutError` raise eder.
        - Diğer ağ hataları için `IletinizConnectionError` raise eder.
        """


class UrllibTransport:
    """Stdlib `urllib` üzerine kurulu varsayılan transport."""

    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: Optional[bytes],
        timeout_ms: int,
    ) -> HttpResponse:
        req = urllib.request.Request(url, data=body, method=method)
        for name, value in headers.items():
            req.add_header(name, value)
        timeout_s = timeout_ms / 1000.0
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
                raw = resp.read()
                response_headers = {k.lower(): v for k, v in resp.headers.items()}
                return HttpResponse(
                    status=resp.status,
                    body=raw,
                    headers=response_headers,
                )
        except urllib.error.HTTPError as e:
            raw = e.read() if hasattr(e, "read") else b""
            response_headers = {k.lower(): v for k, v in (e.headers or {}).items()}
            return HttpResponse(status=e.code, body=raw, headers=response_headers)
        except socket.timeout as e:
            raise IletinizTimeoutError(
                f"İstek {timeout_ms}ms içinde tamamlanamadı."
            ) from e
        except urllib.error.URLError as e:
            reason = e.reason
            if isinstance(reason, socket.timeout):
                raise IletinizTimeoutError(
                    f"İstek {timeout_ms}ms içinde tamamlanamadı."
                ) from e
            raise IletinizConnectionError(str(reason), cause=e) from e
        except OSError as e:  # genel ağ hatası
            raise IletinizConnectionError(str(e), cause=e) from e


class HttpClient:
    """Yüksek seviye HTTP istemcisi: retry, backoff, JSON encode/decode, hata haritalama."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_ms: int,
        max_retries: int,
        default_headers: dict[str, str],
        transport: Transport,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_ms = timeout_ms
        self._max_retries = max_retries
        self._default_headers = default_headers
        self._transport = transport

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[dict[str, Any]] = None,
        body: Any = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        url = self._build_url(path, query)

        headers: dict[str, str] = dict(self._default_headers)
        headers["Authorization"] = f"Bearer {self._api_key}"
        headers["Accept"] = "application/json"
        if options and options.headers:
            headers.update(options.headers)

        payload: Optional[bytes] = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            payload = json.dumps(body, ensure_ascii=False).encode("utf-8")

        timeout_ms = options.timeout_ms if options and options.timeout_ms else self._timeout_ms

        attempt = 0
        while True:
            try:
                response = self._transport.send(method, url, headers, payload, timeout_ms)
            except (IletinizTimeoutError, IletinizConnectionError):
                if self._should_retry(None, attempt):
                    attempt += 1
                    self._sleep(self._backoff_ms(attempt, None))
                    continue
                raise

            status = response.status
            if 200 <= status < 300:
                if status == 204 or not response.body:
                    return None
                try:
                    return json.loads(response.body)
                except json.JSONDecodeError as e:
                    raise IletinizConnectionError("Sunucudan geçersiz JSON döndü.") from e

            if self._should_retry(status, attempt):
                attempt += 1
                self._sleep(self._backoff_ms(attempt, response.get_header("retry-after")))
                continue

            request_id = response.get_header("x-request-id")
            error_body = self._parse_error_body(response.body)
            raise build_api_error(status, error_body, request_id)

    def _build_url(self, path: str, query: Optional[dict[str, Any]]) -> str:
        p = path if path.startswith("/") else "/" + path
        url = self._base_url + p
        if query:
            cleaned: dict[str, str] = {}
            for k, v in query.items():
                if v is None:
                    continue
                cleaned[k] = "true" if v is True else "false" if v is False else str(v)
            if cleaned:
                url = f"{url}?{urllib.parse.urlencode(cleaned)}"
        return url

    def _should_retry(self, status: Optional[int], attempt: int) -> bool:
        if attempt >= self._max_retries:
            return False
        if status is None:
            return True
        if status in _RETRYABLE_STATUSES:
            return True
        return 500 <= status <= 599

    def _backoff_ms(self, attempt: int, retry_after: Optional[str]) -> int:
        if retry_after:
            try:
                seconds = float(retry_after)
                if seconds > 0:
                    return int(min(seconds * 1000.0, 30_000.0))
            except ValueError:
                pass
        base = min((2 ** attempt) * 250, 4000)
        return int(base + random.randint(0, 100))  # noqa: S311

    @staticmethod
    def _sleep(ms: int) -> None:
        time.sleep(ms / 1000.0)

    @staticmethod
    def _parse_error_body(raw: bytes) -> Union[dict[str, Any], str, None]:
        if not raw:
            return None
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            try:
                return raw.decode("utf-8", errors="replace")
            except Exception:  # pragma: no cover
                return None
        if isinstance(decoded, dict):
            return decoded
        return None


__all__ = ["HttpClient", "HttpResponse", "Transport", "UrllibTransport"]
