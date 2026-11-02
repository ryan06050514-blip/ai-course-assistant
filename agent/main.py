import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
from llm import get_llm  # 匯入您寫好的 llm.py 設定

app = FastAPI()

# 🛡️ 允許跨網域存取 (CORS)，這能防止 GitHub Pages 連線時被瀏覽器阻擋
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 實際上線時也可以改成您固定的 GitHub Pages 網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模擬的記憶體資料庫（提供前端顯示學習紀錄使用）
MOCK_HISTORY = [
    {"author": "系統管理員", "content": "歡迎來到 AI 智慧學習助理！後端已成功連接。", "at": datetime.now().isoformat()}
]

class AskRequest(BaseModel):
    question: str

@app.get("/api/health")
def health_check():
    """檢查後端與 AI 狀態"""
    try:
        llm_instance = get_llm()
        return {"status": "ok", "profile": llm_instance.profile, "model": llm_instance.model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages")
def get_messages():
    """獲取歷史學習紀錄"""
    return MOCK_HISTORY

@app.post("/api/ask/stream")
async def ask_stream(request: AskRequest):
    """AI 串流（Streaming）文本生成"""
    try:
        llm_instance = get_llm()
        
        # 呼叫您 llm.py 中設定好的 OpenAI SDK 客戶端與模型
        response = llm_instance.client.chat.completions.create(
            model=llm_instance.model,
            messages=[
                {"role": "system", "content": "你是一個專業的繁體中文技術導師，請使用簡單易懂的短句、Markdown 格式以及生活實例來回答問題。"},
                {"role": "user", "content": request.question}
            ],
            stream=True
        )

        async def event_generator():
            full_reply = ""
            for chunk in response:
                if chunk.choices and chunk.choices.delta.content:
                    token = chunk.choices.delta.content
                    full_reply += token
                    yield token
                    await asyncio.sleep(0.01) # 增加微小延遲讓前端打字機效果更流暢
            
            # 回答結束後，將對話紀錄存入歷史紀錄中
            MOCK_HISTORY.append({
                "author": "AI 助手",
                "content": full_reply,
                "at": datetime.now().isoformat()
            })

        return StreamingResponse(event_generator(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 本地測試時，在 VS Code 終端機執行 python main.py
    # 就會在 http://localhost:8000 啟動伺服器
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)