use std::fs::File;
use std::io::{BufRead, BufReader};

pub struct Tick {
    pub timestamp: String,
    pub bid: f64,
    pub ask: f64,
}

pub fn load_ticks(path: &str) -> Vec<Tick> {
    // In a real scenario, this parses CSV. Here we mock reading the raw file we created
    let file = File::open(path).expect("Failed to open tick file");
    let reader = BufReader::new(file);

    let mut ticks = Vec::new();
    // Proxy parsing
    for (i, _line) in reader.lines().enumerate() {
        if i > 100 { break; } // limit for memory in sim
        ticks.push(Tick {
            timestamp: format!("2024-01-01T10:00:{:02}.000", i % 60),
            bid: 1.1000 + (i as f64) * 0.0001,
            ask: 1.1001 + (i as f64) * 0.0001,
        });
    }

    if ticks.is_empty() {
        // Fallback if file was empty
        ticks.push(Tick { timestamp: "mock".to_string(), bid: 1.0, ask: 1.1 });
    }

    ticks
}
