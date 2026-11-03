# Explainable and Adversarially Aware Detection of Enterprise Digital Sanitization Activity

**Status**: PROPOSED METHODOLOGY

This repository contains the evaluation methodology and pipeline for temporal leakage in insider-threat and sanitization-detection benchmarks.

## Data Caveats
- LANL contains no file-path or removable-media data; those feature groups were removed, not simulated.
- Reported metrics are optimistic relative to deployment prevalence.

The chronological-evaluation protocol is specified and unit-tested but has not been validated on authentic LANL data in this environment because the 7626505158 byte `auth.txt.gz` file exceeded the sandbox download time limit. The file exists on the author's machine and the evaluation is deferred to a local run.
