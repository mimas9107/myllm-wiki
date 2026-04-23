# LLM-Wiki: 主動式個人知識庫 (Active Personal Knowledge Base)

一個基於「自動化監控」與「層次化編譯」理念構建的個人知識庫。不同於傳統的靜態 Wiki 或單純的 RAG 檢索，本專案強調知識的**主動複利**與**自動維護**。

## 核心理念與方法論 (Core Concept & Methodology)

本專案的方法論源自 **Andrej Karpathy 提出的 LLM Wiki 模式**。綜觀 GitHub 上近期排名前列的相關開源實踐（如 `llm_wiki`、`llm-wiki-agent`、`claude-obsidian` 等），皆共同探討了此模式對傳統 RAG（檢索增強生成）的關鍵突破：傳統 RAG 每次面對提問都必須「從零開始」檢索並拼湊片段，無法形成系統性的知識累積；而 LLM Wiki 模式則讓 LLM 扮演長期的知識庫維護者，將原始資料主動轉化為結構化且相互連結的持久性維基。

相較於將資料當作「堆放場」的傳統做法，LLM-Wiki 的目標是讓知識庫成為一個**會呼吸的有機體**：
- **Incremental Compilation (增量編譯)**: 新進的原始素材不是僅被「儲存」等待檢索，而是由 LLM 主動閱讀、提取，並「集成」進既有的知識網絡中。
- **Persistent Compounding (持續複利)**: 交叉引用、實體頁面更新、矛盾檢測與總結合成皆由 AI 自動完成。知識不再隨單次問答而消散，而是會隨著時間的推移而產生複利效應，變得越發豐富與立體。

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

## 致謝
- Andrej Karpathy: [[LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)]

---
*Developed by Antigravity in collaboration with the USER.*
