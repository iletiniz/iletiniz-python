"""Mesaj gönderim ve sorgulama kaynağı."""

from __future__ import annotations

import urllib.parse
from typing import Any, Optional

from iletiniz._http import HttpClient
from iletiniz.errors import IletinizError
from iletiniz.types import (
    MessageStatusResponse,
    RequestOptions,
    SendBulkParams,
    SendBulkResponse,
    SendMessageParams,
    SendMessageResponse,
)

_MAX_BULK_ITEMS = 200


class MessagesResource:
    """`/v1/messages` endpoint ailesi."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def send(
        self,
        params: SendMessageParams,
        options: Optional[RequestOptions] = None,
    ) -> SendMessageResponse:
        """Tek bir SMS mesajı gönderir.

        `body` veya `template` alanlarından **tam olarak biri** verilmelidir.
        `variables` yalnızca `template` ile birlikte kullanılabilir.
        """
        _validate_send_params(params)
        return self._http.request(  # type: ignore[no-any-return]
            "POST",
            "/v1/messages",
            body=_strip_none(dict(params)),
            options=options,
        )

    def send_bulk(
        self,
        params: SendBulkParams,
        options: Optional[RequestOptions] = None,
    ) -> SendBulkResponse:
        """Tek istekte birden fazla mesaj gönderir (en fazla 200 öğe).

        - Üst seviye `template` verildiyse her item'da `body` olmamalı,
          yalnızca `variables` opsiyoneldir.
        - Üst seviye `template` yoksa her item'da `body` zorunludur,
          `variables` kullanılamaz.
        """
        _validate_bulk_params(params)
        cleaned = _strip_none(dict(params))
        items = cleaned.get("items")
        if isinstance(items, list):
            cleaned["items"] = [_strip_none(dict(it)) for it in items]
        return self._http.request(  # type: ignore[no-any-return]
            "POST",
            "/v1/messages/bulk",
            body=cleaned,
            options=options,
        )

    def retrieve(
        self,
        job_id: str,
        options: Optional[RequestOptions] = None,
    ) -> MessageStatusResponse:
        """Daha önce gönderilmiş bir mesajın güncel durumunu döner."""
        if not isinstance(job_id, str) or not job_id:
            raise IletinizError("job_id boş olamaz.")
        return self._http.request(  # type: ignore[no-any-return]
            "GET",
            f"/v1/messages/{urllib.parse.quote(job_id, safe='')}",
            options=options,
        )

    def status(
        self,
        job_id: str,
        options: Optional[RequestOptions] = None,
    ) -> MessageStatusResponse:
        """`retrieve` için alias."""
        return self.retrieve(job_id, options)


def _validate_send_params(params: SendMessageParams) -> None:
    if not isinstance(params, dict):
        raise IletinizError("send() bir dict / SendMessageParams gerektirir.")

    to = params.get("to")
    if not isinstance(to, str) or not (1 <= len(to) <= 64):
        raise IletinizError("'to' alanı 1-64 karakter arasında olmalıdır.")

    has_body = bool(params.get("body"))
    has_template = bool(params.get("template"))

    if has_body == has_template:
        raise IletinizError(
            "'body' veya 'template' alanlarından tam olarak biri zorunludur."
        )
    if "variables" in params and not has_template:
        raise IletinizError("'variables' yalnızca 'template' ile birlikte kullanılabilir.")
    if has_body:
        body = params["body"]
        if not isinstance(body, str) or not (1 <= len(body) <= 1600):
            raise IletinizError("'body' 1-1600 karakter arasında olmalıdır.")


def _validate_bulk_params(params: SendBulkParams) -> None:
    if not isinstance(params, dict):
        raise IletinizError("send_bulk() bir dict / SendBulkParams gerektirir.")

    items = params.get("items")
    if not isinstance(items, list) or not items:
        raise IletinizError("'items' en az bir öğe içermelidir.")
    if len(items) > _MAX_BULK_ITEMS:
        raise IletinizError(f"'items' en fazla {_MAX_BULK_ITEMS} öğe içerebilir.")

    using_template = bool(params.get("template"))

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise IletinizError(f"items[{i}] bir nesne olmalıdır.")
        to = item.get("to")
        if not isinstance(to, str) or not (1 <= len(to) <= 64):
            raise IletinizError(f"items[{i}].to 1-64 karakter arasında olmalıdır.")

        if using_template:
            if "body" in item:
                raise IletinizError(
                    f"Üst seviye 'template' verildi: items[{i}].body kullanılamaz."
                )
        else:
            body = item.get("body")
            if not isinstance(body, str) or len(body) < 1:
                raise IletinizError(f"'template' yok: items[{i}].body zorunludur.")
            if "variables" in item:
                raise IletinizError(
                    f"'template' yok: items[{i}].variables kullanılamaz."
                )


def _strip_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}
