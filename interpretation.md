## Final Summary of Findings and Insights
1. **Weather Impact:** From the exploratory data analysis, lower visibility (`vsby`) and higher wind speeds (`sknt`) strongly correlate with delayed flights.
2. **Traffic Density:** Higher traffic density at the origin airport increases the probability of delays.
3. **Model Performance:** Ensemble methods (Random Forest, XGBoost) generally perform the best, capturing non-linear relationships.
4. **Deep Learning:** LSTM networks can capture time-series dependencies in cascading delays.
5. **Real-Time Capabilities:** The pipeline successfully integrates live METAR weather data to predict delays dynamically.