#!/usr/bin/env python3
import os, re, sys, subprocess
from datetime import datetime
from pathlib import Path

WIKI_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/opt/myllm-wiki/wiki")
INDEX_FILE = WIKI_DIR / "INDEX.md"
DIFF_FILE = Path("/tmp/frontmatter-backfill.diff")

FIELDS_ORDER = ["name", "description", "type", "tags", "confidence", "contested", "contradictions", "sources", "created", "updated", "contributors"]
DEFAULTS = {"type": "concept", "tags": "[]", "confidence": "medium", "contested": "false", "contradictions": "[]", "sources": "[]", "contributors": "[Antigravity]"}

def git_last_modified(path):
    try:
        out = subprocess.check_output(["git", "-C", str(WIKI_DIR), "log", "-1", "--format=%ad", "--date=short", "--", str(path)], stderr=subprocess.DEVNULL, text=True).strip()
        if out: return out
    except Exception:
        pass
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")

def git_created(path):
    try:
        out = subprocess.check_output(["git", "-C", str(WIKI_DIR), "log", "--diff-filter=A", "--format=%ad", "--date=short", "--", str(path)], stderr=subprocess.DEVNULL, text=True).strip().splitlines()
        if out: return out[-1]
    except Exception:
        pass
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")

def is_fence(line):
    return bool(re.match(r'^-{3,}$', line.strip()))

def read_fm_keys(text):
    lines = text.splitlines(keepends=True)
    fm_lines = []
    closing_idx = None
    dash_count = 0
    for i, line in enumerate(lines):
        if is_fence(line):
            dash_count += 1
            if dash_count == 1:
                continue
            elif dash_count == 2:
                closing_idx = i
                break
        if dash_count >= 1:
            fm_lines.append(line)
    if closing_idx is None:
        return None, None
    fm = {}
    for line in fm_lines:
        m = re.match(r'^(\w+):\s*(.+)$', line.strip())
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm, closing_idx

def infer_type(slug, index_text):
    current = "concept"
    for line in index_text.splitlines():
        m = re.match(r'^##\s+(.*)', line)
        if m:
            current = m.group(1).strip()
            continue
        if f"[[{slug}]]" in line:
            if any(k in current for k in ["微控制器", "ESP32", "Arduino", "IoT"]):
                return "entity"
            if any(k in current for k in ["邊緣運算", "樹莓派"]):
                return "entity"
            if any(k in current for k in ["機器人", "代理人"]):
                return "entity"
            return "concept"
    return "concept"

def main():
    if not WIKI_DIR.is_dir():
        print(f"ERROR: {WIKI_DIR} not found", file=sys.stderr)
        sys.exit(1)
    pages = sorted([p for p in WIKI_DIR.glob("*.md") if p.name not in {"INDEX.md", "log.md", "SCHEMA.md"}])
    print(f"Found {len(pages)} wiki pages", file=sys.stderr)
    index_text = INDEX_FILE.read_text(encoding="utf-8") if INDEX_FILE.exists() else ""
    diff_lines = []
    updated_count = 0
    skipped = 0
    for path in pages:
        text = path.read_text(encoding="utf-8")
        fm, closing_idx = read_fm_keys(text)
        if fm is None or closing_idx is None:
            skipped += 1
            continue
        slug = path.stem
        new_fields = {}
        if "type" not in fm: new_fields["type"] = infer_type(slug, index_text)
        if "tags" not in fm: new_fields["tags"] = DEFAULTS["tags"]
        if "confidence" not in fm: new_fields["confidence"] = DEFAULTS["confidence"]
        if "contested" not in fm: new_fields["contested"] = DEFAULTS["contested"]
        if "contradictions" not in fm: new_fields["contradictions"] = DEFAULTS["contradictions"]
        if "sources" not in fm: new_fields["sources"] = DEFAULTS["sources"]
        if "contributors" not in fm: new_fields["contributors"] = DEFAULTS["contributors"]
        if "created" not in fm: new_fields["created"] = git_created(path)
        if "updated" not in fm: new_fields["updated"] = git_last_modified(path)
        if not new_fields:
            continue
        lines = text.splitlines(keepends=True)
        insert_lines = [f"{k}: {v}\n" for k, v in new_fields.items()]
        new_lines = lines[:closing_idx] + insert_lines + lines[closing_idx:]
        new_text = "".join(new_lines)
        if new_text != text:
            old_lines = text.splitlines(keepends=True)
            new_file_lines = new_text.splitlines(keepends=True)
            diff_lines.append(f"--- a/{path.relative_to(WIKI_DIR)}")
            diff_lines.append(f"+++ b/{path.relative_to(WIKI_DIR)}")
            diff_lines.append(f"@@ -{closing_idx-len(insert_lines)+1},{len(old_lines)} +{closing_idx+1},{len(new_file_lines)} @@")
            for ol in old_lines[max(0, closing_idx-2):closing_idx+1]:
                diff_lines.append(f"-{ol.rstrip()}")
            for nl in new_file_lines[max(0, closing_idx-2):closing_idx+len(insert_lines)+1]:
                diff_lines.append(f"+{nl.rstrip()}")
            diff_lines.append("")
            updated_count += 1
            path.write_text(new_text, encoding="utf-8")
    print(f"Updated: {updated_count}, Skipped (no valid FM): {skipped}", file=sys.stderr)
    diff_content = "\n".join(diff_lines)
    DIFF_FILE.write_text(diff_content, encoding="utf-8")
    print(f"Diff written to {DIFF_FILE}")
    print("---- DIFF START ----")
    print(diff_content[:6000])
    print("---- DIFF END ----")

if __name__ == "__main__":
    main()
