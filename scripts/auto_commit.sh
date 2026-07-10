#!/bin/bash
# auto_commit.sh — myllm-wiki 每日自動版控腳本
# 用途：自動 commit wiki/outputs/sentinel 的變動，並推送到 Gitea 私有 repo
# 注意：本 repo 嚴禁推送至 GitHub，僅限 localorigin (Gitea)
#
# 建議 crontab 設定（每天 23:00）：
# 0 23 * * * /opt/myllm-wiki/scripts/auto_commit.sh >> /tmp/wiki_autocommit.log 2>&1

set -euo pipefail

REPO_DIR="/opt/myllm-wiki"
LOG_PREFIX="[auto_commit $(date '+%Y-%m-%d %H:%M:%S')]"

cd "$REPO_DIR"

# 安全檢查：確認沒有 GitHub remote（防止誤推私人資料）
if git remote get-url origin &>/dev/null; then
  echo "$LOG_PREFIX ERROR: 'origin' remote 仍指向 GitHub，請立即執行: git remote remove origin"
  exit 1
fi

# 檢查是否有變動
CHANGED=$(git status --porcelain wiki/ outputs/ sentinel/ 2>/dev/null || true)

if [[ -z "$CHANGED" ]]; then
  echo "$LOG_PREFIX 無變動，跳過 commit。"
  exit 0
fi

# 計算變動檔案數
CHANGED_COUNT=$(echo "$CHANGED" | wc -l | tr -d ' ')

# Stage & commit
git add wiki/ outputs/ sentinel/tasks.md sentinel/states.json sentinel/hot.md sentinel/archive/ sentinel/summaries/ 2>/dev/null || true
git commit -m "auto: wiki snapshot $(date '+%Y-%m-%d %H:%M') [${CHANGED_COUNT} files changed]"

echo "$LOG_PREFIX Committed ${CHANGED_COUNT} changed files."

# Push 到 Gitea（僅當 localorigin 可達時）
if git remote get-url localorigin &>/dev/null; then
  if git push localorigin master; then
    echo "$LOG_PREFIX Pushed to localorigin (Gitea) successfully."
  else
    echo "$LOG_PREFIX WARNING: Push to localorigin failed（可能不在家中網路），commit 已保留在本機。"
  fi
else
  echo "$LOG_PREFIX localorigin 尚未設定，commit 僅保留本機。回家後請設定：
  git remote add localorigin ssh://git@gitea.home:12222/mimas/myllm-wiki-private.git
  git push localorigin master"
fi
