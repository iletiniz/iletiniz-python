"""Tek mesaj gönderme örneği."""

import os

from iletiniz import IletinizClient


def main() -> None:
    client = IletinizClient(api_key=os.environ.get("ILETINIZ_API_KEY"))
    result = client.messages.send(
        {
            "to": "+905551234567",
            "body": "Merhaba! Bu Iletiniz SDK ile gönderilen test mesajıdır.",
        }
    )
    print(f"Job: {result.get('job_id')} Status: {result.get('status')}")


if __name__ == "__main__":
    main()
