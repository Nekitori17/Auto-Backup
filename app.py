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
    self.root.geometry("600x380") # Increased height slightly

    self.app_path = worker.get_app_path()
    self.config_path = os.path.join(self.app_path, worker.CONFIG_FILE)
    
    self.current_config = {}
    self.load_current_config()

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    # Source Input
    tk.Label(main_frame, text="Source Directory:", font=("Arial", 10, "bold")).pack(anchor="w")
    frame_src = tk.Frame(main_frame)
    frame_src.pack(fill="x", pady=(5, 10))
    self.entry_source = tk.Entry(frame_src)
    self.entry_source.pack(side="left", fill="x", expand=True)
    self.entry_source.insert(0, self.current_config.get("source_dir", ""))
    tk.Button(frame_src, text="Browse", command=self.browse_source).pack(side="right", padx=5)

    # Dest Input
    tk.Label(main_frame, text="Backup Destination:", font=("Arial", 10, "bold")).pack(anchor="w")
    frame_dest = tk.Frame(main_frame)
    frame_dest.pack(fill="x", pady=(5, 10))
    self.entry_dest = tk.Entry(frame_dest)
    self.entry_dest.pack(side="left", fill="x", expand=True)
    self.entry_dest.insert(0, self.current_config.get("backup_dir", ""))
    tk.Button(frame_dest, text="Browse", command=self.browse_dest).pack(side="right", padx=5)

    # Format Input
    tk.Label(main_frame, text="Folder Name Format (Time):", font=("Arial", 10, "bold")).pack(anchor="w")
    self.entry_fmt = tk.Entry(main_frame)
    self.entry_fmt.pack(fill="x", pady=(5, 15))
    default_fmt = self.current_config.get("format", "$name-date_v$count")
    self.entry_fmt.insert(0, default_fmt)

    # Variable Instruction Label
    # Fixed typo: Changed %name to $name
    tk.Label(main_frame, 
             text="Variables: $name, $filename, $time, $date, $timestamp, $count, $top_folder", 
             fg="gray", font=("Consolas", 9)).pack(anchor="w")

    # --- Action Buttons Frame ---
    frame_action_buttons = tk.Frame(main_frame)
    frame_action_buttons.pack(fill="x", pady=20)

    # Reset Button (Left side, takes 50%)
    btn_reset = tk.Button(frame_action_buttons, text="RESET", command=self.reset_fields, 
                          bg="#FF4444", fg="white", font=("Arial", 11, "bold"), height=2)
    btn_reset.pack(side="left", expand=True, fill="x", padx=(0, 5))

    # Save Button (Right side, takes 50%)
    btn_save = tk.Button(frame_action_buttons, text="SAVE", command=self.save_config, 
                         bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2)
    btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    # Instruction Label
    tk.Label(main_frame, text="Note: After saving, run app with '--worker' argument to start.", fg="gray").pack()

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

    if not src or not dst:
      messagebox.showerror("Error", "Please enter all required fields.")
      return
    
    if any(c in fmt for c in r'<>:"/\|?*'):
      messagebox.showwarning("Warning", "Format contains forbidden characters (e.g. :).")
      return

    data = {"source_dir": src, "backup_dir": dst, "format": fmt}
    try:
      with open(self.config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
      messagebox.showinfo("Success", "Configuration saved successfully!")
    except Exception as e:
      messagebox.showerror("Error", str(e))
  
  def reset_fields(self):
    self.entry_source.delete(0, tk.END)
    self.entry_dest.delete(0, tk.END)
    self.entry_fmt.delete(0, tk.END)
    self.entry_fmt.insert(0, "$name-date_v$count")

    # Optional: Clear config file immediately or just clear UI
    data = {"source_dir": "", "backup_dir": "", "format": "$name-date_v$count"}
    try:
      with open(self.config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
      messagebox.showinfo("Success", "Configuration Reset Successfully!")
    except Exception as e:
      messagebox.showerror("Error", str(e))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--worker", action="store_true", help="Run backup background worker")
  args = parser.parse_args()

  if args.worker:
    # Run worker mode
    worker.start_watching()
  else:
    # Run GUI mode
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()