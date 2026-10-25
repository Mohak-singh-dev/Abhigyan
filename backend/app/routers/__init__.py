from app.routers.health import router as health_router
from app.routers.institutions import router as institutions_router
from app.routers.complaints import router as complaints_router

__all__ = ["health_router", "institutions_router", "complaints_router"]
