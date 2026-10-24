# 在 api 容器裡執行：docker compose exec api python -m agent.selfcheck
import urllib.error
import urllib.request

for path in ("/health", "/messages"):
    try:
        with urllib.request.urlopen(f"http://localhost:8000{path}", timeout=5) as r:
            print(f"{path:10} {r.status}  {r.read().decode()[:120]}")
    except urllib.error.HTTPError as e:
        print(f"{path:10} {e.code}  {e.read().decode()[:120]}")
