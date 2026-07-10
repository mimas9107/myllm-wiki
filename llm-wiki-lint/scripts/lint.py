import os
import re
import yaml
from datetime import datetime

WIKI_DIR = "/opt/myllm-wiki/wiki"
INDEX_FILE = os.path.join(WIKI_DIR, "INDEX.md")
SCHEMA_FILE = os.path.join(WIKI_DIR, "SCHEMA.md")
REPORT_FILE = "/opt/myllm-wiki/sentinel/lint_report.md"

REQUIRED_FIELDS = {"name", "description", "type", "tags", "confidence", "contested", "contradictions", "sources", "created", "updated", "contributors"}
CURRENT_DATE = datetime(2026, 7, 9)

def extract_valid_set_from_schema():
    with open(SCHEMA_FILE, 'r') as f:
        content = f.read()
    
    types = set(re.findall(r'\|\s*`([^`]+)`\s*\|\s*[^|]+\|\s*`[^`]+\.md`\s*\|', content))
    tags = set(re.findall(r'\|\s*`([^`]+)`\s*\|\s*[^|]+\|', content))
    
    return types, tags

def parse_frontmatter(content):
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) >= 3:
        try:
            frontmatter = yaml.safe_load(parts[1])
            return frontmatter, parts[2]
        except:
            return None, content
    return None, content

def get_links(text):
    return re.findall(r'\[\[(.*?)\]\]', text)

def main():
    VALID_TYPES, VALID_TAGS = extract_valid_set_from_schema()
    VALID_CONFIDENCE = {"high", "medium", "low"}
    
    md_files = [f for f in os.listdir(WIKI_DIR) if f.endswith(".md") and f not in {"INDEX.md", "log.md", "SCHEMA.md"}]
    
    with open(INDEX_FILE, "r") as f:
        index_content = f.read()
    index_links = set(get_links(index_content))
    
    orphans = []
    for f in md_files:
        name = f[:-3]
        if name not in index_links:
            orphans.append(name)
            
    broken_links = []
    missing_frontmatter = []
    invalid_tags = []
    stale_pages = []
    low_confidence = []
    large_pages = []
    inbound_counts = {f[:-3]: 0 for f in md_files}
    outbound_counts = {f[:-3]: 0 for f in md_files}
    invalid_types = []
    
    for f in md_files:
        path = os.path.join(WIKI_DIR, f)
        name = f[:-3]
        with open(path, "r") as file:
            lines = file.readlines()
            content = "".join(lines)
            
        frontmatter, body = parse_frontmatter(content)
        
        if frontmatter is None:
            missing_frontmatter.append(f"{name} (No Frontmatter)")
        else:
            missing = REQUIRED_FIELDS - set(frontmatter.keys())
            if missing:
                missing_frontmatter.append(f"{name} (Missing: {', '.join(missing)})")
            
            fm_type = frontmatter.get("type")
            if fm_type not in VALID_TYPES:
                invalid_types.append(f"{name} (type: {fm_type})")
                
            fm_tags = frontmatter.get("tags", [])
            if isinstance(fm_tags, list):
                invalid = [t for t in fm_tags if t not in VALID_TAGS]
                if invalid:
                    invalid_tags.append(f"{name} (Tags: {', '.join(invalid)})")
                    
            if frontmatter.get("confidence") == "low":
                low_confidence.append(name)
            elif frontmatter.get("confidence") not in VALID_CONFIDENCE and len(frontmatter.get("sources", [])) <= 1:
                low_confidence.append(f"{name} (Single source, no valid confidence)")
                
            updated = str(frontmatter.get("updated", ""))
            try:
                up_date = datetime.strptime(updated, "%Y-%m-%d")
                if (CURRENT_DATE - up_date).days > 90:
                    stale_pages.append(name)
            except:
                pass
                
        if len(lines) > 200:
            large_pages.append(name)
            
        links = get_links(body)
        outbound_counts[name] = len([l for l in links if not l.startswith("http")])
        
        for l in links:
            l_clean = l.split("|")[0].split("#")[0].strip()
            if l_clean not in inbound_counts:
                broken_links.append(f"{name} -> {l_clean}")
            else:
                inbound_counts[l_clean] += 1
                
    inbound_low = [name for name, count in inbound_counts.items() if count < 1]
    outbound_low = [name for name, count in outbound_counts.items() if count < 2]
    
    report = f"""# Wiki Lint Report
> Generated: {CURRENT_DATE.strftime('%Y-%m-%d %H:%M')}
> Total pages: {len(md_files)}

## Critical (必須處理)
- **Broken Links（{len(broken_links)} 個）**: {', '.join(broken_links) if broken_links else '無'}
- **Missing/Invalid Frontmatter（{len(missing_frontmatter) + len(invalid_types)} 個）**: 
  - Missing: {', '.join(missing_frontmatter) if missing_frontmatter else '無'}
  - Invalid Type: {', '.join(invalid_types) if invalid_types else '無'}

## Warnings (建議處理)
- **Orphans（{len(orphans)} 個）**: {', '.join(orphans) if orphans else '無'}
- **Invalid Tags（{len(invalid_tags)} 個）**: {', '.join(invalid_tags) if invalid_tags else '無'}
- **Stale Pages（{len(stale_pages)} 個）**: {', '.join(stale_pages) if stale_pages else '無'}
- **Low Confidence（{len(low_confidence)} 個）**: {', '.join(low_confidence) if low_confidence else '無'}
- **Page Size > 200 lines（{len(large_pages)} 個）**: {', '.join(large_pages) if large_pages else '無'}
- **Inbound < 1（{len(inbound_low)} 個）**: {', '.join(inbound_low) if inbound_low else '無'}
- **Outbound < 2（{len(outbound_low)} 個）**: {', '.join(outbound_low) if outbound_low else '無'}

## Info
- 上次 lint 日期: {CURRENT_DATE.strftime('%Y-%m-%d')}
- 建議動作: 定期檢視 Inbound/Outbound 低於閥值的頁面，補齊脈絡。
"""
    with open(REPORT_FILE, "w") as f:
        f.write(report)
        
    print("Linting complete.")

if __name__ == "__main__":
    main()
