use hlcs_market_sim::slippage;

#[test]
fn test_end_to_end_pipeline() {
    slippage::calculate_slippage();
}
