---
name: myllm-wiki Schema
description: 本知識庫的結構規範、命名規則與內容標準
created: 2026-06-08
updated: 2026-06-08
type: schema
tags: [schema, governance]
sources: [AGENTS.md, llm-wiki skill template]
---

# myllm-wiki Schema

> 本文件定義知識庫的結構規範、命名規則與內容標準。
> Agent 在建檔、補檔、搜索、lint 時**必須遵守**本文件。

---

## 1.  資料夾結構

```
wiki/
├── SCHEMA.md           # 本文件
├── INDEX.md            # 內容索引（單一檔案）
├── log.md              # 維護日誌（追加紀錄）
└── *.md                # 知識頁面
```

| 資料夾 | 權責 | 備註 |
|--------|------|------|
| `wiki/` | Agent 全權維護 | 正式知識區 |
| `wiki/INDEX.md` | 每次新增/刪除頁面時同步更新 | 唯一索引來源 |
| `wiki/log.md` | 每次 wiki 操作後追加紀錄 | 追加寫入，不刪除 |
| `raw/` | **絕對唯讀** | 原始素材不可修改、不可刪除 |
| `sentinel/` | Agent 全權維護 | 任務與狀態管理 |
| `outputs/` | Agent 全權維護 | 臨時報告緩衝區，flush 後才進 wiki |

---

## 2.  檔案命名

| 規則 | 說明 | 範例 |
|------|------|------|
| 小寫 + 連字號 | 無空格、無特殊字元 | `esp32-asyncwebserver-lambda.md` |
| 描述性 | 一眼看出內容 | `debain-apt-upgrade-nvidia-dkms-編譯失敗.md` |
| 日期可選 | 時間性內容可附加日期 | `report-osrm-ndk移植工程-20260529.md` |
| **raw/ 不可改名** | 原始素材路徑由 ingestion 流程記錄 | — |

---

## 3.  Frontmatter（YAML Header）

所有 `wiki/*.md` **必須**以下格式開頭：

```
---
name: 頁面標題
description: 一句話摘要描述
type: entity | concept | comparison | query | summary
tags: []
confidence: high | medium | low
contested: false
contradictions: []
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
contributors: [human/foo, Agent名]
---
```

| 欄位 | 必要性 | 說明 |
|------|--------|------|
| `name` | **必填** | 頁面標題，應與檔名一致 |
| `description` | **必填** | 一句話描述頁面內容 |
| `type` | **必填** | 見第 4 節 |
| `tags` | **必填** | 見第 5 節 |
| `confidence` | **必填** | 見第 6 節 |
| `contested` | **預設值** | `true` 表示頁面內部有未解決的爭議 |
| `contradictions` | **預設值** | 列出與本頁面衝突的其他頁面 slug |
| `sources` | **必填** | 原始來源檔案路徑列表 |
| `created` | **系統補** | 頁面首次落地日期（可由 git 補） |
| `updated` | **系統補** | 頁面最後更新日期（可由 git 補） |
| `contributors` | **必填** | `human/你的名字` + 參與的 Agent 名稱 |

### 3.1  行內溯源標記（Provenance）

在多來源綜合頁面中，主張句**建議**附上 `^[raw/...]` 標記：

```
ESP32 可透過 AsyncWebServer 實現非同步請求處理^[raw/HackMD_User_1777025612812/...md]
```

來源標記符合 `^[raw/相對路徑]` 正則即可。

---

## 4.  頁面類型（Page Types）

| type | 用途 | 命名慣例 |
|------|------|----------|
| `entity` | 具體事物：設備、專案、工具、公司、人物 | `mytelebot-機器人管理系統.md` |
| `concept` | 技術概念、術語解釋、操作指南 | `esp32-asyncwebserver-lambda.md` |
| `comparison` | 方案對比、演算法比較 | `kp01-ch-vs-mld-routing.md` |
| `query` | 問答結果、分析報告、研究筆記 | `report-osrm-ndk移植工程全知識點-20260529.md` |
| `summary` | 綜述頁、會議彙整、系列導讀 | `iot-訓練日記系列.md` |

---

## 5.  標籤分類（Tag Taxonomy）

> 新增標籤**必須先在本節登記**，然後再使用。

### 5.1  領域標籤（必用）

| 標籤 | 對應 INDEX 分類 |
|------|----------------|
| `esp32` | 微控制器與物聯網 |
| `iot` | 微控制器與物聯網 |
| `raspberry-pi` | 邊緣運算與樹莓派 |
| `ai-ml-vision` | 人工智慧與視覺辨識 |
| `dev` | 軟體開發與架構 |
| `linux` | Linux 系統管理與桌面環境 |
| `cloud` | 雲端服務與部署 |
| `gis` | 地理資訊與本地服務 |
| `agent-bot` | AI 代理人與機器人 |
| `life` | 個人筆記與生活 |
| `skill` | 技能與開發框架 |

