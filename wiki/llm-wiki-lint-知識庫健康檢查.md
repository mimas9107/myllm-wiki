---
name: llm-wiki-lint-知識庫健康檢查
description: 執行知識庫健康檢查，尋找孤島頁面、死結連結、Frontmatter 不完整、Tag 非法、頁面過大、Stale 內容、品質信號不足與雙向連結不足。
contributors: [Antigravity]
---
# llm-wiki-lint 知識庫健康檢查

執行知識庫健康檢查，檢視 wiki 的結構完整度與內容品質。

## 系統防護與路徑邊界
1. **唯讀掃描**：掃描期間嚴禁修改 `wiki/` 或 `raw/` 下的任何內容
2. **報告隔離**：掃描結果必須且只能寫入 `sentinel/lint_report.md`
3. **人工授權**：產生報告後，Agent 必須停止動作並等待 User 檢閱

## 前置讀取
執行檢查前必須讀取：
- `wiki/SCHEMA.md` — 作為所有檢查的標準依據
- `wiki/INDEX.md` — 作為孤島/索引完整性檢查的基準
- `wiki/log.md`（最近 20 行）— 了解近期變動

## 檢查清單
1. **孤島頁面**：比對 `wiki/*.md` 與 `INDEX.md`，找出未掛載頁面
2. **斷鏈**：驗證所有 `[[wikilinks]]` 目標檔案是否存在
3. **Frontmatter 完整性**：必填欄位、日期格式、type/confidence 值域
4. **Tag 合法性**：比對 SCHEMA.md taxonomy
5. **頁面大小**：超過 200 行列入拆分候選
6. **Stale 內容**：`updated` 超過 90 天
7. **品質信號**：`confidence: low` 或單一來源
8. **雙向連結**：outbound < 2 或 inbound = 0

## 執行流程
1. 讀取 SCHEMA.md + INDEX.md + log.md
2. 依檢查清單掃描
3. 將結果寫入 `sentinel/lint_report.md`
4. 提示 User 檢閱，未經授權不自動修復

## 與 SCHEMA.md 關係
檢查標準完全引用 `wiki/SCHEMA.md`。若 SCHEMA.md 不存在，則僅執行第 1-2 項（向後相容）。

## 來源檔案連結
- [技能定義](file:///home/mimas/project/myllm-wiki/llm-wiki-lint/SKILL.md)

## 相關主題
- [[llm-wiki-skills-維基知識庫管理技能集]]
- [[llm-wiki-access-知識庫存取技能]]
- [[llm-wiki-flush-知識沖刷技能]]
