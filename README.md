# İletiniz Python SDK

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Iletiniz API için resmi Python SDK'si. Python 3.9+ üzerinde çalışır, hiçbir runtime bağımlılığı yoktur (yalnızca standart kütüphane).

## Kurulum

```bash
pip install iletiniz
```

Gereksinimler:

- Python `>= 3.9`

## Hızlı başlangıç

```python
import os
from iletiniz import IletinizClient

client = IletinizClient(api_key=os.environ["ILETINIZ_API_KEY"])  # 'iltz_live_…' veya 'iltz_test_…'

result = client.messages.send({
    "to": "+905551234567",
    "body": "Merhaba!",
})

print(result["job_id"], result["status"])
```

`api_key` verilmediğinde SDK `ILETINIZ_API_KEY` ortam değişkenini okur.

## Yapılandırma

```python
IletinizClient(
    api_key="iltz_live_…",
    base_url="https://api.iletiniz.com",  # varsayılan
    timeout_ms=30_000,                     # varsayılan
    max_retries=2,                         # 408/429/5xx ve ağ hatalarında
    default_headers={"X-Source": "crm"},
    transport=None,                        # özel Transport implementasyonu
)
```

## Endpoint'ler

SDK, public API yüzeyini kapsar:

| Metot                                     | HTTP                              |
| ----------------------------------------- | --------------------------------- |
| `client.health.check()`                   | `GET /v1/health`                  |
| `client.messages.send(params)`            | `POST /v1/messages`               |
| `client.messages.send_bulk(params)`       | `POST /v1/messages/bulk`          |
| `client.messages.retrieve(job_id)`        | `GET /v1/messages/{job_id}`       |
| `client.messages.status(job_id)` (alias)  | `GET /v1/messages/{job_id}`       |

### Tek mesaj göndermek

```python
client.messages.send({
    "to": "+905551234567",
    "body": "Sipariş kodunuz: 4821",
    "sender": "MAGAZA",     # opsiyonel
    "provider": "netgsm",   # opsiyonel
})
```

### Telegram üzerinden göndermek

`"provider": "telegram"` seçildiğinde `to` alanı SMS yerine Telegram alıcı tanımlayıcısı bekler:
numerik `chat_id` (örn `8409353994`, gruplar için `-1001234567890`) veya `@kullaniciadi`. `sender` Telegram için kullanılmaz — bot kimliği bağlantıdaki token'a gömülüdür.

```python
client.messages.send({
    "to": "8409353994",
    "body": "Merhaba!",
    "provider": "telegram",
})
```

### Template ile göndermek

```python
client.messages.send({
    "to": "+905551234567",
    "template": "order_shipped",
    "variables": {"name": "Ayşe", "tracking_no": "TR123"},
})
```

`body` ve `template` aynı anda kullanılamaz; tam olarak biri zorunludur. `variables` yalnızca `template` ile birlikte verilebilir.

### Toplu gönderim

Tek istekte en fazla 200 öğe gönderebilirsiniz.

```python
# Düz metin modu — her item'da body zorunlu, variables yok
client.messages.send_bulk({
    "items": [
        {"to": "+905551111111", "body": "Mesaj 1"},
        {"to": "+905552222222", "body": "Mesaj 2"},
    ],
})

# Template modu — items'ta body olmamalı
client.messages.send_bulk({
    "template": "low_stock_alert",
    "items": [
        {"to": "+905551111111", "variables": {"product": "Ürün A", "stock": 3}},
        {"to": "+905552222222", "variables": {"product": "Ürün B", "stock": 1}},
    ],
})
```

### Mesaj durumunu sorgulamak

```python
info = client.messages.retrieve(job_id)
# info["status"]: 'sent' | 'queued' | 'failed' | 'delivered' | 'expired' | 'rejected' | 'unknown'
```

### Sağlık kontrolü

```python
health = client.health.check()
# {"ok": True, "db": "up"}
```

## Hata yönetimi

Tüm hatalar `IletinizError` sınıfından türetilir. HTTP status'a göre uygun alt sınıf raise edilir:

```python
from iletiniz import (
    IletinizAPIError,
    IletinizAuthenticationError,
    IletinizConnectionError,
    IletinizNotFoundError,
    IletinizRateLimitError,
    IletinizServerError,
    IletinizTimeoutError,
    IletinizValidationError,
)

try:
    client.messages.send({"to": "+905551234567", "body": "test"})
except IletinizAuthenticationError:
    # 401 — geçersiz veya iptal edilmiş anahtar
    ...
except IletinizValidationError as e:
    # 400 / 422 — istek doğrulanamadı
    print(e.body)
except IletinizRateLimitError:
    # 429 — yeniden denemeden önce backoff
    ...
except IletinizNotFoundError:
    # 404
    ...
except IletinizServerError:
    # 5xx
    ...
except IletinizAPIError as e:
    print(e.status, e.code, str(e), e.request_id)
except IletinizTimeoutError:
    # istek timeout'a takıldı
    ...
except IletinizConnectionError:
    # ağ hatası
    ...
```

## Yeniden deneme stratejisi

SDK, aşağıdaki durumlarda otomatik olarak `max_retries` defa yeniden dener (varsayılan: 2):

- Ağ kaynaklı bağlantı hataları
- HTTP 408, 429, 500–599

`Retry-After` başlığı varsa beklenir; aksi halde exponential backoff (jitter ile) uygulanır. Yeniden denemeyi kapatmak için `max_retries=0` verin.

## Timeout

Her istek için ayrıca timeout verebilirsiniz:

```python
from iletiniz import RequestOptions

client.messages.send(
    {"to": "+905551234567", "body": "merhaba"},
    RequestOptions(timeout_ms=10_000),
)
```

## Tip desteği

SDK tamamen tip ipuçlarıyla yazıldı (PEP 561 — `py.typed`). Tüm parametre ve yanıt tipleri export edilir:

```python
from iletiniz import (
    HealthResponse,
    MessageStatusResponse,
    SendBulkParams,
    SendBulkResponse,
    SendMessageParams,
    SendMessageResponse,
)
```

## Test

SDK, `iletiniz.Transport` protokolü üzerinden HTTP katmanını dışarı açar. Testlerinizde gerçek ağ trafiği oluşturmadan SDK'yı kullanabilirsiniz:

```python
from iletiniz import HttpResponse, IletinizClient, Transport


class FakeTransport(Transport):
    def send(self, method, url, headers, body, timeout_ms):
        return HttpResponse(status=200, body=b'{"ok":true,"db":"up"}', headers={})


client = IletinizClient(api_key="iltz_test_xxx", transport=FakeTransport())
```

## Katkıda Bulunma / Contributing

Katkı sağlamak ister misiniz? Lütfen [CONTRIBUTING.md](./CONTRIBUTING.md) dosyasını inceleyin. English: [CONTRIBUTING.en.md](./CONTRIBUTING.en.md).

## Davranış Kuralları / Code of Conduct

Bu proje [Contributor Covenant](./CODE_OF_CONDUCT.md) davranış kurallarına bağlıdır. English: [CODE_OF_CONDUCT.en.md](./CODE_OF_CONDUCT.en.md).

## Güvenlik / Security

Güvenlik açığı bildirmek için lütfen [SECURITY.md](./SECURITY.md) dosyasındaki adımları izleyin — **public issue açmayın**. English: [SECURITY.en.md](./SECURITY.en.md).

## Lisans / License

MIT — bkz. / see [LICENSE](./LICENSE).
