import os
import json
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox
import worker

class ConfigApp:
  def __init__(self, root: tk.Tk):
    self.root = root
    self.root.title("Auto Backup Setting")
    self.root.geometry("600x450") 

    self.app_path = worker.get_app_path()
    self.config_path = os.path.join(self.app_path, worker.CONFIG_FILE)
    
    self.current_config = {}
    self.load_current_config()

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    # Source
    tk.Label(main_frame, text="Source Directory:", font=("Arial", 10, "bold")).pack(anchor="w")
    frame_src = tk.Frame(main_frame)
    frame_src.pack(fill="x", pady=5)
    self.entry_source = tk.Entry(frame_src)
    self.entry_source.pack(side="left", fill="x", expand=True)
    self.entry_source.insert(0, self.current_config.get("source_dir", ""))
    tk.Button(frame_src, text="Browse", command=self.browse_source).pack(side="right", padx=5)

    # Dest
    tk.Label(main_frame, text="Backup Destination:", font=("Arial", 10, "bold")).pack(anchor="w")
    frame_dest = tk.Frame(main_frame)
    frame_dest.pack(fill="x", pady=5)
    self.entry_dest = tk.Entry(frame_dest)
    self.entry_dest.pack(side="left", fill="x", expand=True)
    self.entry_dest.insert(0, self.current_config.get("backup_dir", ""))
    tk.Button(frame_dest, text="Browse", command=self.browse_dest).pack(side="right", padx=5)

    # --- MODE SELECTION ---
    tk.Label(main_frame, text="Backup Mode:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))
    
    self.mode_var = tk.StringVar(value=self.current_config.get("mode", "event"))
    
    # Frame cho Radio buttons
    frame_mode = tk.Frame(main_frame)
    frame_mode.pack(fill="x")
    
    rb1 = tk.Radiobutton(frame_mode, text="Event-Based (Real-time)", variable=self.mode_var, value="event", command=self.update_labels)
    rb1.pack(side="left", padx=10)
    
    rb2 = tk.Radiobutton(frame_mode, text="Periodic (Interval Scan)", variable=self.mode_var, value="periodic", command=self.update_labels)
    rb2.pack(side="left", padx=10)

    # Time Value Input (Dùng chung cho cả 2 mode)
    self.lbl_time = tk.Label(main_frame, text="Wait Time (Debounce) in Seconds:", font=("Arial", 10, "bold"))
    self.lbl_time.pack(anchor="w", pady=(10, 0))
    
    self.lbl_desc = tk.Label(main_frame, text="Wait X seconds after last edit to save.", font=("Arial", 8), fg="gray")
    self.lbl_desc.pack(anchor="w")

    self.entry_time = tk.Entry(main_frame)
    self.entry_time.pack(fill="x", pady=(5, 10))
    self.entry_time.insert(0, str(self.current_config.get("time_value", 5)))

    # Format
    tk.Label(main_frame, text="Folder Name Format:", font=("Arial", 10, "bold")).pack(anchor="w")
    self.entry_fmt = tk.Entry(main_frame)
    self.entry_fmt.pack(fill="x", pady=5)
    self.entry_fmt.insert(0, self.current_config.get("format", "$top_folder-$date_v$count"))

    tk.Label(main_frame, text="Vars: $name, $date, $time, $count, $top_folder", fg="gray", font=("Consolas", 9)).pack(anchor="w")

    # Buttons
    frame_btns = tk.Frame(main_frame)
    frame_btns.pack(fill="x", pady=20)
    tk.Button(frame_btns, text="RESET", command=self.reset_fields, bg="#FF4444", fg="white", font=("Arial", 10, "bold")).pack(side="left", expand=True, fill="x", padx=5)
    tk.Button(frame_btns, text="SAVE", command=self.save_config, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", expand=True, fill="x", padx=5)

    self.update_labels() # Update UI lần đầu

  def update_labels(self):
      """Đổi text hướng dẫn tùy theo mode đang chọn"""
      mode = self.mode_var.get()
      if mode == "event":
          self.lbl_time.config(text="Debounce Delay (Seconds):")
          self.lbl_desc.config(text="Backup file X seconds AFTER user stops typing (Prevents spam).")
      else:
          self.lbl_time.config(text="Scan Interval (Seconds):")
          self.lbl_desc.config(text="Scan folder every X seconds. If file changed, backup it.")

  def load_current_config(self):
    if os.path.exists(self.config_path):
      try:
        with open(self.config_path, "r", encoding="utf-8") as f:
          self.current_config = json.load(f)
      except: pass

  def browse_source(self):
    f = filedialog.askdirectory()
    if f:
      self.entry_source.delete(0, tk.END)
      self.entry_source.insert(0, f.replace("/", os.sep))

  def browse_dest(self):
    f = filedialog.askdirectory()
    if f:
      self.entry_dest.delete(0, tk.END)
      self.entry_dest.insert(0, f.replace("/", os.sep))

  def save_config(self):
    src = self.entry_source.get().strip()
    dst = self.entry_dest.get().strip()
    fmt = self.entry_fmt.get().strip()
    time_str = self.entry_time.get().strip()
    mode = self.mode_var.get()

    if not src or not dst or not time_str:
      messagebox.showerror("Error", "Missing fields.")
      return
    
    try:
        val = float(time_str)
        if val < 0: raise ValueError
    except:
        messagebox.showerror("Error", "Time value must be a positive number.")
        return
    
    if any(c in fmt for c in r'<>:"/\|?*'):
      messagebox.showwarning("Warning", "Format contains forbidden characters.")
      return

    data = {
        "source_dir": src, "backup_dir": dst, "format": fmt,
        "mode": mode, "time_value": val
    }

    try:
      with open(self.config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
      messagebox.showinfo("Success", "Configuration saved!")
    except Exception as e:
      messagebox.showerror("Error", str(e))
  
  def reset_fields(self):
    self.mode_var.set("event")
    self.entry_time.delete(0, tk.END); self.entry_time.insert(0, "5")
    self.entry_fmt.delete(0, tk.END); self.entry_fmt.insert(0, "$top_folder-$date_v$count")
    self.update_labels()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--worker", action="store_true")
  args = parser.parse_args()

  if args.worker:
    worker.start_watching()
  else:
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()