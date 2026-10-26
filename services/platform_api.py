import logging
import re
import sqlite3
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from services.api_gateway.rate_limiter import RateLimiter
from services.api_gateway.routes import ROUTES
from services.auth_service.schemas import (
    DemoUser,
    TokenValidationRequest,
    TokenValidationResponse,
)
from services.auth_service.service import AuthService, has_permission
from services.monitoring_service.metrics import Metrics
from shared.config import Settings
from shared.database import DemoDatabase
from shared.logging_config import configure_logging, request_id_context

logger = logging.getLogger(__name__)
_DASHBOARD_PATH = Path(__file__).resolve().parent.parent / "web" / "dashboard.html"

ISSUE_FIXTURES = (
    ("ECP-1", "Resolve intermittent authentication service failures"),
    ("ECP-2", "Implement centralized identity and access management"),
    ("ECP-3", "Configure API gateway routing and rate limiting"),
    ("ECP-4", "Automate CI/CD pipeline for containerized services"),
    ("ECP-5", "Resolve database connection pool exhaustion under load"),
    ("ECP-6", "Complete platform security and dependency review"),
    ("ECP-7", "Provision infrastructure through version-controlled IaC"),
    ("ECP-8", "Build cloud infrastructure monitoring dashboard UI"),
    ("ECP-9", "Fix dashboard layout overflow on smaller screens"),
)


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


def create_app(
    settings: Settings | None = None,
    database: DemoDatabase | None = None,
) -> FastAPI:
    app_settings = settings or Settings()
    db = database or DemoDatabase(
        app_settings.database_path,
        app_settings.database_timeout_seconds,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        db.initialize()
        logger.info("Platform demo started")
        yield
        logger.info("Platform demo stopped")

    app = FastAPI(title=app_settings.app_name, version="0.1.0", lifespan=lifespan)
    app.state.settings = app_settings
    app.state.database = db
    app.state.auth_service = AuthService()
    app.state.metrics = Metrics()
    app.state.rate_limiter = RateLimiter(
        app_settings.rate_limit_requests,
        app_settings.rate_limit_window_seconds,
    )

    @app.middleware("http")
    async def observe_request(request: Request, call_next):
        request_id = request.headers.get("x-request-id", "").strip()
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", request_id):
            request_id = str(uuid.uuid4())
        context_token = request_id_context.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - started) * 1000
            route = request.scope.get("route")
            path = route.path if route is not None else "unmatched"
            app.state.metrics.record(path, response.status_code, elapsed_ms)
            logger.info(
                "Request completed method=%s path=%s status_code=%s response_time_ms=%.3f",
                request.method,
                path,
                response.status_code,
                elapsed_ms,
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception:
            logger.exception("Unhandled request error")
            raise
        finally:
            request_id_context.reset(context_token)

    def raise_api_error(status_code: int, code: str, message: str) -> None:
        raise HTTPException(
            status_code=status_code,
            detail={"code": code, "message": message},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict):
            code = str(exc.detail.get("code", "http_error"))
            message = str(exc.detail.get("message", "The request could not be completed."))
        else:
            code = "http_error"
            message = str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code,
                    "message": message,
                    "request_id": request_id_context.get(),
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        _: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "The request did not match the required schema.",
                    "request_id": request_id_context.get(),
                }
            },
        )

    async def enforce_rate_limit(request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        allowed, retry_after = request.app.state.rate_limiter.check(client)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "code": "rate_limit_exceeded",
                    "message": "Request limit exceeded. Retry after the indicated interval.",
                },
                headers={"Retry-After": str(retry_after)},
            )

    async def authenticated_user(
        request: Request,
        authorization: Annotated[str | None, Header()] = None,
    ) -> DemoUser:
        if authorization is None:
            raise_api_error(401, "authentication_required", "A bearer token is required.")
        scheme, separator, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not separator or not token.strip():
            raise_api_error(401, "authentication_required", "A valid bearer token is required.")
        result = request.app.state.auth_service.validate(token.strip())
        if result.user is None:
            if result.error_code == "credential_expired":
                raise_api_error(401, "credential_expired", "The demo credential has expired.")
            raise_api_error(401, "invalid_credentials", "The demo credential is not valid.")
        return result.user

    router = APIRouter(
        prefix="/api/v1",
        dependencies=[Depends(enforce_rate_limit)],
        responses={
            401: {"model": ErrorResponse, "description": "Authentication required or invalid."},
            403: {"model": ErrorResponse, "description": "Permission denied."},
            422: {"model": ErrorResponse, "description": "Request validation failed."},
            429: {"model": ErrorResponse, "description": "Rate limit exceeded."},
        },
    )

    @app.get("/health", response_model=None)
    async def health(request: Request) -> dict[str, object] | JSONResponse:
        try:
            database_healthy = request.app.state.database.ping()
        except sqlite3.Error:
            logger.exception("Database health check failed")
            database_healthy = False
        health_report = {
            "status": "healthy" if database_healthy else "degraded",
            "services": {"api": "healthy", "database": "healthy" if database_healthy else "unavailable"},
        }
        if not database_healthy:
            return JSONResponse(status_code=503, content=health_report)
        return health_report

    @router.get("/auth/health")
    async def auth_health() -> dict[str, str]:
        return {"status": "healthy", "mode": "local_demo_only"}

    @router.post("/auth/validate", response_model=TokenValidationResponse)
    async def validate_token(
        payload: TokenValidationRequest,
        request: Request,
    ) -> TokenValidationResponse:
        result = request.app.state.auth_service.validate(payload.token)
        if result.user is None:
            if result.error_code == "credential_expired":
                raise_api_error(401, "credential_expired", "The demo credential has expired.")
            raise_api_error(401, "invalid_credentials", "The demo credential is not valid.")
        request_id = request_id_context.get()
        request.app.state.database.record_event("auth.validation.succeeded", request_id)
        return TokenValidationResponse(valid=True, user=result.user, request_id=request_id)

    @router.get("/users/me", response_model=DemoUser)
    async def get_current_user(
        user: Annotated[DemoUser, Depends(authenticated_user)],
    ) -> DemoUser:
        return user

    @router.get("/operations/status")
    async def operations_status(
        user: Annotated[DemoUser, Depends(authenticated_user)],
    ) -> dict[str, str]:
        if not has_permission(user.role, "operations:read"):
            raise_api_error(403, "permission_denied", "This route requires the operator role.")
        return {"status": "available", "access": "operator"}

    @router.get("/admin/status")
    async def admin_status(
        user: Annotated[DemoUser, Depends(authenticated_user)],
    ) -> dict[str, str]:
        if not has_permission(user.role, "admin:read"):
            raise_api_error(403, "permission_denied", "This route requires the admin role.")
        return {"status": "available", "access": "admin"}

    @router.get("/metrics")
    async def metrics(request: Request) -> dict[str, object]:
        return request.app.state.metrics.snapshot()

    @router.get("/routes")
    async def routes() -> dict[str, object]:
        return {"source": "local_gateway_configuration", "routes": ROUTES}

    @router.get("/demo/issues")
    async def demo_issues() -> dict[str, object]:
        return {
            "source": "static_fixture_not_live_jira",
            "issues": [{"key": key, "title": title} for key, title in ISSUE_FIXTURES],
        }

    app.include_router(router)

    @app.get("/dashboard", include_in_schema=False)
    async def dashboard() -> FileResponse:
        return FileResponse(_DASHBOARD_PATH, media_type="text/html")

    return app


app = create_app()
