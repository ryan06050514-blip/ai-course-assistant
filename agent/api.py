import os

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from openai import APIConnectionError
from pydantic import BaseModel

from agent.llm import get_llm

DB_URL = os.getenv("DATABASE_URL", "")  # 空字串：改讀 PGHOST、PGUSER 等環境變數
llm = get_llm()  # 第 6 週起：由 LLM_PROFILE 決定本地或雲端

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

@app.get("/health")
def health():
    return {"status": "ok", "profile": llm.profile, "model": llm.model}

@app.get("/messages")
def list_messages():
    sql = "SELECT author, content, created_at FROM messages ORDER BY id DESC LIMIT 20"
    with psycopg.connect(DB_URL) as conn:
        rows = conn.execute(sql).fetchall()
    return [{"author": a, "content": c, "at": t.isoformat()} for a, c, t in rows]

@app.post("/messages", status_code=201)
def add_message(m: MessageIn):
    save(m.author, m.content)
    return {"ok": True}

@app.post("/ask")
def ask(q: AskIn):
    msgs = [{"role": "user", "content": q.question}]
    try:
        r = llm.client.chat.completions.create(model=llm.model, messages=msgs)
    except APIConnectionError:
        raise HTTPException(503, "AI 服務還沒啟動（ollama）")
    answer = r.choices[0].message.content
    save("AI", f"Q：{q.question}\nA：{answer}")
    return {"answer": answer, "tokens": r.usage.total_tokens}

@app.post("/ask/stream")
def ask_stream(q: AskIn):
    """第 6 週選做：串流回答，網頁可以邊產生邊顯示。"""
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
                yield parts[-1]
        save("AI", f"Q：{q.question}\nA：{''.join(parts)}")
    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")
