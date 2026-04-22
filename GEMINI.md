# 知識庫規則說明

## 這個知識庫是什麼
一份關於 **人工智慧、語言模型、AI 代理人、RAG、個人知識管理與數位孿生** 的個人知識庫。

## 資料夾結構
- raw/：原始素材暫存區，AI 不得修改此資料夾內的任何檔案。
- wiki/：整理後的知識庫，由 AI 全權維護，使用者不手動編輯。
- outputs/：AI 產出的報告、回答、分析歸檔。

## Wiki 維護規則
- 每個主題建立一份獨立的 .md 檔案，放在 wiki/
- 每份 wiki 檔案開頭必須有一段摘要
- 相關主題之間用 [[主題名稱]] 格式互相連結
- wiki/ 中維護一份 INDEX.md，列出所有主題
- 當 raw/ 新增素材時，主動更新相關 wiki 文章

## 我的關注方向
- 人工智慧與語言模型
- 通用 AI代理人
- RAG (Retrieval-Augmented Generation)
- 個人知識管理與數位孿生


## 資料夾規則總覽
### 禁止事項
- 任何 AI 工具嚴禁修改 `raw/` 資料夾內的檔案。
- 嚴禁破壞 `GEMINI.md` 與 `INDEX.md` 的結構。

### 工具使用規範
| 工具 | 目標 | 指令位置 |
| :--- | :--- | :--- |
| `tree` | **檢視**目錄樹狀結構 | `tree wiki/projects` |
| `find` | **搜尋**特定檔案名稱 | `find wiki/projects -name "*.md"` |
| `rg` | **全文檢索**關鍵字 | `rg "search_term" wiki/projects` |

### 工作流程範例
1. **搜尋**您感興趣的主題：<br>`rg "ESP32" wiki/projects`
2. **檢視**相關檔案：<br>`tree wiki/projects | grep "ESP32"`
3. **編輯**維護檔案：<br>`vim wiki/projects/esp-miao.md`
