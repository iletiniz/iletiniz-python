"""Toplu mesaj gönderme örneği."""

import os

from iletiniz import IletinizClient


def main() -> None:
    client = IletinizClient(api_key=os.environ.get("ILETINIZ_API_KEY"))
    result = client.messages.send_bulk(
        {
            "template": "low_stock_alert",
            "items": [
                {"to": "+905551111111", "variables": {"product": "Ürün A", "stock": 3}},
                {"to": "+905552222222", "variables": {"product": "Ürün B", "stock": 1}},
            ],
        }
    )
    print(
        f"Toplam: {result.get('total')}, "
        f"Gönderilen: {result.get('sent')}, "
        f"Başarısız: {result.get('failed')}"
    )


if __name__ == "__main__":
    main()
