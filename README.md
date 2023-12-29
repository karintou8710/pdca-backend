# PDCA

## マイグレーション手順

マイグレーションファイルを生成
```bash
$ poetry run alembic revision --automigrate -m "message"
```

最新のマイグレーションの適用
```bash
$ poetry run alembic upgrade head
```

初期状態まで戻す
```bash
$ poetry run alembic downgrade base
```
