---
name: llm-wiki-lint
description: 執行知識庫健康檢查，尋找孤島頁面 (Orphans) 與死結連結 (Broken Links)。
---

# llm-wiki-lint 執行協定

## 系統防護與路徑邊界 (System Guardrails)
1. **唯讀掃描 (Read-Only Scan)**：掃描期間嚴禁修改 `wiki/` 或 `raw/` 下的任何內容。
2. **報告隔離 (Report Isolation)**：掃描結果**必須且只能**寫入 `sentinel/lint_report.md`。絕對禁止寫入 `outputs/`，以免污染知識產出區。
3. **人工授權 (User Authorization)**：產生報告後，Agent 必須停止動作並等待 User 檢閱。嚴禁未經 User 同意便自動修復 INDEX 或刪除檔案。

## 執行流程
1. **掃描孤島 (Orphans)**：比對 `wiki/*.md` 檔案列表與 `wiki/INDEX.md` 中的 `[[內部連結]]`，列出所有未被 INDEX 紀錄的檔案。
2. **掃描斷鏈 (Broken Links)**：讀取 `wiki/*.md` 內的所有 `[[內部連結]]`，驗證目標檔案是否存在。
3. **輸出報告**：將上述結果寫入 `sentinel/lint_report.md`，並在終端機提示 User 檢閱。
