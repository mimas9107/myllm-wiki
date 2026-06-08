---
name: llm-wiki-access-知識庫存取技能
description: 存取並檢索個人的 LLM Wiki 知識庫，以回答使用者的問題或進行知識關聯。
contributors: [Antigravity]
type: concept
tags: []
confidence: medium
contested: false
contradictions: []
sources: []
created: 2026-06-02
updated: 2026-06-02
---
# llm-wiki-access 知識庫存取技能

讓 Agent 能夠安全、有效率地導覽並讀取使用者的本機知識庫。

## 功能特色
- 索引導航：從讀取 `wiki/INDEX.md` 開始，尋找與問題相關的頁面連結
- 連結追蹤：使用工具讀取對應的 `wiki/*.md` 檔案
- 溯源機制：需要更詳細技術規格時，再進一步讀取 `raw/` 中的內容

## 邊界條件 (Constraints)
1. **唯讀存取**：此技能僅限於讀取，嚴禁修改 `wiki/` 或 `raw/` 中的任何內容
2. **尊重原始檔案**：`raw/` 目錄是絕對唯讀的，不可變更

## 執行流程
1. 讀取 `wiki/INDEX.md` 作為檢索起點
2. 追蹤相關的內部連結 `[[頁面名稱]]`
3. 如需詳細技術規格，再溯源至 `raw/` 原始檔案

## 來源檔案連結
- [技能定義](file:///opt/myllm-wiki/raw/project/SKILLS/llm-wiki_skills/llm-wiki-access/SKILL.md)

## 相關主題
- [[llm-wiki-skills-維基知識庫管理技能集]]
- [[llm-wiki-flush-知識沖刷技能]]
- [[llm-wiki-lint-知識庫健康檢查]]