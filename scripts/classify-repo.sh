#!/bin/sh
# classify-repo.sh - 判斷專案類別: private | public | hybrid | unknown
# 用法: ./scripts/classify-repo.sh
# 優先級: 1. .repo-class 檔案 (明確意圖)  2. Remote 掃描 (啟發式)

set -e

# 1. 優先讀取 .repo-class (專案宣告的意圖)
if [ -f "$(git rev-parse --show-toplevel 2>/dev/null)/.repo-class" ]; then
    class=$(grep -E '^class=' "$(git rev-parse --show-toplevel)/.repo-class" | cut -d= -f2 | tr -d ' ')
    case "$class" in
        private|public|hybrid) echo "$class"; exit 0 ;;
    esac
fi

# 2. 回退: 掃描所有 remote URL (啟發式判斷)
remotes=$(git remote -v 2>/dev/null || echo "")

has_gitea=$(echo "$remotes" | grep -q 'gitea\.home' && echo yes || echo no)
has_github=$(echo "$remotes" | grep -q 'github\.com' && echo yes || echo no)
has_codeberg=$(echo "$remotes" | grep -q 'codeberg\.org' && echo yes || echo no)

# 判斷邏輯
if [ "$has_gitea" = "yes" ] && [ "$has_github" = "no" ] && [ "$has_codeberg" = "no" ]; then
    echo "private"
elif [ "$has_github" = "yes" ] || [ "$has_codeberg" = "yes" ]; then
    if [ "$has_gitea" = "yes" ]; then
        echo "hybrid"
    else
        echo "public"
    fi
else
    echo "unknown"
fi