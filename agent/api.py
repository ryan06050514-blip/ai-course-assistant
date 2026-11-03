import os
import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from openai import APIConnectionError
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent.llm import get_llm

DB_URL = os.getenv("DATABASE_URL", "")  # 如果沒設定，psycopg 會改讀 PGHOST、PGUSER 等環境變數
llm = get_llm()  # 由 LLM_PROFILE 決定本地或雲端

class MessageIn(BaseModel):
    author: str
    content: str

class AskIn(BaseModel):
    question: str

def save(author: str, content: str) -> None:
    sql = "INSERT INTO messages (author, content) VALUES (%s, %s)"
    with psycopg.connect(DB_URL) as conn:
        conn.execute(sql, (author, content))

app = FastAPI(title="ai-platform-api")

# 🛡️ 允許跨網域存取 (CORS)，這對 GitHub Pages 連線至雲端後端至關重要
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 💡 1. 補上根路徑，防止直接打開網址時看到 404 Not Found
@app.get("/")
def index():
    return {"message": "AI Course Assistant API 後端運作中！請透過前端網頁進行連線。"}

# 💡 2. 健康檢查路徑（對齊前端 fetch(BACKEND_URL + "/health")）
@app.get("/health")
def health():
    return {"status": "ok", "profile": llm.profile, "model": llm.model}

# 💡 3. 修改為符合前端呼叫的 /messages (移除原本的 /api/messages，並從實體資料庫撈資料)
@app.get("/messages")
def list_messages():
    sql = "SELECT author, content, created_at FROM messages ORDER BY created_at DESC LIMIT 50"
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                # 💡 將資料庫的資料，轉換為前端 JavaScript 預期的欄位名稱 (author, content, at)
                return [
                    {
                        "author": row[0],
                        "content": row[1],
                        "at": row[2].isoformat() if row[2] else ""
                    }
                    for row in rows
                ]
    except Exception as e:
        # 如果資料庫暫時連不上或沒資料，先回傳空陣列讓前端網頁能正常渲染，不噴 500 錯誤
        return []

@app.post("/api/messages", status_code=201)
def add_message(m: dict):
    return {"ok": True}

@app.post("/api/ask")
def ask(q: AskIn):
    msgs = [{"role": "user", "content": q.question}]
    try:
        # 💡 終極修復：如果目前使用的是 gemini 模式，我們強制在呼叫時指定精準的官方相容網址與模型名稱
        if "gemini" in getattr(llm, "profile", "").lower() or os.getenv("LLM_PROFILE") == "gemini":
            llm.client.base_url = "https://googleapis.com"
            target_model = "models/gemini-1.5-flash"
        else:
            target_model = llm.model

        # 呼叫模型
        r = llm.client.chat.completions.create(
            model=target_model, 
            messages=msgs
        )
        
        answer = r.choices[0].message.content
        save("AI", f"Q：{q.question}\nA：{answer}")
        return {"answer": answer, "tokens": r.usage.total_tokens}
        
    except APIConnectionError:
        raise HTTPException(503, "AI 服務連線失敗（Gemini/Ollama）")
    except Exception as e:
        raise HTTPException(500, f"後端模型呼叫失敗，詳細錯誤：{str(e)}")
@app.post("/api/ask/stream")
def ask_stream(q: AskIn):
    def gen():
        parts = []
        stream = llm.client.chat.completions.create(
            model=llm.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位親切的繁體中文大學課程助教。"
                        "請使用台灣常用的繁體中文回答。"
                        "使用者問題開頭可能包含【學習模式：simple】、【學習模式：example】或【學習模式：exam】。"
                        "simple 代表簡單解釋：用白話文說明概念，再提供一個例子。"
                        "example 代表舉例說明：提供具體情境、步驟與範例。"
                        "exam 代表考前重點：整理核心觀念、常見錯誤與三道複習題。"
                        "請使用清楚的段落與條列，內容正確並適合初學者。"
                    ),
                },
                {
                    "role": "user",
                    "content": q.question,
                },
            ],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                parts.append(chunk.choices[0].delta.content)
                yield chunk.choices[0].delta.content
        save("AI", f"Q：{q.question}\nA：{''.join(parts)}")
    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")
