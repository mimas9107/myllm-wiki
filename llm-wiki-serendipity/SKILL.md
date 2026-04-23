---
name: llm-wiki-serendipity
description: 隨機抽取不相關的知識頁面進行碰撞，激發跨領域的靈感與應用場景。
---

# llm-wiki-serendipity 執行協定

## 最高權限覆寫規則 (Supreme Override Rule)
> **拒絕自動觸發**：本技能嚴禁由 Agent 在自主推論、排程或上下文關聯中主動調用。
> **唯一觸發條件**：必須且只能由 User 透過明確的自然語言指令（例如：「執行知識碰撞」）來啟動。若無 User 授權，Agent 必須拒絕執行此技能。

## 執行邊界 (Guardrails)
1. **沙盒隔離**：生成的靈感文章**必須且只能**存放在 `outputs/` 目錄下（命名建議：`outputs/serendipity_[主題].md`）。
2. **禁止直寫**：絕對禁止將產出的靈感直接寫入 `wiki/` 或 `INDEX.md`。這些產出必須等待未來 User 觸發 `llm-wiki-flush` 才能被整合。

## 執行流程
1. 從 `wiki/` 隨機選取 2~3 篇看似無關的原子筆記。
2. 進行深度聯想，撰寫一段結合這些領域的新創意、潛在架構或解決方案。
3. 將結果存入 `outputs/`，並回報 User。
