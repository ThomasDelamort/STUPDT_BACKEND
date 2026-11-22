import re
import time
import html
import logging
from typing import Dict, List, Tuple, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

class SlidingWindowRateLimiter:
    """
    In-memory thread-safe sliding-window rate limiter per client IP and endpoint prefix.
    """
    def __init__(self):
        self._requests: Dict[str, List[float]] = {}
        self.route_limits: Dict[str, Tuple[int, int]] = {
            "/api/chat": (40, 60),
            "/api/gemini": (40, 60),
            "/api/vision/analyze": (15, 60),
            "/api/apology/download": (25, 60),
            "/api/bureaucracy/submit": (35, 60),
            "/api/captcha/verify": (35, 60),
            "default": (120, 60)
        }

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "127.0.0.1"

    def check(self, request: Request) -> Tuple[bool, int, int]:
        """
        Checks whether the incoming request is within allowed rate limits.
        Returns (is_allowed, remaining, retry_after)
        """
        ip = self._get_client_ip(request)
        path = request.url.path

        limit_tuple = self.route_limits.get(path)
        if not limit_tuple:
            for route_prefix, lim in self.route_limits.items():
                if route_prefix != "default" and path.startswith(route_prefix):
                    limit_tuple = lim
                    break
        if not limit_tuple:
            limit_tuple = self.route_limits["default"]

        max_reqs, window_secs = limit_tuple
        now = time.time()
        key = f"{ip}:{path}"

        history = self._requests.setdefault(key, [])
        history = [ts for ts in history if now - ts < window_secs]
        self._requests[key] = history

        if len(history) >= max_reqs:
            oldest_in_window = history[0]
            retry_after = max(1, int(window_secs - (now - oldest_in_window)))
            return False, 0, retry_after

        history.append(now)
        remaining = max_reqs - len(history)
        return True, remaining, 0


rate_limiter = SlidingWindowRateLimiter()


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Applies OWASP security headers, payload size limits, and rate limiting to all requests.
    """
    MAX_VISION_SIZE = 12 * 1024 * 1024
    MAX_DEFAULT_SIZE = 512 * 1024

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length_str = request.headers.get("content-length")
        if content_length_str:
            try:
                content_length = int(content_length_str)
                path = request.url.path
                max_size = self.MAX_VISION_SIZE if "/vision" in path or "/gemini" in path else self.MAX_DEFAULT_SIZE
                if content_length > max_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "detail": f"Payload entity exceeds security limit of {max_size // (1024 * 1024) or (max_size // 1024)} KB.",
                            "blame": "Excessive Data Transmission",
                            "code": "PAYLOAD_TOO_LARGE"
                        }
                    )
            except ValueError:
                pass

        if not request.url.path.startswith("/api/health"):
            allowed, remaining, retry_after = rate_limiter.check(request)
            if not allowed:
                headers = {
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after)
                }
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "StuPDT Anti-Impatience Protocol: You have exceeded allowed request frequency. Please wait.",
                        "retryAfter": retry_after,
                        "blame": "Excessive Customer Urgency",
                        "code": "RATE_LIMIT_EXCEEDED"
                    },
                    headers=headers
                )

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-StuPDT-Firewall"] = "Certified Incompetent & Secure v99.97"
        
        response.headers["Server"] = "StuPDT-Secure-Gateway"

        return response


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitizes string against null bytes, control characters, and escapes HTML entities.
    Truncates to max_length.
    """
    if not text:
        return ""
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    escaped = html.escape(cleaned.strip())
    return escaped[:max_length]


def sanitize_filename(filename: Optional[str]) -> str:
    """
    Sanitizes filename against path traversal attacks (e.g. ../../etc/passwd).
    """
    if not filename:
        return "unnamed_file"
    import os
    base = os.path.basename(filename)
    safe = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base)
    return safe[:100] or "unnamed_file"


def validate_image_magic(data: bytes, mime_type: Optional[str] = None) -> bool:
    """
    Validates image binary against file magic signatures to prevent executable/script uploads.
    """
    if not data or len(data) < 12:
        return False

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    if data.startswith(b"\xff\xd8\xff"):
        return True
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return True
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return True

    return False
