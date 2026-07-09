pub struct Order {
    pub id: u64,
    pub price: f64,
    pub volume: f64,
}

pub fn simulate_order_matching(orders: &[Order]) -> f64 {
    // A proxy for order matching engine that returns execution price
    if orders.is_empty() {
        return 0.0;
    }

    let avg_price: f64 = orders.iter().map(|o| o.price).sum::<f64>() / (orders.len() as f64);
    avg_price
}
