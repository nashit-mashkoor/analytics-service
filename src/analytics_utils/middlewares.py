import uuid
from logging import getLogger

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = getLogger("analytics-ingest-service")


class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        cid = str(uuid.uuid4())

        request.state.cid = cid
        logger.info(
            "Received request",
            extra={
                "method": request.method,
                "url": str(request.url),
                "cid": cid,
            },
        )
        response = await call_next(request)
        return response
