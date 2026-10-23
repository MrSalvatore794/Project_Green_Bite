"""Validate WxPusher notification configuration.

Usage (run from the ``server`` directory):

    python scripts/wxpusher_config.py

This reports whether notifications are enabled and how many recipient UIDs are
configured. It never prints the app token or the UID values themselves.

Setup (from the WxPusher management console at https://wxpusher.zjiecode.com/):
  1. Create a standard-push application and copy its appToken.
  2. Ask the merchant to follow the application to obtain their UID.
  3. Set the environment variables (see server/README.md and .env.example):
       WXPUSHER_APP_TOKEN=AT_xxx
       WXPUSHER_UIDS=UID_xxx,UID_yyy
"""

import sys

from config import Config
from services.notifications import WxPusherNotificationService


def main() -> None:
    service = WxPusherNotificationService(
        app_token=Config.WXPUSHER_APP_TOKEN,
        uids=Config.WXPUSHER_UIDS,
    )

    if not service.is_configured():
        print(
            "WxPusher notifications are DISABLED "
            "(WXPUSHER_APP_TOKEN and WXPUSHER_UIDS must both be set)."
        )
        return

    print("WxPusher notifications are ENABLED.")
    print(f"Recipients: {len(service.uids)}")
    print("App token is set (value not shown).")


if __name__ == "__main__":
    sys.exit(main())
