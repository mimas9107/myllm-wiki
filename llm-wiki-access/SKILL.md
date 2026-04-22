---
name: llm-wiki-access
description: Access and ground knowledge from the personal LLM Wiki knowledge base.
---

# Skill: LLM Wiki Knowledge Access

此技能允許 AI Agent 存取與檢索位於本機的結構化知識庫 (LLM Wiki)，協助使用者回溯過往專案、技術文檔與原始素材。

## 核心配置
- **LLM_WIKI_PATH**: `{{config.LLM_WIKI_PATH}}` (預設為 `~/projects/llm-wiki`)
- **Wiki 目錄**: `{{config.LLM_WIKI_PATH}}/wiki`
- **Raw 素材目錄**: `{{config.LLM_WIKI_PATH}}/raw`

## 觸發條件
當使用者要求：
- 「查詢關於某專案的資訊」
- 「找回之前的筆記或會議紀錄」
- 「了解特定技術的 SOP 或安裝指南」
- 「分析目前的知識儲備」

## 代理執行流程 (漸進式檢索)

### Step 1: 目錄掃描 (Orientation)
首先讀取索引檔案，了解知識庫的全貌：
- 讀取 `{{config.LLM_WIKI_PATH}}/wiki/INDEX.md`
- 讀取 `{{config.LLM_WIKI_PATH}}/wiki/專案總覽.md` (如果是專案相關問題)

### Step 2: 關鍵字檢索 (Search)
如果索引中沒有直接匹配的項，使用 `rg` (ripgrep) 進行全文檢索：
```bash
rg -i "關鍵字" "{{config.LLM_WIKI_PATH}}/wiki/"
```

### Step 3: 知識導航與提取 (Navigation)
找到對應的 Wiki 頁面後，讀取內容：
- 提取 **摘要 (Summary)** 提供快速回答。
- 查看 **相關連結 (Links)** 進行知識關聯跳轉。

### Step 4: 知識落地 (Grounding)
**這是最重要的步驟**。Agent 必須找出 Wiki 頁面底部的「檔案連結 (File Links)」或「來源檔案 (Source Links)」，指向 `{{config.LLM_WIKI_PATH}}/raw/` 底下的真實路徑。
- 如果是程式碼，指向 `{{config.LLM_WIKI_PATH}}/raw/projects/...`
- 如果是文件，指向 `{{config.LLM_WIKI_PATH}}/raw/Documents/...`

### Step 5: 回應使用者
在回應中，除了提供知識內容外，必須附上「落地連結」，格式建議：
- **詳細文檔**: [頁面名稱](file://{{config.LLM_WIKI_PATH}}/wiki/FileName.md)
- **原始源碼/素材**: [原始位置](file://{{config.LLM_WIKI_PATH}}/raw/...)

## 使用注意事項 (Constraints)
1. **唯讀原則**: Agent 嚴禁修改 `{{config.LLM_WIKI_PATH}}/raw/` 內的任何檔案。
2. **同步更新**: 如果發現 `raw/` 有新素材但 Wiki 尚未涵蓋，應主動建議更新 Wiki。
3. **路徑一致性**: 務必使用環境變數 `{{config.LLM_WIKI_PATH}}` 以確保在不同機器上的相容性。

---
*維護者: Antigravity*
