# MEMORY.md - 工作階段恢復指南

## 任務背景
正在整理 `/opt/myllm-wiki/raw/project/` (即 `/usr/local/home/mimas/project/`) 中的多個專案，將技術文件原子化後放進 Wiki 知識庫。

## 如何恢復進度

### Step 1: 載入 Redis Submemory 技能
```bash
# 執行以下命令來取得上次儲存的進度
python3 /home/mimas/.agents/skills/redis-submemory/scripts/redis_submemory.py get --cat state --entity wiki_organize --attr progress
```

### Step 2: 取得剩餘待處理專案清單
```bash
python3 /home/mimas/.agents/skills/redis-submemory/scripts/redis_submemory.py get --cat index --entity wiki_organize --attr remaining_projects
```

### Step 3: 查看 Sentinel 工作清單
```bash
# 確認已完成頁面數量
cat /opt/myllm-wiki/sentinel/tasks.md | head -5

# 查看最近工作記錄
cat /opt/myllm-wiki/sentinel/hot.md | head -25
```

## 已完成之 Wiki 頁面 (共 16 個)

1. **ESP-MIAO-邊緣語音助理** - `wiki/ESP-MIAO-邊緣語音助理.md`
2. **myTeleBot-機器人管理系統** - `wiki/myTeleBot-機器人管理系統.md`
3. **redis-submemory-標準化記憶介面** - `wiki/redis-submemory-標準化記憶介面.md`
4. **memoir-dev-skills-記憶驅動開發框架** - `wiki/memoir-dev-skills-記憶驅動開發框架.md`
5. **myRedis-簡易示範專案** - `wiki/myRedis-簡易示範專案.md`
6. **internal-portal-家庭網路設備管理入口** - `wiki/internal-portal-家庭網路設備管理入口.md`
7. **Auth-認證服務框架** - `wiki/Auth-認證服務框架.md`
8. **myXiaomi-智慧吸塵器控制器** - `wiki/myXiaomi-智慧吸塵器控制器.md`
9. **weathertools-天氣資料抓取工具** - `wiki/weathertools-天氣資料抓取工具.md`
10. **Linux-USB-網路設備除錯** - `wiki/Linux-USB-網路設備除錯.md`
11. **ESP32-CAM-文字識別** - `wiki/ESP32-CAM-文字識別.md`
12. **incubator-edge-system-邊緣監控系統** - `wiki/incubator-edge-system-邊緣監控系統.md`
13. **inmp441-recorder-AI語音節點** - `wiki/inmp441-recorder-AI語音節點.md`
14. **rpi-rtc-manager-樹莓派時間管理** - `wiki/rpi-rtc-manager-樹莓派時間管理.md`
15. **hackmd-agent-python-HackMD自動化工具** - `wiki/hackmd-agent-python-HackMD自動化工具.md`
16. **purr-輕量級語音客戶端** - `wiki/purr-輕量級語音客戶端.md`

## 剩餘待處理專案清單 (共 8 個)

```
[
  "keyprod_tracking",
  "mock-target",
  "myllm-wiki",
  "opencode-sandbox",
  "redis",
  "SKILLS",
  "travelplan",
  "viewpoints"
]
```

## 下一步驟

1. 從剩餘清單中挑選一個專案
2. 讀取其 `README.md` 或 `SPEC.md`
3. 建立 Wiki 頁面（遵循現有格式：YAML header + 內容 + 來源檔案連結 + 相關主題）
4. 更新 `INDEX.md` - 加入適當分類
5. 更新 `log.md` - 新增一筆維護紀錄
6. 更新 `sentinel/tasks.md` - 標記為已完成
7. 更新 `sentinel/hot.md` - 更新最近工作與統計
8. 儲存新進度至 Redis：
   ```bash
   # 更新剩餘清單
   python3 /home/mimas/.agents/skills/redis-submemory/scripts/redis_submemory.py set --cat index --entity wiki_organize --attr remaining_projects --data '[...]'
   
   # 更新進度
   python3 /home/mimas/.agents/skills/redis-submemory/scripts/redis_submemory.py set --cat state --entity wiki_organize --attr progress --data '{"status": "in_progress", "wave": "19", "pages_created": 16, "timestamp": "2026-05-11"}'
   ```

## 關鍵檔案位置

- **Wiki 目錄**: `/opt/myllm-wiki/wiki/`
- **原始專案**: `/opt/myllm-wiki/raw/project/` (符號連結至 `/usr/local/home/mimas/project/`)
- **Sentinel 目錄**: `/opt/myllm-wiki/sentinel/`
- **INDEX**: `/opt/myllm-wiki/wiki/INDEX.md`
- **Log**: `/opt/myllm-wiki/wiki/log.md`

---
*最後更新: 2026-05-11*
