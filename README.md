# 📂 Auto Backup Tool

A lightweight, high-performance automatic backup tool written in **Rust**.  
Supports both **real-time (event-based)** backups and **periodic scanning**.

## ✨ Features

- **⚡ High Performance**  
  Written in Rust, extremely low RAM and CPU usage.

- **🎮 User-Friendly GUI**  
  Easy configuration via a simple graphical interface.

- **🔄 Two Working Modes**
  - **Event-Based (Real-time):**  
    Instantly backs up files when changes are detected (with debounce to avoid spam).
  - **Periodic:**  
    Scans directories at fixed intervals (seconds/minutes) to detect changes.

- **📝 Flexible Naming Format**  
  Customize backup folder names using variables like `$date`, `$time`, `$count`, etc.

- **🚀 Background Execution**  
  Worker mode runs silently without a window and logs activity to a file.

## 📥 Installation

1. Go to the **Releases** section on the right side of the GitHub page.
2. Download the latest `AutoBackup.exe`.
3. Place the file in any directory you want to store it in.

## 📖 Usage Guide

### 1. Configuration (GUI)

Run `AutoBackup.exe` directly to open the settings window.

- **Source Directory**  
  The folder you want to monitor.

- **Backup Destination**  
  The folder where backups will be stored.

- **Mode**
  - **Real-time:**  
    Best for working folders, source code, or documents.
  - **Periodic:**  
    Suitable for large folders with fewer changes.

- **Time Value**  
  Delay time (seconds) before backup or interval between scans.

- **Format**  
  Example: `$top_folder-$date_v$count`

Click **SAVE CONFIG** to save your settings.

### 2. Run Backup (Worker Mode)

#### Method 1: Using Command Prompt (CMD)

```cmd
AutoBackup.exe --worker
```

#### Method 2: Using a Shortcut (Recommended)

1. Right-click `AutoBackup.exe` → **Create shortcut**
2. Right-click the shortcut → **Properties**
3. In the **Target** field, append ` --worker`  
   Example: `D:\Tool\AutoBackup.exe --worker`
4. Use this shortcut to run silently.

### 3. View Logs

A file named `backup_log.txt` will be created in the **Backup Destination** directory.

## 🛠️ Build from Source

### Requirements

- Rust
- Git

### Build Steps

```bash
git clone https://github.com/username/Auto-Backup-Rust.git
cd Auto-Backup-Rust
cargo build --release
```

Output file:

```
target/release/AutoBackup.exe
```

## 📝 Format Variables

- `$name` — Original file name  
- `$date` — Current date (YYYY-MM-DD)  
- `$time` — Current time (HH-MM-SS)  
- `$timestamp` — Full timestamp  
- `$count` — Backup index  
- `$top_folder` — Top-level source folder name  

---

Developed with ❤️ in Rust.

## 🚀 Release Guide

```bash
git tag v1.0.0
git push origin v1.0.0
```
