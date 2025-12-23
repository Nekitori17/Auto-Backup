use chrono::Local;
use std::path::Path;

pub fn variable_replacer(fmt: &str, top_folder: &str, src_path: &Path, count: usize) -> String {
    let now = Local::now();
    let filename = src_path
        .file_name()
        .unwrap_or_default()
        .to_string_lossy();
    let name = src_path
        .file_stem()
        .unwrap_or_default()
        .to_string_lossy();

    let mut res = fmt.to_string();
    res = res.replace("$date", &now.format("%Y-%m-%d").to_string());
    res = res.replace("$time", &now.format("%H-%M-%S").to_string());
    res = res.replace("$timestamp", &now.format("%Y%m%d_%H%M%S").to_string());
    res = res.replace("$count", &(count + 1).to_string());
    res = res.replace("$top_folder", top_folder);
    res = res.replace("$filename", &filename);
    res = res.replace("$name", &name);
    
    res
}