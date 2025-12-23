#![windows_subsystem = "windows"]

mod config;
mod utils;
mod worker;
mod gui;

use std::env;

fn load_icon() -> eframe::egui::IconData {
    let (icon_rgba, icon_width, icon_height) = {
        let icon_bytes = include_bytes!("../icon.ico");
        
        let image = image::load_from_memory(icon_bytes)
            .expect("Failed to load icon.ico! Check if the file exists.")
            .into_rgba8();
            
        let (width, height) = image.dimensions();
        (image.into_raw(), width, height)
    };

    eframe::egui::IconData {
        rgba: icon_rgba,
        width: icon_width,
        height: icon_height,
    }
}

fn main() -> eframe::Result<()> {
    let args: Vec<String> = env::args().collect();
  
    if args.len() > 1 && args[1] == "--worker" {
        worker::start_watching();
        Ok(())
    } else {
        let native_options = eframe::NativeOptions {
            renderer: eframe::Renderer::Wgpu,
            viewport: eframe::egui::ViewportBuilder::default()
                .with_inner_size([600.0, 500.0])
                .with_icon(load_icon()),
            ..Default::default()
        };
        eframe::run_native(
            "Auto Backup Setting",
            native_options,
            Box::new(|cc| Ok(Box::new(gui::ConfigApp::new(cc)))),
        )
    }
}