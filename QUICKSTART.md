# 快速入門 (Quick Start)

歡迎使用 LLM-Wiki！按照以下步驟，即可啟動您的自動化知識管理之旅。

## 1. 環境準備

確保您的系統已安裝以下工具：
- **Python 3.8+**
- **Ollama**: 請確保 Ollama 服務已啟動，並已下載推薦模型：
  ```bash
  ollama pull qwen2.5:1.5b
  ```

## 2. 初始化專案

在專案根目錄執行以下指令建立虛擬環境：
```bash
python3 -m venv .venv
./.venv/bin/pip install watchdog requests
```

## 3. 啟動守護進程 (Tier 1)

執行啟動腳本，開啟第一線監控：
```bash
./start_watchdog.sh
```
此後，所有放入 `raw/` 目錄的檔案都會自動觸發初步整理。

## 4. 匯整知識 (Tier 2)

當您想要將累積的資訊正式編譯進 Wiki 時，請喚醒您的 AI 代理人並下達指令：
> 「幫我處理 `pending_tasks.md` 中的任務。」

## 5. 檢視成果

建議配合 **Obsidian** 使用：
- 將本專案目錄作為 Obsidian Vault 開啟。
- 使用 **Graph View** 檢視 AI 自動建立的知識聯結 `[[主題]]`。

---
*Happy Knowledge Building!*
