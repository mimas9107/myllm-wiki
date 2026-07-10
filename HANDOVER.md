# 知識庫維護交接備忘錄 (Handover Memo)

## 1. 專案概況
本專案 (myllm-wiki) 旨在建立一個以 AI 代理人、IoT 與居家照護為核心的「活體知識庫」。目前已完成核心專案的落地作業，進入「殘餘素材清理與原子化歸檔」階段。

- **當前進度**: 
  - 已建立 Wiki 頁面：61 個
  - 待處理任務：約 32 項 (詳見 `sentinel/tasks.md`)
  - 核心開發專案 (ESP-MIAO, purr, hackmd-agent 等)：**全數落地完成**。

## 2. 核心維護協定 (必讀)
接手者必須嚴格遵守 `GEMINI.md` 中的「原子化更新協定」，每項修改必須同步更新：
1. **`wiki/INDEX.md`**: 確保新頁面有正確掛載分類，嚴禁孤島頁面。
2. **`wiki/log.md`**: 紀錄維護動作。
3. **`sentinel/tasks.md`**: 將完成的任務標記為 `[x]`。
4. **`sentinel/hot.md`**: 更新近期上下文，便於下一位 Agent 銜接。

## 3. 殘餘素材分類與處理建議

### A 類：高價值技術碎料 (優先處理)
這類素材通常包含具體的硬體接線或特殊 Bug 修復，應考慮併入現有 Wiki 頁面或建立小工具頁面。
- `批量 文字轉 qrcode_.md`: 可建立「技術工具箱」分類。
- `[Raspberry Pi] 使用 1.8 TFT LCD ...`: 應併入 RPi 硬體控制相關章節。
- `智慧藥盒以yolov7v訓練模型.md`: 檢查是否與 `wiki/智慧藥盒-YOLOv7訓練.md` 有內容重疊或補充。

### B 類：IoT 訓練日記 (低優先級)
大部分內容已由上一階段 Agent 合成至 `wiki/IoT-訓練日記-主題彙整.md`。
- **處理策略**: 快速掃描是否有漏掉的程式碼範例，若無新意則直接標記為完成。

### C 類：教學簡報與二進位檔 (暫不處理)
- `raw/IoT_training/` 下的 76 個 PPTX 檔案與 SavedModel 資料夾。
- **原因**: 價值密度低，且二進位檔無法直接轉為 Markdown。

## 4. 工具與技能
- **Redis Submemory**: 使用 `activate_skill redis-submemory` 來存取任務狀態。
- **兩階段編譯 (Two-Phase Ingest)**: 遵循「先分析草稿，後正式生成」的原則，確保知識收斂至 `purpose.md` 定義的領域。

## 5. 下一步計畫建議
1. 依照 `sentinel/tasks.md` 的順序，每次選取 1-2 個 MD 檔案進行「原子化整合」。
2. 優先清理 `raw/HackMD_User_1777025612812/` 下的雜項筆記。
3. 定期檢查 `wiki/INDEX.md` 的結構是否需要調整。

---
*交接人：Gemini CLI (v1.4.0) | 日期：2026-05-11*
