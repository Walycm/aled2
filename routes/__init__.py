from .heroes import router as heroes_router
from .teams import router as teams_router
from .users import router as users_router

__all__ = ["heroes_router", "teams_router", "users_router"]