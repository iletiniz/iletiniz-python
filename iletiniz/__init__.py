"""Iletiniz API resmi Python SDK'si."""

from iletiniz._http import HttpResponse, Transport
from iletiniz.client import IletinizClient
from iletiniz.errors import (
    IletinizAPIError,
    IletinizAuthenticationError,
    IletinizConnectionError,
    IletinizError,
    IletinizNotFoundError,
    IletinizPermissionError,
    IletinizRateLimitError,
    IletinizServerError,
    IletinizTimeoutError,
    IletinizValidationError,
)
from iletiniz.resources.health import HealthResource
from iletiniz.resources.messages import MessagesResource
from iletiniz.types import (
    BulkItemInput,
    HealthResponse,
    MessageStatus,
    MessageStatusResponse,
    RequestOptions,
    SendBulkItemResult,
    SendBulkParams,
    SendBulkResponse,
    SendMessageParams,
    SendMessageResponse,
    SendMessageStatus,
)

__version__ = "0.1.0"

__all__ = [
    "BulkItemInput",
    "HealthResource",
    "HealthResponse",
    "HttpResponse",
    "IletinizAPIError",
    "IletinizAuthenticationError",
    "IletinizClient",
    "IletinizConnectionError",
    "IletinizError",
    "IletinizNotFoundError",
    "IletinizPermissionError",
    "IletinizRateLimitError",
    "IletinizServerError",
    "IletinizTimeoutError",
    "IletinizValidationError",
    "MessageStatus",
    "MessageStatusResponse",
    "MessagesResource",
    "RequestOptions",
    "SendBulkItemResult",
    "SendBulkParams",
    "SendBulkResponse",
    "SendMessageParams",
    "SendMessageResponse",
    "SendMessageStatus",
    "Transport",
    "__version__",
]
