---
name:          "AGENTS.md"
description:   "Active Wiki Protocol - 原子化更新與索引治理"
created_date:  "2026/05/29 13:25:00"
modified_date: "2026/06/18 10:45:00"
project_version: "1.5.0"
document_version: "1.1.0"
agent_sign: ['human/mimas', 'gemini cli/gemini-cli']
---

# MyLLM-Wiki 知識庫管理與維護協定 (AGENTS.md)

本文件定義此專案的特化開發行為。Agent 必須同時遵循工作區全域規範 (../AGENTS.md)。

## 1. 強制執行清單 (Post-Action Checklist)
- 每次異動必須更新 wiki/INDEX.md、wiki/log.md 與 sentinel/hot.md。
- 新頁面必須符合「最小落地契約」（禁止空白頁、必須有來源、必須有雙向連結）。
## 2. 目錄治理
- raw/: 絕對唯讀。
- sentinel/: 管理心臟 (tasks.md, states.json)。
- Symlink 禁令: 嚴禁對 Symlink 執行遞迴掃描，僅限按需探訪。

---
*註：本文件專注於專案業務與技術細節，通用環境指令與 Token 節約準則請查閱全域規範。*
