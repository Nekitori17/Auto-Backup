use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

pub const CONFIG_FILE: &str = "backup_config.json";

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AppConfig {
    pub source_dir: String,
    pub backup_dir: String,
    pub format: String,
    pub mode: String,
    pub time_value: f64,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            source_dir: String::new(),
            backup_dir: String::new(),
            format: String::from("$top_folder-$time-$date"),
            mode: String::from("event"),
            time_value: 5.0,
        }
    }
}

pub fn get_app_path() -> PathBuf {
    std::env::current_exe()
        .map(|p| p.parent().unwrap_or(Path::new(".")).to_path_buf())
        .unwrap_or_else(|_| PathBuf::from("."))
}

pub fn load_config() -> AppConfig {
    let config_path = get_app_path().join(CONFIG_FILE);
    if config_path.exists() {
        if let Ok(content) = fs::read_to_string(config_path) {
            if let Ok(cfg) = serde_json::from_str(&content) {
                return cfg;
            }
        }
    }
    AppConfig::default()
}

pub fn save_config(config: &AppConfig) -> Result<(), String> {
    let config_path = get_app_path().join(CONFIG_FILE);
    let json = serde_json::to_string_pretty(config).map_err(|e| e.to_string())?;
    fs::write(config_path, json).map_err(|e| e.to_string())?;
    Ok(())
}