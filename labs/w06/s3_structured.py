"""Step 3：結構化輸出——把客服信件變成程式讀得懂的 JSON。"""
import sys
from typing import Literal

from pydantic import BaseModel, Field

from agent.llm import get_llm


class Ticket(BaseModel):
    category: Literal["帳號", "付款", "技術問題", "其他"]
    priority: Literal["低", "中", "高"]
    summary: str = Field(description="20 字以內的摘要")
    needs_human: bool


EMAIL = "我昨天付款兩次被重複扣款 3,200 元，客服電話一直打不通，今天下班前一定要處理！"

llm = get_llm(sys.argv[1] if len(sys.argv) > 1 else None)
r = llm.client.chat.completions.parse(
    model=llm.model,
    messages=[
        {"role": "system", "content": "把客服信件分類，只輸出符合 schema 的 JSON。"},
        {"role": "user", "content": EMAIL},
    ],
    response_format=Ticket,
    temperature=0,
)
ticket = r.choices[0].message.parsed
print(ticket.model_dump_json(indent=2))
assert isinstance(ticket, Ticket)  # 程式可以直接用欄位
print("→ 需要轉真人：" if ticket.needs_human else "→ 自動回覆即可：", ticket.summary)
