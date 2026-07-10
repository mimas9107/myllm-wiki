#!/bin/bash
# pptx2text.sh - Batch convert PPTX files to text using LibreOffice headless
# Usage: ./pptx2text.sh <input_dir> <output_dir>

set -e

INPUT_DIR="${1:-/opt/myllm-wiki/raw}"
OUTPUT_DIR="${2:-/tmp/pptx_text}"
TEMP_HTML_DIR="/tmp/pptx_html"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$TEMP_HTML_DIR"

# Find all PPTX files
PPTX_FILES=$(find "$INPUT_DIR" -name "*.pptx" -type f 2>/dev/null)
TOTAL=$(echo "$PPTX_FILES" | wc -l)

echo "=== PPTX 批次文字萃取 ==="
echo "輸入目錄: $INPUT_DIR"
echo "發現 $TOTAL 個 PPTX 檔案"
echo "輸出目錄: $OUTPUT_DIR"
echo ""

COUNT=0
SKIP=0
ERROR=0

# Text extractor using Python
python3 << 'PYEOF'
import sys, html
from html.parser import HTMLParser
import re

class PPTXTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_lines = []
        self.skip_depth = 0
        self.current_text = ""
        self.ignore_tags = {'script', 'style', 'defs'}
        self.prev_tag = None

    def handle_starttag(self, tag, attrs):
        if tag in self.ignore_tags:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.ignore_tags and self.skip_depth > 0:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth == 0:
            # Clean whitespace-heavy content
            cleaned = re.sub(r'\s+', ' ', data).strip()
            if cleaned and len(cleaned) > 1:
                self.text_lines.append(cleaned)

def extract_from_html(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        parser = PPTXTextExtractor()
        parser.feed(content)
        return '\n'.join(parser.text_lines)
    except Exception as e:
        return f"[ERROR reading {filepath}: {e}]"

if __name__ == '__main__':
    # Read file list from stdin
    files = sys.stdin.read().splitlines()
    for f in files:
        if not f:
            continue
        # Output path: .pptx -> .txt
        txt_name = f.replace('.pptx', '.txt').replace('/pptx_html/', '/pptx_text/')
        html_file = f.replace('.pptx', '.html').replace(INPUT_DIR, TEMP_HTML_DIR)
        if INPUT_DIR is None:
            INPUT_DIR = '/opt/myllm-wiki/raw'
        try:
            text = extract_from_html(html_file)
            with open(txt_name, 'w', encoding='utf-8') as out:
                out.write(text)
            print(f"OK: {txt_name}")
        except FileNotFoundError:
            print(f"SKIP (no HTML): {html_file}")
        except Exception as e:
            print(f"ERROR: {f} -> {e}")
PYEOF