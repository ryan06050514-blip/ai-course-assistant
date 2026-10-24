# 第 5 週 Lab 4：Docker 三層式網站（教師參考解答／學生 starter）

Windows 10/11 + Docker Desktop（WSL 2 後端），指令以 PowerShell 為準。

```
瀏覽器 ──:8080──▶ web (Nginx)          frontend 網路
                    │ /api/* → api:8000
                    ▼
                  api (FastAPI)         frontend + backend + ai
                  │            │
        SQL :5432 ▼            ▼ OpenAI API :11434
          db (PostgreSQL 18)   ollama
          backend（internal）  ai 網路
```

| 檔案 | 層 | 用途 |
|---|---|---|
| `web/Dockerfile`、`web/nginx.conf`、`web/index.html` | 展示層 | 靜態網頁＋反向代理 |
| `Dockerfile`、`agent/api.py` | 應用層 | uv multi-stage、FastAPI（/health、/messages、/ask） |
| `db/init.sql` | 資料層 | 第一次建立 volume 時建表 |
| `compose.yaml` | 全部 | 4 個服務、3 個網路、2 個 volume |
| `compose.gpu.yaml` | AI 服務 | 有 NVIDIA 顯卡時疊加使用 |
| `Dockerfile.naive` | — | 反面教材 |
| `agent/selfcheck.py` | 應用層 | 在 api 容器內檢查 /health 與 /messages |
| `.env.example`、`.gitattributes`、`.dockerignore` | — | 密碼範本、LF 換行、建置排除 |

## 一次跑完（PowerShell）

```powershell
Copy-Item .env.example .env          # 改密碼
docker compose up -d --build
docker compose exec ollama ollama pull qwen3:0.6b
start http://localhost:8080
docker compose exec api python -m agent.selfcheck
```

NVIDIA GPU：`docker compose -f compose.yaml -f compose.gpu.yaml up -d`

## 隔離驗證

```powershell
docker compose exec web wget -qO- http://api:8000/health   # 成功
docker compose exec web wget -T 3 http://db:5432           # bad address 'db'
docker compose exec db wget -T 3 http://1.1.1.1            # 逾時（internal）
Test-NetConnection localhost -Port 5432                    # False
```
