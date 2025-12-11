import os
import sys
import time
import json
import shutil
import logging
from threading import Timer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils import variable_replacer

CONFIG_FILE = "backup_config.json"

def get_app_path():
  if getattr(sys, "frozen", False):
    return os.path.dirname(sys.executable)
  return os.path.dirname(os.path.abspath(__file__))

def perform_backup(src_path, source_root, backup_root, fmt):
    try:
        if not os.path.exists(src_path): return

        rel_path = os.path.relpath(src_path, source_root)
        parts = rel_path.split(os.sep)

        if len(parts) > 1:
            top_folder = parts[0]
            middle_path = os.path.join(*parts[1:-1]) if len(parts) > 2 else ""
        else:
            top_folder = "Root" 
            middle_path = ""

        check_count_dir = os.path.join(backup_root, top_folder)
        amount_of_backup_current = 0
        if os.path.exists(check_count_dir):
            try:
                amount_of_backup_current = len([
                    d for d in os.listdir(check_count_dir) 
                    if os.path.isdir(os.path.join(check_count_dir, d))
                ])
            except: pass

        format_folder_name = variable_replacer(fmt, top_folder, src_path, amount_of_backup_current)
        target_folder = os.path.join(backup_root, top_folder, format_folder_name, middle_path)

        os.makedirs(target_folder, exist_ok=True)

        filename = os.path.basename(src_path)
        final_dest = os.path.join(target_folder, filename)

        shutil.copy2(src_path, final_dest)

        log_msg = f"Backup Success: {src_path} -> {final_dest}"
        print(log_msg)
        logging.info(log_msg)

    except Exception as e:
        err = f"ERROR: {e}"
        print(err)
        logging.error(err)

class DebounceHandler(FileSystemEventHandler):
    def __init__(self, source, dest, fmt, delay):
        self.source = source
        self.dest = dest
        self.fmt = fmt
        self.delay = delay
        self.pending_tasks = {}

    def _trigger(self, src_path):
        if os.path.isdir(src_path): return
        
        if src_path in self.pending_tasks:
            self.pending_tasks[src_path].cancel()
        
        t = Timer(self.delay, self._execute, args=[src_path])
        t.start()
        self.pending_tasks[src_path] = t

    def _execute(self, src_path):
        if src_path in self.pending_tasks:
            del self.pending_tasks[src_path]
        perform_backup(src_path, self.source, self.dest, self.fmt)

    def on_modified(self, event): self._trigger(str(event.src_path))
    def on_created(self, event): self._trigger(str(event.src_path))

def run_event_mode(source, dest, fmt, debounce_time):
    print(f"--- MODE: REAL-TIME EVENT (Debounce: {debounce_time}s) ---")
    handler = DebounceHandler(source, dest, fmt, debounce_time)
    observer = Observer()
    observer.schedule(handler, source, recursive=True)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def run_periodic_mode(source, dest, fmt, interval):
    print(f"--- MODE: PERIODIC SCAN (Every {interval}s) ---")
    last_scan_time = time.time() - interval
    last_scan_time = time.time()

    try:
        while True:
            time.sleep(interval)
            current_scan_start = time.time()
            print(f"Scanning for changes...")

            count = 0
            for root, dirs, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > last_scan_time:
                            perform_backup(file_path, source, dest, fmt)
                            count += 1
                    except OSError:
                        pass
            
            if count > 0:
                print(f"Interval Scan: Backed up {count} files.")
            
            last_scan_time = current_scan_start

    except KeyboardInterrupt:
        print("Stopping periodic scan.")

def start_watching():
    app_path = get_app_path()
    config_path = os.path.join(app_path, CONFIG_FILE)

    if not os.path.exists(config_path):
        print("Config not found.")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except: return

    src = config.get("source_dir")
    dst = config.get("backup_dir")
    fmt = config.get("format", "$top_folder-$date_v$count")
    
    # Lấy config chế độ
    mode = config.get("mode", "event")
    time_val = float(config.get("time_value", 5))

    if not src or not dst: return

    if not os.path.exists(dst): os.makedirs(dst)
    logging.basicConfig(filename=os.path.join(dst, "backup_log.txt"), level=logging.INFO, 
                        format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    print(f"Source: {src}")
    print(f"Dest: {dst}")

    if mode == "periodic":
        run_periodic_mode(src, dst, fmt, time_val)
    else:
        run_event_mode(src, dst, fmt, time_val)