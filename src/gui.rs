use eframe::{egui, App, Frame};
use crate::config::{AppConfig, save_config};

pub struct ConfigApp {
    config: AppConfig,
    status_msg: String,
}

impl ConfigApp {
    pub fn new(_cc: &eframe::CreationContext) -> Self {
        let mut app = Self {
            config: AppConfig::default(),
            status_msg: String::new(),
        };
        app.config = crate::config::load_config();
        app
    }

    fn reset_fields(&mut self) {
        self.config.mode = "event".to_string();
        self.config.time_value = 5.0;
        self.config.format = "$top_folder-$time-$date".to_string();
        self.status_msg = "Fields reset.".to_string();
    }

    fn save(&mut self) {
        if self.config.source_dir.trim().is_empty() || self.config.backup_dir.trim().is_empty() {
            self.status_msg = "Error: Missing fields.".to_string();
            return;
        }
        if self.config.time_value < 0.0 {
            self.status_msg = "Error: Time value must be positive.".to_string();
            return;
        }
        let forbidden = ['<', '>', ':', '"', '/', '\\', '|', '?', '*'];
        if self.config.format.chars().any(|c| forbidden.contains(&c)) {
             self.status_msg = "Warning: Format contains forbidden characters.".to_string();
             return;
        }

        match save_config(&self.config) {
            Ok(_) => self.status_msg = "Configuration saved!".to_string(),
            Err(e) => self.status_msg = format!("Error saving: {}", e),
        }
    }
}

impl App for ConfigApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut Frame) {
        let my_frame = egui::containers::Frame::default()
            .inner_margin(20.0)
            .fill(ctx.style().visuals.window_fill());

        egui::CentralPanel::default().frame(my_frame).show(ctx, |ui| {
            ui.vertical_centered(|ui| {
                ui.heading(egui::RichText::new("Auto Backup Settings").size(24.0).strong());
            });
            ui.add_space(20.0);

            ui.label(egui::RichText::new("Source Directory:").strong());
            ui.add_space(4.0);
            ui.horizontal(|ui| {
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if ui.button("Browse...").clicked() {
                        if let Some(path) = rfd::FileDialog::new().pick_folder() {
                            self.config.source_dir = path.to_string_lossy().to_string();
                        }
                    }
                    ui.add(egui::TextEdit::singleline(&mut self.config.source_dir).desired_width(f32::INFINITY));
                });
            });

            ui.add_space(15.0);

            ui.label(egui::RichText::new("Backup Destination:").strong());
            ui.add_space(4.0);
            ui.horizontal(|ui| {
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if ui.button("Browse...").clicked() {
                        if let Some(path) = rfd::FileDialog::new().pick_folder() {
                            self.config.backup_dir = path.to_string_lossy().to_string();
                        }
                    }
                    ui.add(egui::TextEdit::singleline(&mut self.config.backup_dir).desired_width(f32::INFINITY));
                });
            });

            ui.add_space(20.0);
            ui.separator();
            ui.add_space(10.0);

            ui.horizontal(|ui| {
                ui.label(egui::RichText::new("Backup Mode:").strong());
                ui.add_space(10.0); // Khoảng cách
                ui.radio_value(&mut self.config.mode, "event".to_string(), "Event-Based (Real-time)");
                ui.add_space(10.0);
                ui.radio_value(&mut self.config.mode, "periodic".to_string(), "Periodic (Interval Scan)");
            });

            ui.add_space(15.0);

            let (label_text, desc_text) = if self.config.mode == "event" {
                ("Wait Time (Debounce):", "Backup X seconds AFTER typing stops.")
            } else {
                ("Scan Interval:", "Scan folder every X seconds.")
            };

            ui.horizontal(|ui| {
                ui.label(egui::RichText::new(label_text).strong());
                ui.add(egui::DragValue::new(&mut self.config.time_value).speed(0.1).range(0.1..=3600.0));
                ui.label("seconds");
            });
            // Dòng mô tả nhỏ nằm ngay dưới
            ui.label(egui::RichText::new(desc_text).small().color(egui::Color32::GRAY));

            ui.add_space(15.0);

            // --- FORMAT ---
            ui.label(egui::RichText::new("Folder Name Format:").strong());
            ui.add(egui::TextEdit::singleline(&mut self.config.format).desired_width(f32::INFINITY));
            ui.label(egui::RichText::new("Available: $name, $date, $time, $count, $top_folder").monospace().small().color(egui::Color32::GRAY));

            ui.add_space(25.0);

            // --- BUTTONS ---
            ui.columns(2, |columns| {
                columns[0].vertical_centered_justified(|ui| {
                    if ui.add_sized([ui.available_width(), 40.0], egui::Button::new(egui::RichText::new("RESET").strong())).clicked() {
                        self.reset_fields();
                    }
                });
                columns[1].vertical_centered_justified(|ui| {
                     let btn = egui::Button::new(egui::RichText::new("SAVE CONFIG").strong()).fill(egui::Color32::from_rgb(46, 125, 50));
                    if ui.add_sized([ui.available_width(), 40.0], btn).clicked() {
                        self.save();
                    }
                });
            });

            if !self.status_msg.is_empty() {
                ui.add_space(15.0);
                ui.label(egui::RichText::new(&self.status_msg).color(egui::Color32::LIGHT_BLUE));
            }

            ui.with_layout(egui::Layout::bottom_up(egui::Align::Center), |ui| {
                ui.add_space(10.0);
                ui.label(egui::RichText::new("To run worker: ./Auto-Backup.exe --worker").monospace().color(egui::Color32::GRAY));
                ui.separator();
            });
        });
    }
}