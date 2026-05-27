import json
import time
from src.helper.response_helper import get_final_response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request, Response
from typing import Callable
from src.core.setting import settings

class RequestResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in settings.EXCLUDE_URL:
            response = await call_next(request)
            return response
        start_time = time.time()
        response = await call_next(request)

        if response.headers.get("content-type", "").startswith("text/event-stream"):
            elapsed_time = round((time.time() - start_time) * 1000, 3)
            response.headers["X-Execution-Time"] = str(elapsed_time)
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        elapsed_time = round((time.time() - start_time) * 1000, 3)

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = body.decode("utf-8", errors="replace")

        headers = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
        return JSONResponse(
            content=get_final_response(data, response.status_code, elapsed_time),
            status_code=response.status_code,
            headers=headers,
        )





