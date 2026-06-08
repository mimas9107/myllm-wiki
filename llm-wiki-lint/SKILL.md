---
name: llm-wiki-lint
description: 執行知識庫健康檢查，尋找孤島頁面 (Orphans)、死結連結 (Broken Links)、Frontmatter 不完整、Tag 非法、頁面過大、Stale 內容、品質信號不足與雙向連結不足。
---

# llm-wiki-lint 執行協定

## 系統防護與路徑邊界 (System Guardrails)
1. **唯讀掃描 (Read-Only Scan)**：掃描期間嚴禁修改 `wiki/` 或 `raw/` 下的任何內容。
2. **報告隔離 (Report Isolation)**：掃描結果**必須且只能**寫入 `sentinel/lint_report.md`。絕對禁止寫入 `outputs/`，以免污染知識產出區。
3. **人工授權 (User Authorization)**：產生報告後，Agent 必須停止動作並等待 User 檢閱。嚴禁未經 User 同意便自動修復 INDEX 或刪除檔案。

## 前置讀取 (Orientation)

執行任何檢查前，**必須**讀取以下檔案：
1. `wiki/SCHEMA.md` — 作為所有檢查的標準依據
2. `wiki/INDEX.md` — 作為孤島/索引完整性檢查的基准
3. `wiki/log.md`（最近 20 行）— 了解近期變動，避免誤報剛建立的頁面

## 檢查清單

### 1. 孤島頁面 (Orphans)
比對 `wiki/*.md` 檔案列表與 `wiki/INDEX.md` 中的 `[[內部連結]]`，列出所有未被 INDEX 紀錄的檔案。

### 2. 斷鏈 (Broken Links)
讀取 `wiki/*.md` 內的所有 `[[內部連結]]`，驗證目標檔案是否存在。

### 3. Frontmatter 完整性
根據 `wiki/SCHEMA.md` 第 3 節檢查每個頁面的 YAML Header：
- 必填欄位齊全：`name`, `description`, `type`, `tags`, `confidence`, `contested`, `contradictions`, `sources`, `created`, `updated`, `contributors`
- 日期格式合法：`YYYY-MM-DD`
- `type` 必須是 SCHEMA.md 定義的 5 種之一
- `confidence` 必須是 `high` / `medium` / `low` 之一
- `contested` 必須是 `true` / `false`

### 4. Tag 合法性
根據 `wiki/SCHEMA.md` 第 5.1 節的領域標籤清單檢查：
- 列出頁面中所有不存在的標籤
- 標記為「待補錄」或「待移除」

### 5. 頁面大小 (Page Size)
根據 `wiki/SCHEMA.md` 第 6 節：
- 列出超過 200 行的頁面，標記為「待拆分候選」

### 6. Stale 內容 (Staleness)
根據 `wiki/SCHEMA.md` 第 7 節：
- 檢查 `updated` 欄位，超過 90 天未更新的頁面列入觀察
- 結合 `sentinel/states.json` 中是否有新來源提及同實體

### 7. 品質信號 (Quality Signals)
根據 `wiki/SCHEMA.md` 第 6 節：
- 列出 `confidence: low` 的所有頁面
- 列出單一來源且無 `confidence` 欄位的頁面（應補 `medium` 或尋找 corroboration）

### 8. 雙向連結最低門檻
根據 `wiki/SCHEMA.md` 第 8.2 節：
- 每頁 **outbound** wikilinks 數 < 2 的列出
- 每頁 **inbound** wikilinks 數 = 0 的列出（INDEX 掛載不算 inbound）

## 報告格式

掃描結果寫入 `sentinel/lint_report.md`，格式如下：

```markdown
# Wiki Lint Report
> Generated: YYYY-MM-DD HH:MM
> Total pages: N

## Critical (必須處理)
- **Broken Links（N 個）**: ...
- **Missing Frontmatter（N 個）**: ...

## Warnings (建議處理)
- **Orphans（N 個）**: ...
- **Invalid Tags（N 個）**: ...
- **Stale Pages（N 個）**: ...
- **Low Confidence（N 個）**: ...
- **Page Size > 200 lines（N 個）**: ...
- **Inbound < 1（N 個）**: ...
- **Outbound < 2（N 個）**: ...

## Info
- 上次 lint 日期: ...
- 建議動作: ...
```

## 向下相容說明

- 原有 orphan/broken link 掃描保留
- 輸出格式仍為 `sentinel/lint_report.md`
- 修復流程仍走 `sentinel/tasks.md` 兩階段編譯（Phase 1 分析 → Phase 2 修復）
- 僅在 User 明確授權後才執行修復

## 與 SCHEMA.md 的依賴關係

本 Skill 的檢查標準**完全引用** `wiki/SCHEMA.md`。
若 `wiki/SCHEMA.md` 不存在，則跳過第 3-8 項檢查，僅執行第 1-2 項（向後相容）。
