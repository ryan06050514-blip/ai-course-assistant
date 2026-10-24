"""Step 6：同一個題目，比較本地與雲端（延遲、token、估計花費），輸出 compare.md。"""
import sys
import time
from pathlib import Path

from agent.llm import cost_usd, get_llm

PROMPT = "請用 100 字以內，向主管說明為什麼 AI 平台要把資料層放在 internal 網路。"
profiles = sys.argv[1:] or ["local"]
rows = []
for p in profiles:
    llm = get_llm(p)
    t0 = time.perf_counter()
    try:
        msgs = [{"role": "user", "content": PROMPT}]
        r = llm.client.chat.completions.create(model=llm.model, messages=msgs)
    except Exception as e:  # 沒有金鑰或網路不通時繼續比下一個
        rows.append(f"| {p} | {llm.model} | 失敗：{type(e).__name__} | | | |")
        continue
    dt = time.perf_counter() - t0
    u = r.usage
    rows.append(f"| {p} | {llm.model} | {dt:.1f}s | {u.prompt_tokens} | {u.completion_tokens} "
                f"| {cost_usd(llm.model, u.prompt_tokens, u.completion_tokens):.6f} |")
    print(f"--- {p} ---\n{r.choices[0].message.content}\n")
head = "| profile | model | 延遲 | 輸入 | 輸出 | US$ |\n|---|---|---|---|---|---|\n"
table = head + "\n".join(rows)
Path("compare.md").write_text(table + "\n", encoding="utf-8")
print(table)
