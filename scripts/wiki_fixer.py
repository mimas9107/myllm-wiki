import os
import re
import yaml

WIKI_DIR = "/opt/myllm-wiki/wiki"

def get_links(text):
    return re.findall(r'\[\[(.*?)\]\]', text)

def fix_frontmatter(path, filename):
    with open(path, "r") as file:
        content = file.read()
        
    if not content.startswith("---"):
        return content
        
    parts = content.split("---", 2)
    if len(parts) >= 3:
        try:
            fm = yaml.safe_load(parts[1])
            modified = False
            
            if "contested" not in fm:
                fm["contested"] = False
                modified = True
            if "contradictions" not in fm:
                fm["contradictions"] = []
                modified = True
            if "sources" not in fm:
                fm["sources"] = []
                modified = True
                
            if modified:
                new_fm_str = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
                new_content = "---\n" + new_fm_str + "---\n" + parts[2].lstrip()
                return new_content
        except Exception as e:
            print(f"Error parsing frontmatter in {filename}: {e}")
            
    return content

def fix_links_in_content(content, valid_targets):
    links = get_links(content)
    new_content = content
    
    for l in links:
        l_clean = l.split("|")[0].split("#")[0].strip()
        if l_clean not in valid_targets and not l_clean.startswith("http"):
            # Strip brackets to fix broken links (since we don't know the exact target automatically)
            new_content = new_content.replace(f"[[{l}]]", l)
            
    return new_content

def main():
    md_files = [f for f in os.listdir(WIKI_DIR) if f.endswith(".md") and f not in {"INDEX.md", "log.md", "SCHEMA.md"}]
    valid_targets = {f[:-3] for f in md_files}
    
    total_files_modified = 0
    
    for f in md_files:
        path = os.path.join(WIKI_DIR, f)
        
        # 1. Fix Frontmatter
        content_after_fm = fix_frontmatter(path, f)
        
        # 2. Fix Links
        final_content = fix_links_in_content(content_after_fm, valid_targets)
        
        with open(path, "r") as file:
            original_content = file.read()
            
        if final_content != original_content:
            with open(path, "w") as file:
                file.write(final_content)
                total_files_modified += 1
                print(f"Fixed issues in {f}")
                
    print(f"Total files modified: {total_files_modified}")

if __name__ == "__main__":
    main()
