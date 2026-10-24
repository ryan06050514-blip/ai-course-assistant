"""Step 4：工具呼叫——模型決定要用哪個工具，程式負責執行。"""
import json
import os
import sys
import urllib.request

from agent.llm import get_llm

PLATFORM = os.getenv("PLATFORM_URL", "http://localhost:8080")
WEATHER = {"台中": "多雲 26°C", "台北": "陣雨 23°C", "高雄": "晴 30°C"}


def get_weather(city: str) -> str:
    return WEATHER.get(city, "查無資料")


def count_messages() -> str:
    """呼叫 Lab 4 平台的 API（經過 Nginx）。"""
    with urllib.request.urlopen(f"{PLATFORM}/api/messages", timeout=5) as r:
        return f"目前最新 {len(json.load(r))} 筆留言"


TOOLS = {"get_weather": get_weather, "count_messages": count_messages}
SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_weather", "description": "查詢台灣城市今天的天氣",
        "parameters": {"type": "object", "required": ["city"],
                       "properties": {"city": {"type": "string", "description": "城市名，例如 台中"}}}}},
    {"type": "function", "function": {
        "name": "count_messages", "description": "查詢 AI 平台留言板目前有幾筆留言",
        "parameters": {"type": "object", "properties": {}}}},
]

llm = get_llm(sys.argv[1] if len(sys.argv) > 1 else None)
question = sys.argv[2] if len(sys.argv) > 2 else "台中今天天氣如何？留言板現在有幾筆留言？"
messages = [{"role": "user", "content": question}]
for turn in range(5):  # 最多 5 回合，避免無限迴圈
    r = llm.client.chat.completions.create(model=llm.model, messages=messages, tools=SCHEMAS)
    msg = r.choices[0].message
    if not msg.tool_calls:
        print(f"\n最終回答（第 {turn + 1} 回合）：\n{msg.content}")
        break
    messages.append(msg.model_dump(exclude_none=True))
    for call in msg.tool_calls:
        args = json.loads(call.function.arguments or "{}")
        result = TOOLS[call.function.name](**args)
        print(f"🔧 {call.function.name}({args}) → {result}")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
