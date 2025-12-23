use crate::config::{get_app_path, load_config, CONFIG_FILE};
use crate::utils::variable_replacer;
use chrono::Local;
use notify::{Config, RecommendedWatcher, RecursiveMode, Watcher};
use std::collections::HashMap;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::mpsc::channel;
use std::thread;
use std::time::{Duration, Instant, SystemTime};
use walkdir::WalkDir;

pub fn start_watching() {
    let app_path = get_app_path();
    let config_path = app_path.join(CONFIG_FILE);

    if !config_path.exists() {
        return;
    }

    let config = load_config();
    if config.source_dir.is_empty() || config.backup_dir.is_empty() {
        return;
    }

    let _ = fs::create_dir_all(&config.backup_dir);
    
    log_to_file(&config.backup_dir, "Worker started watching...");

    if config.mode == "periodic" {
        run_periodic_mode(config.source_dir, config.backup_dir, config.format, config.time_value);
    } else {
        run_event_mode(config.source_dir, config.backup_dir, config.format, config.time_value);
    }
}

fn log_to_file(backup_root: &str, message: &str) {
    let log_path = Path::new(backup_root).join("backup_log.txt");
    
    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(log_path) {
        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S");
        let _ = writeln!(file, "{} - {}", timestamp, message);
    }
}

fn perform_backup(src_path: &Path, source_root: &str, backup_root: &str, fmt: &str) {
    if !src_path.exists() { return; }

    let src_root_path = Path::new(source_root);
    let rel_path = match src_path.strip_prefix(src_root_path) {
        Ok(p) => p,
        Err(_) => return,
    };

    let components: Vec<_> = rel_path.components().map(|c| c.as_os_str().to_string_lossy().into_owned()).collect();
    
    let (top_folder, middle_path) = if components.len() > 1 {
        let top = components[0].clone();
        let mid = components[1..components.len()-1].join(&std::path::MAIN_SEPARATOR.to_string());
        (top, mid)
    } else {
        ("Root".to_string(), "".to_string())
    };

    let check_count_dir = Path::new(backup_root).join(&top_folder);
    let mut amount = 0;
    if check_count_dir.exists() {
        if let Ok(entries) = fs::read_dir(&check_count_dir) {
            amount = entries.filter(|e| e.as_ref().map(|x| x.path().is_dir()).unwrap_or(false)).count();
        }
    }

    let format_folder_name = variable_replacer(fmt, &top_folder, src_path, amount);
    let target_folder = Path::new(backup_root)
        .join(&top_folder)
        .join(format_folder_name)
        .join(middle_path);

    if let Err(e) = fs::create_dir_all(&target_folder) {
        log_to_file(backup_root, &format!("ERROR creating dir: {}", e));
        return;
    }

    let filename = src_path.file_name().unwrap();
    let final_dest = target_folder.join(filename);

    match fs::copy(src_path, &final_dest) {
        Ok(_) => {
            let msg = format!("Backup Success: {:?} -> {:?}", src_path, final_dest);
            log_to_file(backup_root, &msg);
        },
        Err(e) => {
            log_to_file(backup_root, &format!("ERROR copy: {}", e));
        },
    }
}

fn run_periodic_mode(source: String, dest: String, fmt: String, interval: f64) {
    log_to_file(&dest, &format!("--- MODE: PERIODIC SCAN (Every {}s) ---", interval));
    let duration = Duration::from_secs_f64(interval);
    let mut last_scan_time = SystemTime::now();

    loop {
        thread::sleep(duration);
        let current_scan_start = SystemTime::now();

        let mut count = 0;
        for entry in WalkDir::new(&source).into_iter().filter_map(|e| e.ok()) {
            let path = entry.path();
            if path.is_file() {
                if let Ok(metadata) = fs::metadata(path) {
                    if let Ok(mtime) = metadata.modified() {
                        if mtime > last_scan_time {
                            perform_backup(path, &source, &dest, &fmt);
                            count += 1;
                        }
                    }
                }
            }
        }

        if count > 0 {
            log_to_file(&dest, &format!("Interval Scan: Backed up {} files.", count));
        }
        last_scan_time = current_scan_start;
    }
}

fn run_event_mode(source: String, dest: String, fmt: String, debounce_time: f64) {
    log_to_file(&dest, &format!("--- MODE: REAL-TIME EVENT (Debounce: {}s) ---", debounce_time));
    
    let (tx, rx) = channel();
    
    let mut watcher = RecommendedWatcher::new(move |res| {
        let _ = tx.send(res);
    }, Config::default()).unwrap();

    if let Err(e) = watcher.watch(Path::new(&source), RecursiveMode::Recursive) {
        log_to_file(&dest, &format!("Error starting watcher: {}", e));
        return;
    }

    let mut pending_files: HashMap<PathBuf, Instant> = HashMap::new();
    let debounce_duration = Duration::from_secs_f64(debounce_time);

    loop {
        while let Ok(res) = rx.try_recv() {
            match res {
                Ok(event) => {
                    for path in event.paths {
                        if path.is_dir() { continue; }
                        pending_files.insert(path, Instant::now() + debounce_duration);
                    }
                },
                Err(e) => log_to_file(&dest, &format!("Watch error: {:?}", e)),
            }
        }

        let now = Instant::now();
        let mut to_process = Vec::new();

        let keys: Vec<PathBuf> = pending_files.keys().cloned().collect();
        for k in keys {
            if let Some(target_time) = pending_files.get(&k) {
                if now >= *target_time {
                    to_process.push(k.clone());
                }
            }
        }

        for path in to_process {
            pending_files.remove(&path);
            perform_backup(&path, &source, &dest, &fmt);
        }

        thread::sleep(Duration::from_millis(100));
    }
}