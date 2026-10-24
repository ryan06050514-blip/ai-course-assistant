"""Step 2：串流輸出，量測第一個字出現的時間（TTFT）。"""
import sys
import time

from agent.llm import get_llm

llm = get_llm(sys.argv[1] if len(sys.argv) > 1 else None)
t0 = time.perf_counter()
first = None
stream = llm.client.chat.completions.create(
    model=llm.model,
    messages=[{"role": "user", "content": "用三點條列說明容器和虛擬機的差別。"}],
    stream=True,
    stream_options={"include_usage": True},
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        first = first or time.perf_counter()
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.usage:
        usage = chunk.usage
total = time.perf_counter() - t0
print(f"\n\nTTFT {first - t0:.2f}s　總時間 {total:.2f}s　輸出 {usage.completion_tokens} tokens"
      f"　≈ {usage.completion_tokens / (total - (first - t0)):.1f} tokens/s")
