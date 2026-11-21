import re
import time
import html
import logging
from typing import Dict, List, Tuple, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# =============================================================================
# 1. SLIDING WINDOW RATE LIMITER
# =============================================================================
class SlidingWindowRateLimiter:
    """
    In-memory thread-safe sliding-window rate limiter per client IP and endpoint prefix.
    """
    def __init__(self):
        # Stores: { "ip:endpoint": [timestamp1, timestamp2, ...] }
        self._requests: Dict[str, List[float]] = {}
        # Route-specific limits (max_requests, window_seconds)
        self.route_limits: Dict[str, Tuple[int, int]] = {
            "/api/chat": (40, 60),          # 40 requests / minute for Chat AI
            "/api/gemini": (40, 60),        # 40 requests / minute for Gemini proxy
            "/api/vision/analyze": (15, 60),# 15 requests / minute for Vision AI (payload heavy)
            "/api/apology/download": (25, 60), # 25 downloads / minute for PDF generation
            "/api/bureaucracy/submit": (35, 60), # 35 submissions / minute
            "/api/captcha/verify": (35, 60),     # 35 verify attempts / minute (brute-force defense)
            "default": (120, 60)            # 120 requests / minute for general endpoints
        }

    def _get_client_ip(self, request: Request) -> str:
        # Check standard reverse proxy headers
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

        # Determine route limit
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

        # Clean old timestamps
        history = self._requests.setdefault(key, [])
        history = [ts for ts in history if now - ts < window_secs]
        self._requests[key] = history

        if len(history) >= max_reqs:
            oldest_in_window = history[0]
            retry_after = max(1, int(window_secs - (now - oldest_in_window)))
            return False, 0, retry_after

        # Record this request
        history.append(now)
        remaining = max_reqs - len(history)
        return True, remaining, 0


rate_limiter = SlidingWindowRateLimiter()


# =============================================================================
# 2. SECURITY HEADERS & BODY SIZE LIMIT MIDDLEWARE
# =============================================================================
class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Applies OWASP security headers, payload size limits, and rate limiting to all requests.
    """
    MAX_VISION_SIZE = 12 * 1024 * 1024     # 12 MB for image uploads
    MAX_DEFAULT_SIZE = 512 * 1024           # 512 KB for standard JSON bodies

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Payload Size Verification
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

        # 2. Rate Limiting Check (bypass internal health checks)
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

        # 3. Process Request
        response = await call_next(request)

        # 4. Inject OWASP Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-StuPDT-Firewall"] = "Certified Incompetent & Secure v99.97"
        
        # Obfuscate / override server banner
        response.headers["Server"] = "StuPDT-Secure-Gateway"

        return response


# =============================================================================
# 3. INPUT SANITIZATION & SECURITY UTILITIES
# =============================================================================
def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitizes string against null bytes, control characters, and escapes HTML entities.
    Truncates to max_length.
    """
    if not text:
        return ""
    # Strip null bytes & control chars (except standard whitespace)
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    # Escape HTML to prevent XSS
    escaped = html.escape(cleaned.strip())
    # Truncate
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

    # Signatures
    # PNG: \x89PNG\r\n\x1a\n
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    # JPEG: \xff\xd8\xff
    if data.startswith(b"\xff\xd8\xff"):
        return True
    # WEBP: RIFF....WEBP
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return True
    # GIF: GIF87a or GIF89a
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return True

    return False
