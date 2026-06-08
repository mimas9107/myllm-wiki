# 維護日誌 (Log)

## [2026-04-22] Project Created
- 初始化 LLM-Wiki 知識庫架構。

## [2026-06-08] SCHEMA Integration & Lint Skill Upgrade (Source Repo)
- 新增 `wiki/SCHEMA.md`：定義 frontmatter 欄位、tag 分類、page threshold、raw/ 唯讀等規範。
- 新增 `wiki/llm-wiki-lint-知識庫健康檢查.md`：對應 SCHEMA 的 8-check protocol 說明頁。
- 新增 `wiki/llm-wiki-flush-知識沖刷技能.md`：定義 outputs/ 到 wiki/ 的遷移協議。
- 新增 `wiki/llm-wiki-access-知識庫存取技能.md`：知識庫查詢與檢索技能文件。
- 新增 `wiki/llm-wiki-serendipity-知識隨機碰撞.md`：隨機知識發現技能文件。
- 升級 `llm-wiki-lint/SKILL.md`：改為讀取 SCHEMA.md 驅動的 8-check  health protocol。
- 新增 `scripts/backfill-frontmatter.py`：保守式 frontmatter 欄位補全（支援 3/4-dash fence）。
- 修改 `AGENTS.md`：啟動掛載加入 `wiki/SCHEMA.md` 自動讀取。
- 更新 `wiki/INDEX.md`：補齊 4 個新頁面與 Governance 分類。