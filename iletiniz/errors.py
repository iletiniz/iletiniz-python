"""Iletiniz SDK hata sınıfları."""

from __future__ import annotations

from typing import Any, Optional, Union


class IletinizError(Exception):
    """Tüm SDK hatalarının taban sınıfı."""


class IletinizAPIError(IletinizError):
    """API tarafından dönen HTTP hatası."""

    def __init__(
        self,
        message: str,
        *,
        status: int,
        code: Optional[str] = None,
        body: Union[dict[str, Any], str, None] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status: int = status
        self.code: Optional[str] = code
        self.body: Union[dict[str, Any], str, None] = body
        self.request_id: Optional[str] = request_id


class IletinizAuthenticationError(IletinizAPIError):
    """401."""


class IletinizPermissionError(IletinizAPIError):
    """403."""


class IletinizValidationError(IletinizAPIError):
    """400 / 422."""


class IletinizRateLimitError(IletinizAPIError):
    """429."""


class IletinizNotFoundError(IletinizAPIError):
    """404."""


class IletinizServerError(IletinizAPIError):
    """5xx."""


class IletinizConnectionError(IletinizError):
    """Ağ bağlantı hatası."""

    def __init__(self, message: str, cause: Optional[BaseException] = None) -> None:
        super().__init__(message)
        self.cause: Optional[BaseException] = cause


class IletinizTimeoutError(IletinizError):
    """İstek timeout süresinde tamamlanamadı."""


def build_api_error(
    status: int,
    body: Union[dict[str, Any], str, None],
    request_id: Optional[str],
) -> IletinizAPIError:
    """HTTP status'a göre uygun `IletinizAPIError` alt sınıfını üretir."""
    code: Optional[str] = None
    message: Optional[str] = None

    if isinstance(body, dict):
        if isinstance(body.get("error"), str):
            code = body["error"]
        if isinstance(body.get("message"), str):
            message = body["message"]
    elif isinstance(body, str) and body:
        message = body

    if not message:
        message = f"HTTP {status}"

    params: dict[str, Any] = {
        "status": status,
        "code": code,
        "body": body,
        "request_id": request_id,
    }

    if status == 401:
        return IletinizAuthenticationError(message, **params)
    if status == 403:
        return IletinizPermissionError(message, **params)
    if status == 404:
        return IletinizNotFoundError(message, **params)
    if status in (400, 422):
        return IletinizValidationError(message, **params)
    if status == 429:
        return IletinizRateLimitError(message, **params)
    if status >= 500:
        return IletinizServerError(message, **params)
    return IletinizAPIError(message, **params)
