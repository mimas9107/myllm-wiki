---
name: SPEC.md
description: 專案功能規格書 (Project Specification)
created_date: "2026/06/08"
modified_date: "2026/06/08"
project_version: "1.4.0"
document_version: "1.0.0"
agent_sign: ['Antigravity']
---

# LLM-Wiki 專案規格書

## 1. 專案概述

| 項目 | 說明 |
|------|------|
| 專案名稱 | LLM-Wiki (Active Personal Knowledge Base) |
| 版本 | 1.4.0 |
| 核心理念 | 自動化監控 + 層次化編譯 + Schema 驅動治理 |
| 維護者 | Antigravity |

## 2. 功能規格

### 2.1 雙層處理架構

| 層級 | 名稱 | 技術棧 | 職責 |
|------|------|--------|------|
| Tier 1 | Wiki-Watchdog (Sentinel) | Python watchdog + Ollama (qwen2.5:1.5b) | 檔案監控、初級摘要、任務掛號 |
| Tier 2 | Knowledge Manager | Hermes Agent (nous) | 深度整合、Wiki 更新、INDEX/log 維護 |

### 2.2 目錄結構與權限

| 目錄 | 權限 | 說明 |
|------|------|------|
| `raw/` | **唯讀 (RO)** | 原始素材，Agent 絕對不可修改/刪增任何字元 |
| `wiki/` | AI 維護 (RW) | 正式知識庫，遵循最小落地契約 |
| `outputs/` | 緩衝區 (RW) | 延伸報告、問答結案、待遷移知識 |
| `sentinel/` | 系統管理 (RW) | tasks.md, states.json, hot.md, lint_report.md |
| `scripts/` | 執行 (RX) | 工具腳本 |

### 2.3 SCHEMA.md 規範內容 (v1.4.0 新增)

| 區段 | 說明 |
|------|------|
| 1. Domain Declaration | 專案域名、版本、schema_version |
| 2. Frontmatter 必填欄位 | 11 欄位：name, description, type, tags, confidence, contested, contradictions, sources, created, updated, contributors |
| 3. 頁面類型 | entity, concept, comparison, query, summary (5 種) |
| 4. Tag 分類體系 | 11 大類對應 INDEX.md 分類 |
| 5. Page Thresholds | 拆分門檻 200 行、警告門檻 150 行 |
| 6. Update Policy | 高信度 ≤ 30 天、中信度 ≤ 90 天、低信度 ≤ 180 天 |
| 7. Provenance Markers | `^[raw/...]` 格式，source link 格式規範 |
| 8. INDEX/Log 維護 | 雙向連結門檻：outbound ≥ 2, inbound ≥ 1 |
| 9. Raw/ 唯讀宣告 | 絕對不可修改 |
| 10. States.json 去重 | sha256 + last_processed |

### 2.4 技能生態

| Skill | 功能 | 權限 |
|-------|------|------|
| `llm-wiki-lint` | 8-check health scan (SCHEMA-driven) | 唯讀掃描，報告隔離至 sentinel/ |
| `llm-wiki-flush` | outputs/ → wiki/ 結構化遷移 | 人工授權觸發 |
| `llm-wiki-access` | 知識庫查詢與檢索 | 唯讀 |
| `llm-wiki-serendipity` | 隨機知識發現 | 最高權限覆寫，純人工啟動 |

### 2.5 查準工具

| 工具 | 用途 | 特性 |
|------|------|------|
| `backfill-frontmatter.py` | 缺失欄位補全 | 保守式 insert-before-closing-fence，支援 3/4-dash fence |
| `version-sync-checker` | 版本一致性檢查 | 跨檔案版本同步 |

## 3. 非功能規格

### 3.1 向下相容性
- 所有變更採 **Additive Only** 機制：只新增欄位/檔案，不刪除/重命名既有結構
- `llm-wiki-lint` 若偵測不到 SCHEMA.md，自動退回到 legacy 2-check 模式

### 3.2 資料完整性
- `states.json` 以 sha256 追蹤 `raw/` 檔案指紋，防止重複 Ingest
- `raw/` 目錄符號連結治理：禁止遞迴掃描，按需精確存取

### 3.3 審計追蹤
- 所有 Wiki 異動必須記錄於 `wiki/log.md`
- `sentinel/hot.md` 為上下文恢復檔案，每輪工作結束必須更新

## 4. 介面規格

### 4.1 CLI 介面
```bash
# Frontmatter 回填
python3 scripts/backfill-frontmatter.py [wiki_dir]

# 版本同步檢查
python3 scripts/version_sync_checker.py
```

### 4.2 Hermes Agent 啟動掛載
每次 session 啟動必讀：
1. `purpose.md`
2. `wiki/SCHEMA.md`
3. `sentinel/hot.md`

## 5. 版本規則

| 規則 | 說明 |
|------|------|
| 語意化版本 | MAJOR.MINOR.PATCH |
| 進位規則 | 10 PATCH → 1 MINOR，10 MINOR → 1 MAJOR |
| 文件版本 | document_version 獨立追蹤 |

## 6. 部署環境

| 環境 | 路徑 | 用途 |
|------|------|------|
| Source (dev) | `~/project/myllm-wiki/` | 開發、修改、測試 |
| Production | `/opt/myllm-wiki/` | 實際運行，手動同步 |

---

*規格版本 1.0.0 | 對應專案版本 1.4.0*