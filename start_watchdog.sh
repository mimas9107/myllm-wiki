#!/bin/bash

# Wiki-Watchdog 啟動腳本 (v1.3.1)
# 用途：自動偵測環境並啟動第一線 (Tier 1) 監控服務

BASE_DIR=$(cd "$(dirname "$0")"; pwd)
VENV_PATH="$BASE_DIR/.venv"
SCRIPT_PATH="$BASE_DIR/scripts/wiki_watchdog.py"
SENTINEL_DIR="$BASE_DIR/sentinel"
LOG_PATH="$SENTINEL_DIR/watchdog.log"

echo "------------------------------------------"
echo "正在啟動 Wiki-Watchdog Sentinel..."
echo "------------------------------------------"

# 0. 建立管理目錄
mkdir -p "$SENTINEL_DIR"

# 1. 檢查虛擬環境
if [ ! -d "$VENV_PATH" ]; then
    echo "錯誤: 找不到虛擬環境 (.venv)。"
    echo "請先執行: python3 -m venv .venv && ./.venv/bin/pip install watchdog requests"
    exit 1
fi

# 2. 清理舊進程
OLD_PID=$(ps aux | grep wiki_watchdog.py | grep -v grep | awk '{print $2}')
if [ ! -z "$OLD_PID" ]; then
    echo "正在關閉舊進程 (PID: $OLD_PID)..."
    kill $OLD_PID
    sleep 1
fi

# 3. 啟動服務
echo "正在後台啟動監控服務..."
nohup "$VENV_PATH/bin/python3" -u "$SCRIPT_PATH" > "$LOG_PATH" 2>&1 &

# 4. 驗證
sleep 2
NEW_PID=$(ps aux | grep wiki_watchdog.py | grep -v grep | awk '{print $2}')
if [ ! -z "$NEW_PID" ]; then
    echo "啟動成功！PID: $NEW_PID"
    echo "管理目錄: $SENTINEL_DIR"
    echo "日誌路徑: $LOG_PATH"
    echo "------------------------------------------"
    tail -n 3 "$LOG_PATH"
else
    echo "啟動失敗，請檢查日誌: $LOG_PATH"
fi
