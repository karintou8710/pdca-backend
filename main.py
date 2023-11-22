from fastapi import FastAPI

from api.errors import register_exception
from api.routers import user

app = FastAPI()

# 初期化
register_exception(app)


app.include_router(user.router, prefix="/api")
