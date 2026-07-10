#!/usr/bin/env python3
"""Extract text from the given report files -- multi-backend, zero new deps.

Usage:
    python extract_text.py <file>
    python extract_text.py <directory>   (extracts all supported files recursively)

Backends tried in order: pdftotext, pandoc, libreoffice, python stdlib.
Exits 0 on any success, 1 if no text could be extracted.
"""

import subprocess, sys, os, shutil, tempfile, zipfile
from pathlib import Path

def try_pdftotext(path):
    """使用 pdftotext 系統工具萃取 PDF 文字層，限制前 10 頁。"""
    p = subprocess.run(["pdftotext", str(path), "-", "-l", "10"], capture_output=True, text=True, timeout=30)
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None

def try_pandoc(path):
    """使用 pandoc 系統工具轉換文件 (docx/pptx) 為純文字。"""
    p = subprocess.run(["pandoc", str(path), "-t", "plain"], capture_output=True, text=True, timeout=30)
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None

def try_libreoffice(path):
    """使用 libreoffice 命令行轉換文件 (ppt/xls/doc) 為純文字。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = subprocess.run(["libreoffice", "--headless", "--convert-to", "txt:Text", str(path), "--outdir", tmp],
                           capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            return None
        outfile = Path(tmp) / (Path(path).stem + ".txt")
        if outfile.exists():
            text = outfile.read_text(encoding="utf-8", errors="replace").strip()
            return text if text else None
    return None

def try_python_extract(path):
    """以 Python 標準函式庫 (zipfile + re) 直接解析 docx/pptx 內部 XML。

    docx 與 pptx 本質為 ZIP 壓縮檔，此函式繞過外部工具直接提取文字節點。
    僅作為前三個後端均失敗時的最後手段。
    """
    ext = Path(path).suffix.lower()
    if ext not in (".docx", ".pptx"):
        return None
    try:
        with zipfile.ZipFile(path) as z:
            texts = []
            for name in z.namelist():
                if name.startswith("word/") and name.endswith(".xml"):
                    texts.append(z.read(name).decode("utf-8", errors="replace"))
                elif name.startswith("ppt/slides/") and name.endswith(".xml"):
                    texts.append(z.read(name).decode("utf-8", errors="replace"))
        raw = " ".join(texts)
        import re
        cleaned = re.sub(r"<[^>]+>", " ", raw)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned if len(cleaned) > 50 else None
    except Exception:
        return None

BACKENDS = [
    ("pdftotext", try_pdftotext, ".pdf"),
    ("pandoc", try_pandoc, ".docx"),
    ("pandoc", try_pandoc, ".pptx"),
    ("libreoffice", try_libreoffice, ".ppt"),
    ("libreoffice", try_libreoffice, ".xls"),
    ("libreoffice", try_libreoffice, ".xlsx"),
    ("libreoffice", try_libreoffice, ".doc"),
    ("python stdlib", try_python_extract, ".docx"),
    ("python stdlib", try_python_extract, ".pptx"),
]

SUPPORTED_EXT = {ext for _, _, ext in BACKENDS}

def extract_one(path):
    """依 BACKENDS 順序輪詢各後端，回傳第一組成功萃取的純文字。"""
    for name, func, ext in BACKENDS:
        if ext and path.suffix.lower() != ext:
            continue
        if not shutil.which(name.split()[0]) and name != "python stdlib":
            continue
        try:
            result = func(path)
            if result:
                return result
        except Exception:
            continue
    return None

def main():
    """解析命令列參數，對檔案或目錄進行遞迴萃取。"""
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    files = []
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = sorted(target.rglob("*"))
        files = [f for f in files if f.suffix.lower() in SUPPORTED_EXT and f.is_file()]

    total = 0
    for f in files:
        text = extract_one(f)
        if text:
            print(f"=== {f.relative_to(target.parent if target.is_file() else target)} ===")
            print(text)
            print()
            total += 1
        else:
            print(f"--- {f.name}: no extractable text ---", file=sys.stderr)

    sys.exit(0 if total > 0 else 1)

if __name__ == "__main__":
    main()
