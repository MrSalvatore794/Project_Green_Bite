"""Optional WxPusher merchant notification service.

Notifications are best-effort: they are triggered only after an order has been
committed, and any failure here must never affect the order result. The service
is disabled when configuration is incomplete.

Reference (official): https://wxpusher.zjiecode.com/
"""

import json
import logging
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

WXPUSHER_SEND_URL = "https://wxpusher.zjiecode.com/api/send/message"
# WxPusher business success code (the HTTP status may be 200 even on failure).
SUCCESS_CODE = 1000


class NotificationError(Exception):
    """Raised when a notification cannot be delivered (network or provider)."""


class WxPusherNotificationService:
    """Send new-order notifications to the merchant through WxPusher."""

    def __init__(self, app_token="", uids="", timeout=5.0, http_post=None):
        self.app_token = app_token or ""
        self.uids = self._parse_uids(uids)
        self.timeout = timeout
        # Injectable HTTP seam so tests can mock network requests.
        self._http_post = http_post or self._default_post

    @staticmethod
    def _parse_uids(uids) -> list[str]:
        if isinstance(uids, str):
            return [uid.strip() for uid in uids.split(",") if uid.strip()]
        return [uid for uid in (uids or []) if uid]

    def is_configured(self) -> bool:
        """Return True when both an app token and at least one UID are set."""
        return bool(self.app_token and self.uids)

    def send_new_order_notification(self, order) -> bool:
        """Send a best-effort notification for a newly created order.

        Never raises: delivery failures are logged and reported as ``False`` so
        the caller can treat notification as optional.
        """
        if not self.is_configured():
            return False

        try:
            self._send(self._build_payload(order))
            return True
        except NotificationError as exc:
            logger.warning("WxPusher notification failed: %s", exc)
            return False
        except Exception:  # defensive: never let notification break ordering
            logger.exception("Unexpected error sending WxPusher notification.")
            return False

    def _build_payload(self, order) -> dict:
        """Build the JSON payload without exposing secrets or customer data."""
        lines = [
            f"New order #{order.id}",
            f"Total: ${order.total_amount:.2f}",
            f"Pickup: {order.pickup_date} {order.pickup_time}",
            f"Payment: {order.payment_status}",
            "Items:",
        ]
        for item in order.items:
            lines.append(f"- {item.product_name} x{item.quantity}")

        return {
            "appToken": self.app_token,
            "content": "\n".join(lines),
            "summary": f"New order #{order.id}",
            "contentType": 1,
            "uids": self.uids,
        }

    def _send(self, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        try:
            response = self._http_post(data)
        except urllib.error.HTTPError as exc:
            raise NotificationError(f"HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise NotificationError(f"network error: {exc.reason}") from exc
        except TimeoutError as exc:
            raise NotificationError("timeout") from exc
        except NotificationError:
            raise
        except Exception as exc:
            raise NotificationError(str(exc)) from exc

        status = getattr(response, "status", None)
        if status is None and hasattr(response, "getcode"):
            try:
                status = response.getcode()
            except Exception:
                status = None

        try:
            body = response.read().decode("utf-8", "replace")
        except Exception as exc:
            raise NotificationError("failed to read response") from exc

        if status is not None and int(status) >= 400:
            raise NotificationError(f"HTTP {status}")

        try:
            result = json.loads(body)
        except json.JSONDecodeError as exc:
            raise NotificationError("malformed response") from exc

        if result.get("code") != SUCCESS_CODE:
            raise NotificationError(f"provider code {result.get('code')}")

    def _default_post(self, data: bytes):
        request = urllib.request.Request(
            WXPUSHER_SEND_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urllib.request.urlopen(request, timeout=self.timeout)
