from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.auth import router as auth_router
from app.routers.orders import router as orders_router
from app.routers.search import router as search_router
from app.routers.account import router as account_router
from app.routers.favorites import router as favorites_router

app = FastAPI(root_path='/api/v1')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

for router in [auth_router, orders_router, search_router,
               account_router, favorites_router]:
    app.include_router(router)
