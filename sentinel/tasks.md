# 任務清單 (Task List)

> [!NOTE]
> 本文件由使用者提供原始素材清單。Agent 將依序執行知識萃取與落地。
> 所有任務已於 2026-07-09 全數歸檔至 `sentinel/archive/tasks_20260709.md`。

---

## 執行注意事項

1. 每完成一項萃取任務，立刻標記 [x]，避免重複消耗 API quota
2. extract_img 指令務必加上 --resume，支援中斷後繼續
3. 產生出的 Markdown 必須置於 `wiki/` 目錄，並滿足最小落地契約
4. Phase 1 的過渡草稿請放置於 `scratch/` 或直接回傳於對話中
