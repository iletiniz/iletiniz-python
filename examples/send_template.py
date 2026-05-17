"""Template ile mesaj gönderme örneği."""

import os

from iletiniz import IletinizClient


def main() -> None:
    client = IletinizClient(api_key=os.environ.get("ILETINIZ_API_KEY"))
    result = client.messages.send(
        {
            "to": "+905551234567",
            "template": "order_shipped",
            "variables": {"name": "Ayşe", "tracking_no": "TR123456789"},
        }
    )
    print(f"Sent via template: {result.get('template_key', '-')} -> {result.get('status')}")


if __name__ == "__main__":
    main()
