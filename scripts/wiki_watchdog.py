import os
import time
import requests
import hashlib
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- 設定區域：三權分立架構 ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MONITOR_DIR = os.path.join(BASE_DIR, "raw")
SENTINEL_DIR = os.path.join(BASE_DIR, "sentinel")
SUMMARY_DIR = os.path.join(SENTINEL_DIR, "summaries")
TASK_LIST = os.path.join(SENTINEL_DIR, "tasks.md")
STATE_FILE = os.path.join(SENTINEL_DIR, "states.json")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"

# 策略與過濾
WHITELIST_EXTS = {'.c', '.cpp', '.py', '.js', '.md', '.pdf', '.odp', '.docx', '.txt'}
IGNORE_FILENAMES = {'CMakeLists.txt', 'requirements.txt', 'package-lock.json', 'yarn.lock', 'LICENSE', '.gitignore'}
IGNORE_DIRS = {'.git', 'node_modules', 'build', 'dist', '__pycache__', '.venv', 'target'}
FLOOD_THRESHOLD = 20
FLOOD_WINDOW = 5
# --- --- --- ---

class WikiHandler(FileSystemEventHandler):
    def __init__(self):
        self.event_count = 0
        self.last_event_time = time.time()
        self.is_flooded = False
        self.states = self._load_states()

    def _load_states(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_state(self, file_path, file_hash):
        self.states[file_path] = {
            "hash": file_hash,
            "last_processed": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.states, f, indent=2, ensure_ascii=False)

    def _get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                buf = f.read(1024 * 1024)
                hasher.update(buf)
            return hasher.hexdigest()
        except: return None

    def on_created(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path, "新增")

    def on_modified(self, event):
        if not event.is_directory:
            if os.path.abspath(event.src_path) == MONITOR_DIR:
                return
            self._handle_event(event.src_path, "修改")

    def _handle_event(self, file_path, action_type):
        current_time = time.time()
        if current_time - self.last_event_time < FLOOD_WINDOW:
            self.event_count += 1
        else:
            self.event_count = 1
            self.is_flooded = False
        self.last_event_time = current_time

        if self.event_count > FLOOD_THRESHOLD:
            if not self.is_flooded:
                print(f"[⚠️ 警報] 觸發防洪熔斷模式。")
                self._log_mass_event(file_path)
                self.is_flooded = True
            return

        self.process_file(file_path, action_type)

    def process_file(self, file_path, action_type):
        abs_path = os.path.abspath(file_path)
        file_name = os.path.basename(abs_path)
        
        # 1. 基礎過濾
        parts = abs_path.split(os.sep)
        if any(d in parts for d in IGNORE_DIRS) or file_name.startswith('.'):
            return
        if file_name in IGNORE_FILENAMES or os.path.splitext(abs_path)[1].lower() not in WHITELIST_EXTS:
            return

        # 2. 雜湊校驗
        current_hash = self._get_file_hash(abs_path)
        if not current_hash: return
        
        if abs_path in self.states and self.states[abs_path]["hash"] == current_hash:
            return

        print(f"[*] 處理{action_type}: {file_name}")
        
        # 3. AI 摘要
        try:
            ext = os.path.splitext(abs_path)[1].lower()
            if ext in ['.pdf', '.docx', '.odp']:
                summary_text = f"偵測到 {ext} 檔案，請手動匯整。"
            else:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4000)
                if not content.strip(): return
                summary_text = self._call_ollama(content, ext)
        except Exception as e:
            print(f"[!] 處理失敗: {e}")
            return

        # 4. 落地摘要與任務，更新狀態
        self._save_summary(abs_path, summary_text)
        self._add_to_task_list(abs_path)
        self._save_state(abs_path, current_hash)

    def _call_ollama(self, content, ext):
        role = "程式碼分析專家" if ext in ['.c', '.cpp', '.py', '.js'] else "知識庫管理員"
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": MODEL, 
                "prompt": f"你是一個{role}。請針對以下{ext}內容進行繁體中文摘要。內容：\n\n{content}",
                "stream": False
            }, timeout=30)
            return response.json().get("response", "無法產生摘要")
        except: return "Ollama 服務暫時無法回應。"

    def _save_summary(self, abs_path, summary):
        file_name = os.path.basename(abs_path)
        summary_path = os.path.join(SUMMARY_DIR, f"{file_name}.summary.md")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"### Source: {abs_path}\n\n{summary}")

    def _add_to_task_list(self, abs_path):
        file_name = os.path.basename(abs_path)
        with open(TASK_LIST, 'a+', encoding='utf-8') as f:
            f.seek(0)
            if file_name not in f.read():
                f.write(f"\n- [ ] **待匯整**: {file_name}\n  - 路徑: `{abs_path}`\n")

    def _log_mass_event(self, file_path):
        dir_name = os.path.dirname(file_path)
        with open(TASK_LIST, 'a', encoding='utf-8') as f:
            f.write(f"\n- [ ] **⚠️ 大量檔案匯入**: `{dir_name}`\n")

if __name__ == "__main__":
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    if not os.path.exists(TASK_LIST):
        with open(TASK_LIST, 'w', encoding='utf-8') as f:
            f.write("# 待處理 Wiki 任務清單\n")
            
    observer = Observer()
    observer.schedule(WikiHandler(), MONITOR_DIR, recursive=True)
    observer.start()
    print(f"🚀 Wiki Watchdog (v6) 啟動成功！")
    print(f"管理目錄: {SENTINEL_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