### 5.2  功能標籤（可選）

| 標籤 | 含義 |
|------|------|
| `hardware` | 硬體操作/接線 |
| `firmware` | 韌體開發 |
| `network` | 網路與通訊 |
| `deployment` | 部署與維運 |
| `debug` | 除錯與問題排查 |
| `tutorial` | 教學/入門 |
| `reference` | 參考文件/API |
| `report` | 報告/分析 |
| `config` | 設定檔說明 |

---

## 6.  內容完整度門檻（Page Thresholds）

| 情境 | 處理方式 |
|------|----------|
| 實體/概念在 ≥2 個來源出現，或單一來源的核心內容 | **建立頁面** |
| 僅在單一來源出現一次 passing mention | **不建頁**，可加入既有頁面 |
| 頁面超過 200 行 | **拆分**，建立子頁面 + 目錄頁 |
| 內容被新來源完全取代 | **歸檔**，移至 `_archive/`，更新 INDEX |
| Stub 頁面 | **允許**，但必須滿足 SCHEMA.md 所有欄位 |

---

## 7.  更新與衝突處理（Update Policy）

| 情境 | 處理方式 |
|------|----------|
| 新資訊與舊內容衝突，且**時間較新** | 以新資訊為準，舊內容移至歷史段落 |
| 新資訊與舊內容**同等可信但結論不同** | 保留雙方案，頁面標註 `contested: true`，在 `contradictions` 列出涉案頁面 |
| 新來源與既有頁面**互補** | 補充分段落 + 更新 `sources` + bump `updated` 日期 |

---

## 8.  索引與雙向連結規則

### 8.1  INDEX.md

- `INDEX.md` 是**唯一索引來源**，所有 wiki 頁面必須掛載於此
- 每個條目格式：`- [[檔名]] 一句話摘要`
- 分類依項目 5.1 的領域標籤為準
- 頁面數超過 50 條時，分類下可建立字母子區段（`A-M` / `N-Z`）
- 總頁數超過 200 條時，建 `_meta/topic-map.md`

### 8.2  雙向連結最低門檻

| 規則 | 說明 |
|------|------|
| 每頁 **≥2 個 outbound** | 新頁面必須至少連結 2 個既有頁面 |
| 每頁 **≥1 個 inbound** | 至少 1 個既有頁面要回頭連到本頁 |
| INDEX 掛載**不算** inbound | 必須是 wiki 頁面間的 [[wikilinks]] |

---

## 9.  Log 格式規範

每次 wiki 操作後，在 `wiki/log.md` 追加：

```
## [YYYY-MM-DD] action | 動作名稱
- 操作：具體內容
- 影響檔案：列出所有建立/修改/歸檔的檔案
- 任務：sentinel/tasks.md 第 N 項
```

| action | 說明 |
|--------|------|
| `ingest` | 原始素材落地為 wiki 頁面 |
| `update` | 既有頁面內容更新 |
| `create` | 手動建立新頁面 |
| `archive` | 頁面歸檔移除 |
| `query` | 問答結果但未落地 |
| `lint` | 執行健康檢查 |

---

## 10.  核心約束

| 約束 | 說明 |
|------|------|
| **raw/ 絕對唯讀** | 原始素材不可修改、不可覆蓋、不可刪除 |
| **去重靠 sentinel/states.json** | sha256 + last_processed 為去重主力 |
| **不動 raw 檔案** | SCHEMA.md 不要求也不允許修改 raw/ |
| **雙向連結不驗 INDEX** | INDEX 掛載不能取代 wiki 頁面間的互聯 |
| **無 AI 推論污染** | 未經驗證的推論只能放 outputs/，不得進 wiki/ |

---

## 11.  與生產環境的對應關係

生產環境 `/opt/myllm-wiki` 結構更完整，增加以下模組：

- `sentinel/hot.md`（上下文恢復）
- `sentinel/states.json`（去重雜湊庫）
- `sentinel/archive/`（歸檔備份）
- `outputs/` + `llm-wiki-flush`（緩衝區沖刷）
- `llm-wiki-serendipity`（隨機碰撞）
- `purpose.md`（知識收斂方向）
- Obsidian 整合設定

上述模組**協議不變**，但不在本 SCHEMA.md 管制範圍內。SCHEMA.md 管的是「wiki 頁面本身的結構標準」。
