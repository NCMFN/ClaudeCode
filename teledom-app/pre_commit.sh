#!/bin/bash
set -e
echo "Running Pre-commit checks..."
npm run build
echo "All checks passed!"
