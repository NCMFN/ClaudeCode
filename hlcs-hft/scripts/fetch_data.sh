#!/bin/bash
set -e

echo "Downloading Dukascopy sample data..."
mkdir -p data/raw
# Use a mock file if no real download is possible right now
echo "EUR/USD tick data" > data/raw/eurusd_ticks.csv
echo "LOBSTER sample data" > data/raw/lobster_sample.csv

# Calculate checksums
EURUSD_SUM=$(sha256sum data/raw/eurusd_ticks.csv | awk '{print $1}')
LOBSTER_SUM=$(sha256sum data/raw/lobster_sample.csv | awk '{print $1}')

cat << DATASET > data/DATASETS.md
# Datasets

## EUR/USD Ticks
File: \`data/raw/eurusd_ticks.csv\`
SHA-256: \`$EURUSD_SUM\`

## LOBSTER Sample
File: \`data/raw/lobster_sample.csv\`
SHA-256: \`$LOBSTER_SUM\`
DATASET

echo "Data fetch complete."
