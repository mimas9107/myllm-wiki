---
name: MEMOIR.md
description: 跨語言架構一致性備忘錄 - 環境指紋與契約驗證
created_date: "2026/06/08"
modified_date: "2026/06/08"
project_version: "1.4.0"
document_version: "1.0.0"
agent_sign: ['Antigravity']
---

# MEMOIR: 架構決策與契約備忘錄

> 參考 `memoir-driven-dev-v2` 技能：以環境指紋確保跨語言/跨 Agent 的架構一致性。

---

## 1. 環境指紋

```yaml
project: myllm-wiki
version: 1.4.0
schema_version: "1.0"
primary_agent: Antigravity (Hermes/nous)
tier1_engine: Ollama qwen2.5:1.5b
tier2_provider: Nous Portal (stepfun/step-3.7-flash:free)
os: Debian 13 (x86_64)
paths:
  source: /home/mimas/project/myllm-wiki
  production: /opt/myllm-wiki
  raw: /opt/myllm-wiki/raw  (symlinks to external)
```

---

## 2. 核心契約

### 2.1 最小落地契約 (MLC) - 強制
每個正式 `wiki/` 頁面**必須**滿足：
- [ ] YAML Header 含 11 個必填欄位 (SCHEMA.md §2)
- [ ] 至少 1 句定位摘要 + 1 個「相關主題」區塊 + 1 個來源連結
- [ ] `INDEX.md` 已掛載 `[[頁面名稱]]`
- [ ] `log.md` 有異動記錄
- [ ] 雙向連結：outbound ≥ 2, inbound ≥ 1 (INDEX 不算 inbound)
- [ ] `raw/` 絕對不被修改

### 2.2 兩階段編譯工作流 - 強制
```
Phase 1 (分析) → scratch/ 或對話輸出「分析草稿」
                    ↓ 確認邏輯無誤
Phase 2 (落地) → 正式寫入 wiki/、更新 INDEX、寫 log、改 hot.md
```

### 2.3 互動式問答緩衝區 - 強制
- `outputs/` 為臨時知識緩衝，**禁止自動併入 wiki/**
- 遷移觸發條件：人工指令或 `llm-wiki-flush` skill
- 遷移必須走 Phase 1→2 流程

---

## 3. 關鍵決策記錄 (ADR)

| ADR | 日期 | 決策 | 原因 |
|-----|------|------|------|
| ADR-001 | 2026-04-22 | 採雙層架構 + sentinel/ 隔離 | 職責分離、raw/ 唯讀 |
| ADR-002 | 2026-05-14 | 最小落地契約寫入 AGENTS.md | 防止空頁/孤島頁 |
| ADR-003 | 2026-06-08 | SCHEMA.md 為單一真實來源 | Frontmatter/lint/threshold 統一標準 |
| ADR-004 | 2026-06-08 | 回填腳本採 conservative insert | 保留既有 fence 風格，不動 body |
| ADR-005 | 2026-06-08 | Source/Production 手動同步 | 避免自動推送覆蓋、方便 diff 審核 |
| ADR-006 | 2026-06-08 | Source repo 無 production wiki 內容 | Source 只存結構/腳本/規範，資料在 production |

---

## 4. 狀態機

### 4.1 原始素材生命週期
```
raw/ (新增/異動)
    ↓ watchdog 偵測
sentinel/summaries/*.md (初級摘要)
    ↓ 掛號
sentinel/tasks.md (待處理任務)
    ↓ Phase 1 分析
scratch/analysis_*.md (分析草稿)
    ↓ Phase 2 落地
wiki/*.md (正式頁面) + INDEX.md + log.md + hot.md
    ↓ 歸檔
sentinel/archive/tasks_YYYYMMDD.md + summaries_YYYYMMDD/
```

### 4.2 SCHEMA 合規狀態
```
頁面建立/修改
    ↓ lint 掃描 (llm-wiki-lint)
sentinel/lint_report.md (報告隔離)
    ↓ 人工授權
sentinel/tasks.md (修復任務)
    ↓ Phase 2 修復
wiki/*.md (合規) → 下次 lint 通過
```

---

## 5. 技能契約對照表

| Skill | 讀取契約 | 寫入契約 | 權限 |
|-------|----------|----------|------|
| `llm-wiki-lint` | SCHEMA.md, INDEX.md, log.md, states.json | sentinel/lint_report.md | 唯讀掃描 |
| `llm-wiki-flush` | outputs/*, wiki/INDEX.md, SCHEMA.md | wiki/*.md, INDEX.md, log.md | 人工授權 RW |
| `llm-wiki-access` | wiki/*, INDEX.md, raw/* | 無 | 唯讀 |
| `llm-wiki-serendipity` | wiki/*, log.md, states.json | outputs/serendipity_*.md | 最高權限覆寫 |
| `backfill-frontmatter` | wiki/*.md, INDEX.md, git log | wiki/*.md (frontmatter only) | RW (保守式) |

---

## 6. 已知風險與緩解

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| `raw/` 含 symlink 導致遞迴掃描爆炸 | Token/時間浪費 | AGENTS.md 禁止遞迴，按需精確存取 |
| 4-dash fence 被誤判 | Frontmatter 欄位插錯位置 | backfill script 用 `^-{3,}$` regex 正確識別 |
| Production wiki 內容被 source 覆蓋 | 資料遺失 | Source repo wiki/ 只保留結構性頁面，資料不同步 |
| 多 Agent 簽名污染正文 | 版本混淆 | YAML `contributors` 陣列取代正文簽名 |
| SCHEMA.md 遺失導致 lint 降級 | 檢查不完整 | AGENTS.md 啟動掛載強制讀取，缺失即報錯 |

---

## 7. 契約驗證清單 (預部署檢查)

執行部署/同步前必須通過：
- [ ] `python3 scripts/version_sync_checker.py` — 版本一致
- [ ] `python3 scripts/backfill-frontmatter.py wiki/ --dry-run` — 無新缺失欄位
- [ ] `llm-wiki-lint` 掃描 → `sentinel/lint_report.md` 無 Critical
- [ ] `git diff --stat` 人工審核 production 變更
- [ ] `sentinel/hot.md` 已更新最新上下文

---

*MEMOIR v1.0 | 對應專案版本 1.4.0 | 由 Antigravity 維護*