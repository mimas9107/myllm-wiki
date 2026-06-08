---
name: llm-wiki-flush-知識沖刷技能
description: 將 outputs/ 中的深度分析、合成報告或暫存知識點，正式「沖刷 (Flush)」並「注入 (Inject)」至 wiki/ 知識庫中。
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
# llm-wiki-flush 知識沖刷技能

本 Skill 用於解決「合成知識碎片化」的問題。當使用者下達「執行知識沖刷」或「Flush outputs」時，Agent 必須遵循以下標準化流程。

## 路徑防呆與安全邊界
1. **【絕對禁區】**：嚴禁修改、寫入或覆蓋 `raw/` 與 `sentinel/` 目錄下的任何檔案
2. **【注入目標】**：知識注入只能寫入 `wiki/` 目錄下的現有檔案
3. **【綜述目標】**：建立新的 Synthesis 頁面時，路徑必須是 `wiki/Synthesis-*.md`
4. **【歸檔限制】**：完成後的報告只能移動到 `outputs/archive/`，嚴禁使用 `rm` 直接刪除檔案

## 執行流程

### 1. 盤點階段 (Inventory)
- 掃描 `outputs/` 目錄中尚未整合的 `.md` 檔案
- 讀取 `wiki/log.md`，確認哪些報告已被標記為完成整合

### 2. 雙軌整合策略

#### 軌道 A：結論注入 (Insight Injection)
針對報告中提到的具體技術細節、錯誤修正或優化建議，直接更新至對應的原子頁面

#### 軌道 B：建立專題綜述 (Synthesis Hub)
如果報告是關於多個領域的「跨界合成」，在 `wiki/` 下建立新的專題彙整頁面

### 3. 完工動作
1. 更新 INDEX：在 `wiki/INDEX.md` 的「跨領域合成」區塊掛載新建立的綜述頁面
2. 紀錄 Log：在 `wiki/log.md` 增加紀錄
3. 強制存檔：將已完成沖刷的原始輸出檔案移動至 `outputs/archive/`

## 來源檔案連結
- [技能定義](file:///opt/myllm-wiki/raw/project/SKILLS/llm-wiki_skills/llm-wiki-flush/SKILL.md)

## 相關主題
- [[llm-wiki-skills-維基知識庫管理技能集]]
- [[llm-wiki-access-知識庫存取技能]]
- [[llm-wiki-lint-知識庫健康檢查]]