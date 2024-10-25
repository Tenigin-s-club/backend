from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(root_path='/api/v1')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f'http://localhost:{settings.FRONTEND_PORT}', 'http://localhost'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

