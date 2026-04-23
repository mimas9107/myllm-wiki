# LLM-Wiki: 主動式個人知識庫 (Active Personal Knowledge Base)

一個基於「自動化監控」與「層次化編譯」理念構建的個人知識庫。不同於傳統的靜態 Wiki 或單純的 RAG 檢索，本專案強調知識的**主動複利**與**自動維護**。

## 核心理念 (Core Concept)

大多數知識管理系統只是資料的「堆放場」。LLM-Wiki 的目標是讓知識庫成為一個**會呼吸的有機體**：
- **Incremental Compilation (增量編譯)**: 新資訊不是被「儲存」，而是被「集成」進既有的知識網絡。
- **Persistent Compounding (持續複利)**: 交叉引用、矛盾檢測與總結合成是自動完成的，知識會隨時間變得越發豐富。

## 系統架構 (Architecture)

系統採用 **Tiered Processing (層次化處理)** 架構：

### 第一線 (Tier 1): Wiki-Watchdog (The Sentinel)
- **角色**: 基於 Python 的檔案系統監控守護進程。
- **任務**: 偵測 `raw/` 異動，調用本地 **Ollama** 進行「初級摘要」與「任務掛號」。
- **工具**: Python `watchdog`, Ollama (預設 `qwen2.5:1.5b`)。

### 第二線 (Tier 2): Knowledge Manager (Antigravity)
- **角色**: 高階 AI 代理人。
- **任務**: 讀取初級摘要，進行深度整合、更新 `wiki/` 頁面、維護 `INDEX.md` 與 `log.md`。
- **目標**: 確保結構一致性與高品質的知識產出。

## 目錄結構

- `raw/`: 原始素材區（唯讀，Agent 不得修改）。
- `wiki/`: 正式知識庫（由 AI 維護的 Markdown 檔案）。
- `outputs/`: 供人工/AI 審閱後匯入 Wiki 的正式報告或長篇合成。
- `sentinel/`: 守護者工作區（包含初級摘要、狀態指紋、任務清單與日誌）。
- `scripts/`: 系統工具腳本。

## 快速開始

請參閱 [[QUICKSTART.md]] 以獲取安裝與操作指南。

---
*Developed by Antigravity in collaboration with the USER.*
