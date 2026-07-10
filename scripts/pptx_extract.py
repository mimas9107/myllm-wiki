#!/usr/bin/env python3
"""
pptx_extract.py - Batch PPTX text extraction using LibreOffice headless + HTML parsing
Usage: python3 pptx_extract.py [--input DIR] [--output DIR] [--html DIR]
"""
import subprocess, sys, os, re
from html.parser import HTMLParser
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

HTML_DIR = Path("/tmp/pptx_html")
TEXT_DIR = Path("/tmp/pptx_text")
INPUT_DIR = Path("/opt/myllm-wiki/raw")

class PPTXTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'defs', 'svg', 'g'}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'defs', 'svg', 'g'} and self.skip > 0:
            self.skip -= 1

    def handle_data(self, data):
        if self.skip == 0:
            t = re.sub(r'\s+', ' ', data).strip()
            if t:
                self.lines.append(t)

def extract_text(html_path):
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        parser = PPTXTextExtractor()
        parser.feed(content)
        return '\n'.join(parser.lines)
    except Exception as e:
        return f"[EXTRACTION ERROR: {e}]"

def convert_pptx(pptx_path, html_base, text_base, input_base):
    html_dir = Path(str(pptx_path).replace('.pptx', '.html').replace(str(input_base), str(html_base))).parent
    html_dir.mkdir(parents=True, exist_ok=True)
    html_out = str(pptx_path).replace('.pptx', '.html').replace(str(input_base), str(html_base))
    try:
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'html',
             '--outdir', str(html_dir), str(pptx_path)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return f"[CONVERT ERROR: {result.stderr[:200]}]"
        return extract_text(html_out)
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {e}]"

def main():
    parser = argparse.ArgumentParser(description='Batch PPTX text extraction')
    parser.add_argument('--input', '-i', default=INPUT_DIR, type=Path)
    parser.add_argument('--html-dir', default=HTML_DIR, type=Path)
    parser.add_argument('--output', '-o', default=TEXT_DIR, type=Path)
    parser.add_argument('--workers', '-w', type=int, default=4)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    args.html_dir.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)

    pptx_files = list(args.input.rglob("*.pptx"))
    total = len(pptx_files)
    print(f"=== PPTX 批次文字萃取 ===")
    print(f"發現 {total} 個 PPTX 檔案")
    print(f"HTML 快取: {args.html_dir}")
    print(f"文字輸出: {args.output}")
    print(f"並行緒數: {args.workers}")
    print()

    if args.dry_run:
        for f in pptx_files:
            print(f"  {f.relative_to(args.input)}")
        print(f"\n共 {total} 個檔案 (dry-run)")
        return

    # Pre-convert all PPTX to HTML using parallel libreoffice calls
    print("Phase 1: LibreOffice 轉換...")
    for i, pptx in enumerate(pptx_files):
        html_out = str(pptx).replace('.pptx', '.html').replace(str(args.input), str(args.html_dir))
        if Path(html_out).exists():
            print(f"  [{i+1}/{total}] SKIP (HTML 已存在): {pptx.name}")
            continue
        html_dir = str(Path(html_out).parent)
        Path(html_dir).mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'html',
             '--outdir', html_dir, str(pptx)],
            capture_output=True, text=True, timeout=120
        )
        status = "OK" if result.returncode == 0 else f"FAIL({result.returncode})"
        print(f"  [{i+1}/{total}] {status}: {pptx.name}")

    print("\nPhase 2: HTML 文字萃取...")
    for i, pptx in enumerate(pptx_files):
        html_path = str(pptx).replace('.pptx', '.html').replace(str(args.input), str(args.html_dir))
        txt_path = str(pptx).replace('.pptx', '.txt').replace(str(args.input), str(args.output))
        Path(txt_path).parent.mkdir(parents=True, exist_ok=True)

        text = extract_text(html_path)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        lines = len(text.splitlines())
        print(f"  [{i+1}/{total}] {lines:4d} lines: {Path(txt_path).name}")

    print(f"\n完成！共處理 {total} 個檔案")
    print(f"文字檔位置: {args.output}")

if __name__ == '__main__':
    main()