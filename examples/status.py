"""Mesaj durumu sorgulama örneği."""

import os
import sys

from iletiniz import IletinizClient, IletinizNotFoundError


def main() -> None:
    if len(sys.argv) < 2:
        print("Kullanım: python status.py <job_id>", file=sys.stderr)
        sys.exit(2)

    client = IletinizClient(api_key=os.environ.get("ILETINIZ_API_KEY"))
    try:
        info = client.messages.retrieve(sys.argv[1])
    except IletinizNotFoundError:
        print("Mesaj bulunamadı.", file=sys.stderr)
        sys.exit(1)
    print(info)


if __name__ == "__main__":
    main()
