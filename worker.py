import os
import sys
import time
import json
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils import variable_replacer

CONFIG_FILE = "backup_config.json"

def get_app_path():
  if getattr(sys, "frozen", False):
    return os.path.dirname(sys.executable)
  return os.path.dirname(os.path.abspath(__file__))

class BackupHandler(FileSystemEventHandler):
  def __init__(self, source_dir: str, backup_dir: str, format: str):
    self.source_dir = os.path.normpath(source_dir)
    self.backup_dir = os.path.normpath(backup_dir)
    self.format = format
    
    if not os.path.exists(self.backup_dir):
      os.makedirs(self.backup_dir)

    log_file = os.path.join(self.backup_dir, "backup_log.txt")
    logging.basicConfig(filename=log_file, 
                        level=logging.INFO, 
                        format="%(asctime)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

  def _process_backup(self, src_path: str):
    try:
      if os.path.isdir(src_path):
        return

      time.sleep(1)

      # 1. Calculate relative path elements
      rel_path = os.path.relpath(src_path, self.source_dir)
      parts = rel_path.split(os.sep)

      # 2. Extract Top Folder and Middle Path
      if len(parts) > 1:
        top_folder = parts[0]
        # Join everything between TopFolder and Filename
        middle_path = os.path.join(*parts[1:-1]) if len(parts) > 2 else ""
      else:
        top_folder = "Root" 
        middle_path = ""

      # 3. Calculate Count (based on existing folders in Backup/TopFolder)
      check_count_dir = os.path.join(self.backup_dir, top_folder)
      amount_of_backup_current = 0
      
      if os.path.exists(check_count_dir):
        try:
          amount_of_backup_current = len([
            d for d in os.listdir(check_count_dir) 
            if os.path.isdir(os.path.join(check_count_dir, d))
          ])
        except Exception:
          pass

      # 4. Generate Format Folder Name
      format_folder_name = variable_replacer(self.format, top_folder, src_path, amount_of_backup_current)

      # 5. Construct Final Path: Backup / TopFolder / {Format} / MiddlePath
      target_folder = os.path.join(self.backup_dir, top_folder, format_folder_name, middle_path)

      os.makedirs(target_folder, exist_ok=True)

      filename = os.path.basename(src_path)
      final_dest = os.path.join(target_folder, filename)

      shutil.copy2(src_path, final_dest)

      log_msg = f"Backup Success: {src_path} -> {final_dest}"
      print(log_msg)
      logging.info(log_msg)

    except Exception as e:
      err_msg = f"ERROR backup {src_path}: {str(e)}"
      print(err_msg)
      logging.error(err_msg)

  def on_modified(self, event):
    self._process_backup(str(event.src_path))

  def on_created(self, event):
    self._process_backup(str(event.src_path))

def start_watching():
  app_path = get_app_path()
  config_path = os.path.join(app_path, CONFIG_FILE)

  if not os.path.exists(config_path):
    print("Error: Config file not found.")
    return

  try:
    with open(config_path, "r", encoding="utf-8") as f:
      config = json.load(f)
  except Exception as e:
    print(f"Error reading config: {e}")
    return

  source = config.get("source_dir")
  destination = config.get("backup_dir")
  fmt = config.get("format", "$name-date_v$count")

  if not source or not destination:
    print("Invalid configuration.")
    return

  print("=== WORKER STARTED ===")
  print(f"Source: {source}")
  print(f"Dest: {destination}")
  print(f"Format: {fmt}")
  
  event_handler = BackupHandler(source, destination, fmt)
  observer = Observer()
  observer.schedule(event_handler, source, recursive=True)
  observer.start()

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()