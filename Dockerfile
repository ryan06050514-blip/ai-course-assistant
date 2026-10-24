# ① 建置階段：有 uv，負責安裝套件
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
# ② 先只裝相依：pyproject.toml / uv.lock 沒變就直接命中快取
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project
# ③ 再放程式碼：改程式只會重跑這兩層
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev
# ④ 執行階段：乾淨的 slim，不帶 uv 與快取；⑤ 以非 root 使用者執行
FROM python:3.12-slim-trixie
RUN groupadd --system app && useradd --system --gid app --no-create-home app
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
USER app
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
