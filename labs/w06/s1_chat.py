"""Step 1：第一次呼叫，看 token、延遲與花費。用法：uv run python -m labs.w06.s1_chat [profile]"""
import sys
import time

from agent.llm import cost_usd, get_llm

llm = get_llm(sys.argv[1] if len(sys.argv) > 1 else None)
t0 = time.perf_counter()
r = llm.client.chat.completions.create(
    model=llm.model,
    messages=[
        {"role": "system", "content": "你是企業 AI 平台課程的助教，用繁體中文回答。"},
        {"role": "user", "content": "用兩句話說明什麼是 token。"},
    ],
    temperature=0.2,
)
dt = time.perf_counter() - t0
u = r.usage
print(r.choices[0].message.content)
print(f"\n[{llm.profile}] {llm.model}  輸入 {u.prompt_tokens} / 輸出 {u.completion_tokens} tokens"
      f"  {dt:.1f}s  ≈ US${cost_usd(llm.model, u.prompt_tokens, u.completion_tokens):.6f}")
