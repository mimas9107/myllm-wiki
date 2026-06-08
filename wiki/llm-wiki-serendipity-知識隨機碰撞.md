---
name: llm-wiki-serendipity-知識隨機碰撞
description: 隨機抽取不相關的知識頁面進行碰撞，激發跨領域的靈感與應用場景。
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
# llm-wiki-serendipity 知識隨機碰撞

隨機抽取不相關的知識頁面進行碰撞，激發跨領域的靈感與應用場景。

## 最高權限覆寫規則
> **拒絕自動觸發**：本技能嚴禁由 Agent 在自主推論、排程或上下文關聯中主動調用
> **唯一觸發條件**：必須且只能由 User 透過明確的自然語言指令（例如：「執行知識碰撞」）來啟動

## 執行邊界 (Guardrails)
1. **沙盒隔離**：生成的靈感文章必須且只能存放在 `outputs/` 目錄下
2. **禁止直寫**：絕對禁止將產出的靈感直接寫入 `wiki/` 或 `INDEX.md`

## 執行流程
1. 從 `wiki/` 隨機選取 2~3 篇看似無關的原子筆記
2. 進行深度聯想，撰寫一段結合這些領域的新創意、潛在架構或解決方案
3. 將結果存入 `outputs/`，並回報 User

## 來源檔案連結
- [技能定義](file:///opt/myllm-wiki/raw/project/SKILLS/llm-wiki_skills/llm-wiki-serendipity/SKILL.md)

## 相關主題
- [[llm-wiki-skills-維基知識庫管理技能集]]
- [[llm-wiki-flush-知識沖刷技能]]