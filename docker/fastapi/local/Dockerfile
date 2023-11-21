FROM python:3.10.13-bookworm
ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN apt-get update

RUN pip install poetry

COPY ../../pyproject.toml* ../../poetry.lock* ./

RUN poetry config virtualenvs.in-project true
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

# uvicornのサーバーを立ち上げる
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]