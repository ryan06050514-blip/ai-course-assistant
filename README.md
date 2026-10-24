# 第 6 週｜AI 模型基礎（Lab 5：同一份程式，切換本地與雲端）

> 設計機器學習平台與系統架構（東海大學 115 學年上學期）。這是**第 6 週上課時的 repo 快照**；每週的程式都建立在前一週之上，所以這個資料夾也包含前幾週的全部內容。

環境：Windows 10/11＋Docker Desktop（WSL 2）＋uv；指令以 PowerShell 為準（換行用反引號 `）。

## 本週 Lab

- 目標：用 llm.py 抽象化模型設定，完成串流、結構化輸出、工具呼叫與 embedding
- 產出：labs/w06 六支程式、similarity.png、compare.md（本地 vs 雲端比較表）
- 原則：沒有雲端金鑰也能完成 Step 1–5；Step 6 至少比較兩個 profile

> 延續第 5 週的 repo：平台照常啟動，再加一個只開給本機的 Ollama 埠。

| 步驟 | 內容 |
|---|---|
| 1 第一次呼叫（10 分） | 建立 llm.py，跑 s1_chat：看 token 數、延遲與估計費用。 |
| 2 串流（10 分） | s2_stream：量 TTFT 與每秒 token 數，體會串流的價值。 |
| 3 結構化輸出（15 分） | s3_structured：把客服信件轉成 Pydantic 物件。 |
| 4 工具呼叫（20 分） | s4_tools：查天氣，並呼叫上週平台的 API。 |
| 5 Embedding（15 分） | s5_embeddings：六個句子的相似度矩陣圖。 |
| 6 本地 vs 雲端（20 分） | s6_compare：同一題比延遲、token 與費用，寫進 README。 |

## 課前準備：模型、套件與金鑰

- 用 dev 覆寫檔啟動平台，把 ollama 開在 127.0.0.1
- 下載 qwen3:1.7b（約 1.4 GB）與 qwen3-embedding:0.6b（約 639 MB）
- 安裝 python-dotenv，以及 Lab 用的 numpy、matplotlib
- 雲端金鑰（OpenAI／Gemini／Claude 擇一）只寫進 .env

```powershell
docker compose -f compose.yaml `
  -f compose.dev.yaml up -d
docker compose exec ollama ollama pull qwen3:1.7b
docker compose exec ollama `
  ollama pull qwen3-embedding:0.6b
curl.exe http://127.0.0.1:11434/v1/models
uv add python-dotenv
uv add --dev numpy matplotlib
notepad .env
```

其餘步驟的指令與檢查點在本週簡報的 Lab 章節。

## 本週新增與修改的檔案

相對第 5 週新增：

- `agent/llm.py`
- `labs/w06/__init__.py`
- `labs/w06/s1_chat.py`
- `labs/w06/s2_stream.py`
- `labs/w06/s3_structured.py`
- `labs/w06/s4_tools.py`
- `labs/w06/s5_embeddings.py`
- `labs/w06/s6_compare.py`

## 測試

```powershell
uv sync
uv run pytest -q
uv run ruff check .
```

## 排錯速查

| 症狀 | 原因與處理 |
|---|---|
| APIConnectionError（local） | 沒有用 compose.dev.yaml 啟動，或 ollama 還沒 healthy；curl.exe 127.0.0.1:11434 先確認。 |
| model not found | 模型名稱拼錯或還沒 pull：docker compose exec ollama ollama list。 |
| 401 Unauthorized | 金鑰錯誤、沒寫進 .env，或變數名稱不是 GEMINI_API_KEY 這類格式。 |
| 429 Too Many Requests | 免費額度的速率限制：等一下再試，或改用本地 profile。 |
| 中文字在圖上變方塊 | matplotlib 找不到中文字型：Windows 確認有 Microsoft JhengHei。 |
| 回應很慢、筆電很燙 | CPU 推論是正常的；換 qwen3:0.6b，或關掉推理模式。 |

## 各週內容在哪裡

| 週次 | 主題 | 主要檔案 |
|---|---|---|
| 第 5 週 | 容器服務：Docker 三層式網站 | web/、agent/api.py、db/、compose.yaml |
| 第 6 週 | AI 模型基礎 | agent/llm.py、labs/w06/ |

第 5 週三層式網站的完整說明：[README_w05.md](README_w05.md)。
