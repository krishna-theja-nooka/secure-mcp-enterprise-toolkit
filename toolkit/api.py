import logging
import sqlite3
from pathlib import Path
from uuid import uuid4

from fastapi import Body, FastAPI, Request, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from toolkit.config import Settings
from toolkit.models import ToolResult
from toolkit.service import SCHEMAS, Service

STATIC = Path(__file__).parent / "static"
auth = APIKeyHeader(name="X-API-Key", auto_error=False)


def create_app(settings=None):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    service = Service(settings or Settings.load())
    app = FastAPI(
        title="Enterprise Tool Console",
        version="0.1.0",
        description="Synthetic local MCP toolkit. Supply X-API-Key for protected APIs.",
    )
    app.state.service = service
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"]
    )

    @app.middleware("http")
    async def headers(request: Request, call_next):
        # JSON APIs reject oversized bodies before parsing. Chunked requests are bounded too.
        if request.method == "POST":
            size = 0
            chunks = []
            async for chunk in request.stream():
                size += len(chunk)
                if size > 8192:
                    return JSONResponse(
                        {"error": "Request exceeds 8 KiB.", "trace_id": str(uuid4())}, 413
                    )
                chunks.append(chunk)
            request._body = b"".join(chunks)
        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", str(uuid4()))
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        if not request.url.path.startswith(("/docs", "/redoc")):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
            )
        return response

    def invoke(request, operation, payload=None, approval_id=None):
        result, status = service.call(
            operation, payload or {}, request.headers.get("X-API-Key"), approval_id
        )
        return JSONResponse(result.model_dump(), status, headers={"X-Request-ID": result.trace_id})

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/health")
    def health():
        return {"status": "ok", "synthetic": True}

    @app.get("/ready")
    def ready():
        try:
            with service.store.connect() as con:
                con.execute("SELECT COUNT(*) FROM vehicles").fetchone()
            configured = bool(service.settings.keys)
            return JSONResponse(
                {"status": "ready" if configured else "credentials_required"},
                200 if configured else 503,
            )
        except sqlite3.Error:
            return JSONResponse({"status": "storage_unavailable"}, 503)

    @app.get("/api/schemas")
    def schemas():
        return {name: cls.model_json_schema() for name, cls in SCHEMAS.items()}

    @app.post("/api/tools/{tool}", response_model=ToolResult)
    def tool(
        tool: str,
        request: Request,
        arguments: dict = Body(...),
        api_key: str | None = Security(auth),
    ):
        if tool not in {"analytics", "documents", "propose_ticket"}:
            return JSONResponse({"error": "Unknown tool"}, 404)
        return invoke(request, tool, arguments)

    @app.post("/api/approvals/{approval_id}/decision", response_model=ToolResult)
    def decide(
        approval_id: str,
        request: Request,
        decision: dict = Body(...),
        api_key: str | None = Security(auth),
    ):
        return invoke(request, "decide", decision, approval_id)

    @app.get("/api/{view}", response_model=ToolResult)
    def view(view: str, request: Request, api_key: str | None = Security(auth)):
        if view not in {"approvals", "tickets", "metrics", "audit"}:
            return JSONResponse({"error": "Unknown view"}, 404)
        return invoke(request, view)

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app
