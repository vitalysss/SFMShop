import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.api.lifespan import lifespan
from src.api.middleware import log_requests
from src.api.routes import auth, external
from src.api.routes.orders import router as orders_router
from src.api.routes.products import router as products_router
from src.api.routes.versioned_products import v1_router, v2_router
from src.config import DEBUG

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="SFMShop API",
    description=(
        "Backend интернет-магазина: каталог, JWT-аутентификация, "
        "заказы и фоновые задачи."
    ),
    version="1.0.0",
    lifespan=lifespan,
    debug=DEBUG,
)
app.middleware("http")(log_requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(v1_router)
app.include_router(v2_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(
    external.router,
    prefix="/api/v1",
)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}


@app.get("/admin", include_in_schema=False)
async def admin_page():
    path = Path(__file__).resolve().parents[2] / "templates" / "admin.html"

    return FileResponse(path)
