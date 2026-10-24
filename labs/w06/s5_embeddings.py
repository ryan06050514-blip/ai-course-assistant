"""Step 5：Embedding 與相似度矩陣，輸出 similarity.png。"""
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from agent.llm import get_llm

SENTENCES = [
    "容器共用主機的作業系統核心",
    "Docker 讓應用程式帶著環境一起走",
    "虛擬機有自己的作業系統",
    "今天台中的天氣很好",
    "週末想去高美濕地看夕陽",
    "PostgreSQL 是關聯式資料庫",
]

llm = get_llm(sys.argv[1] if len(sys.argv) > 1 else None)
model = sys.argv[2] if len(sys.argv) > 2 else "qwen3-embedding:0.6b"
r = llm.client.embeddings.create(model=model, input=SENTENCES)
V = np.array([d.embedding for d in r.data])
V = V / np.linalg.norm(V, axis=1, keepdims=True)  # 正規化後，內積就是 cosine
S = V @ V.T
print(f"維度 {V.shape[1]}")
for i, s in enumerate(SENTENCES):
    best = max((j for j in range(len(SENTENCES)) if j != i), key=lambda j: S[i, j])
    print(f"{s[:14]:<16} 最像 → {SENTENCES[best][:14]}（{S[i, best]:.2f}）")

matplotlib.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Noto Sans CJK TC", "sans-serif"]
fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(S, cmap="Reds", vmin=0, vmax=1)
labels = [s[:8] + "…" for s in SENTENCES]
ax.set_xticks(range(len(S)), labels, rotation=45, ha="right")
ax.set_yticks(range(len(S)), labels)
for i in range(len(S)):
    for j in range(len(S)):
        ax.text(j, i, f"{S[i, j]:.2f}", ha="center", va="center", fontsize=9,
                color="white" if S[i, j] > 0.6 else "black")
fig.colorbar(im)
fig.tight_layout()
fig.savefig("similarity.png", dpi=150)
print("已輸出 similarity.png")
