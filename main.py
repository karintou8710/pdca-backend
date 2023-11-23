# flake8: noqa
from dotenv import load_dotenv  # 他のファイルをimportする前に環境変数を読み込む

load_dotenv(verbose=True)

### 以下メイン処理 ###

from fastapi import FastAPI

from api.errors import register_exception
from api.routers import user

app = FastAPI()

# 初期化
register_exception(app)


app.include_router(user.router, prefix="/api")
