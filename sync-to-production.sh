#!/usr/bin/env bash
# sync-to-production.sh
# 同步 source repo 結構性變更到 production，不覆蓋 production 的 wiki 內容頁

set -euo pipefail

SRC="/home/mimas/project/myllm-wiki"
DST="/opt/myllm-wiki"

echo "=== Sync source -> production ==="
echo "SRC: $SRC"
echo "DST: $DST"
echo

# 1. 同步根目錄文件
echo "[1/5] Sync root files..."
rsync -av \
  --exclude='.git/' \
  --exclude='raw/' \
  --exclude='outputs/' \
  --exclude='sentinel/' \
  --exclude='wiki/' \
  --exclude='myllm-wiki-hermes-plan.md' \
  --exclude='frontmatter-backfill.diff' \
  "$SRC/" "$DST/"

# 2. 同步 scripts/
echo "[2/5] Sync scripts/..."
rsync -av "$SRC/scripts/" "$DST/scripts/"

# 3. 同步 skills/
echo "[3/5] Sync skills..."
for skill in llm-wiki-lint llm-wiki-flush llm-wiki-access llm-wiki-serendipity; do
  if [ -d "$SRC/$skill" ]; then
    rsync -av "$SRC/$skill/" "$DST/$skill/"
  fi
done

# 4. 同步 wiki/ 結構性檔案（不包含 140+ 內容頁）
echo "[4/5] Sync wiki/ structural files..."
rsync -av \
  --include='SCHEMA.md' \
  --include='INDEX.md' \
  --include='log.md' \
  --include='llm-wiki-*' \
  --exclude='*' \
  "$SRC/wiki/" "$DST/wiki/"

# 5. 驗證
echo "[5/5] Verify key files exist in production..."
for f in \
  wiki/SCHEMA.md \
  wiki/INDEX.md \
  wiki/log.md \
  scripts/backfill-frontmatter.py \
  llm-wiki-lint/SKILL.md; do
  [ -f "$DST/$f" ] && echo "  ✓ $f" || echo "  ✗ MISSING: $f"
done

echo
echo "=== Done ==="
echo "Next steps in production:"
echo "  cd $DST"
echo "  git status"
echo "  # review, then git add + commit"