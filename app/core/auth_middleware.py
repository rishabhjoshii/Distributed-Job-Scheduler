from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import config_settings


async def auth_api_key_middleware(request: Request, call_next):
    if not config_settings.AUTH_ENABLED:
        return await call_next(request)

    path = request.url.path.rstrip("/") or "/"
    if path == "/":
        return await call_next(request)

    method = request.method.upper()

    # skip paths
    if any(path.startswith(p) for p in config_settings.parsed_skip_paths):
        return await call_next(request)

    # protect only certain methods
    protected_methods = config_settings.parsed_protected_methods
    if protected_methods and method not in protected_methods:
        return await call_next(request)

    # validate API key
    api_key = request.headers.get(config_settings.AUTH_API_KEY_HEADER)

    if not api_key or api_key not in config_settings.parsed_api_keys:
        # In middleware, return a response instead of raising to avoid 500/ExceptionGroup wrapping.
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    return await call_next(request)