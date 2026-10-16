"""ClaudeShare backend: FastAPI app serving GraphQL, transfers and the static frontend."""
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL

from .config import PORT, SOURCE_HOME, STATIC_DIR
from .resolvers.context import get_context
from .schema import schema
from .services import accounts, auth, credsync, transfer, watcher

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "same-origin",
    "Content-Security-Policy": ("default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
                                "connect-src 'self' ws: wss:; frame-ancestors 'none'; base-uri 'none'"),
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    SOURCE_HOME.mkdir(parents=True, exist_ok=True)
    SOURCE_HOME.chmod(0o700)  # the shared login's home: root only
    accounts.sync_all()
    tasks = [asyncio.create_task(watcher.loop()), asyncio.create_task(credsync.loop())]
    yield
    for task in tasks:
        task.cancel()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def guard(request: Request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS") and not auth.same_origin(request):
        return JSONResponse({"error": "Cross-origin request blocked"}, status_code=403)
    response = await call_next(request)
    for key, value in SECURITY_HEADERS.items():
        response.headers.setdefault(key, value)
    return response


@app.get("/healthz")
def healthz() -> str:
    return "ok"


app.include_router(GraphQLRouter(schema, context_getter=get_context, graphql_ide=None,
                                 subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL]), prefix="/graphql")
app.include_router(transfer.router, prefix="/files")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    # stdlib asyncio loop: uvloop cannot start subprocesses as another uid (user=/group=)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info", loop="asyncio")
