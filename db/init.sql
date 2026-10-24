-- 只在資料目錄是空的時候執行一次（第一次建立 volume）
CREATE TABLE IF NOT EXISTS messages (
    id         SERIAL PRIMARY KEY,
    author     TEXT NOT NULL,
    content    TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO messages (author, content)
VALUES ('system', '資料層初始化完成');
