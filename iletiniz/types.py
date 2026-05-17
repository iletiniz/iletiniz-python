"""SDK için tip tanımları."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

try:
    from typing import Literal, TypedDict
except ImportError:  # pragma: no cover
    from typing_extensions import Literal, TypedDict  # type: ignore[assignment]


MessageStatus = Literal[
    "sent", "queued", "failed", "delivered", "expired", "rejected", "unknown"
]
SendMessageStatus = Literal["sent", "queued", "failed"]


class ApiError(TypedDict):
    code: str
    message: str


TemplateVariables = dict[str, Union[str, int, float]]


class SendMessageParams(TypedDict, total=False):
    """Tek mesaj gönderim parametreleri.

    `to` zorunlu; `body` veya `template` alanlarından tam olarak biri verilmeli.
    """

    to: str
    body: str
    template: str
    variables: TemplateVariables
    sender: str
    provider: str
    # İYS izni. True → ticari (sağlayıcının İYS filtresi devreye girer).
    # False/yok → bilgilendirme. Sadece SMS sağlayıcılarında işlenir;
    # WhatsApp/Telegram için yok sayılır.
    iys: bool


class SendMessageResponse(TypedDict, total=False):
    job_id: str
    status: SendMessageStatus
    to: str
    provider: str
    template: str
    template_key: str
    error: ApiError
    created_at: str


class MessageStatusResponse(TypedDict, total=False):
    job_id: str
    status: MessageStatus
    to: str
    provider: str
    error: ApiError
    created_at: str
    sent_at: Optional[str]
    delivered_at: Optional[str]


class BulkItemInput(TypedDict, total=False):
    to: str
    body: str
    variables: TemplateVariables


class SendBulkParams(TypedDict, total=False):
    provider: str
    sender: str
    template: str
    # Bkz. SendMessageParams.iys. Tüm batch için tek değer.
    iys: bool
    items: list[BulkItemInput]


class SendBulkItemResult(TypedDict, total=False):
    to: str
    status: Literal["sent", "failed"]
    job_id: str
    error: ApiError


class SendBulkResponse(TypedDict, total=False):
    total: int
    sent: int
    failed: int
    provider: str
    template: str
    template_key: str
    created_at: str
    results: list[SendBulkItemResult]


class HealthResponse(TypedDict):
    ok: bool
    db: Literal["up", "down"]


@dataclass(frozen=True)
class RequestOptions:
    """İstek bazlı opsiyonlar."""

    timeout_ms: Optional[int] = None
    headers: Optional[dict[str, str]] = None


__all__ = [
    "ApiError",
    "BulkItemInput",
    "HealthResponse",
    "MessageStatus",
    "MessageStatusResponse",
    "RequestOptions",
    "SendBulkItemResult",
    "SendBulkParams",
    "SendBulkResponse",
    "SendMessageParams",
    "SendMessageResponse",
    "SendMessageStatus",
    "TemplateVariables",
]


# Re-export for runtime introspection (e.g. error_body type hints)
_Any = Any
