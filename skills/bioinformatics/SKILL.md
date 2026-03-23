---
name: bioinformatics
description: Bioinformatics guidelines for variant analysis, pathogenicity scoring, genomic standards, and pipeline tools. Focused on reliable sources for clinical and research bioinformatics workflows.
type: skill
---

# Bioinformatics Guidelines

> Skill for bioinformaticians covering variant scoring, genomic standards, annotation tools, and pipeline best practices.
> Invoke with `/bioinformatics` when working on genomic analysis, variant interpretation, or pipeline design.

---

## Section 1: Variant Pathogenicity Scoring

Scoring variant pathogenicity requires combining multiple in-silico predictors. No single tool is definitive — use ensemble approaches and always cross-reference with clinical databases.

### Core Scoring Tools

| Tool | Purpose | Source |
|------|---------|--------|
| SIFT | Predicts whether amino acid substitution affects protein function (score 0–1; <0.05 = damaging) | https://sift.bii.a-star.edu.sg/sift4g/ |
| REVEL | Ensemble score for missense variant pathogenicity (0–1; >0.5 = likely pathogenic) | https://sites.google.com/site/revelgenomics/ |
| MutationTaster | Predicts disease-causing potential of sequence alterations | https://www.mutationtaster.org/ |
| ANNOVAR | Functional annotation of genetic variants from sequencing data | https://annovar.openbioinformatics.org/en/latest/ |
| GATK Phred Scores | Quality scoring for variant calling confidence (Q30 = 99.9% accuracy) | https://gatk.broadinstitute.org/hc/en-us/articles/360035531872-Phred-scaled-quality-scores |

### Scoring Interpretation Guidelines

**SIFT**
- Score < 0.05 → **Damaging** (affects protein function)
- Score ≥ 0.05 → **Tolerated**
- Always check the median sequence conservation score alongside SIFT score

**REVEL**
- Score > 0.75 → Strong evidence of pathogenicity
- Score 0.5–0.75 → Moderate evidence
- Score < 0.15 → Likely benign
- Recommended threshold for clinical use: **> 0.5** (adjustable per study design)

**GATK Phred Quality Scores**
- GQ (Genotype Quality) ≥ 20 → Acceptable
- GQ ≥ 30 → High confidence
- DP (Depth) ≥ 10× → Minimum; ≥ 30× preferred for clinical
- Filter: `PASS` in FILTER column is mandatory before scoring

### Ensemble Scoring Workflow

```
1. Run GATK variant calling → apply VQSR or hard filters
2. Annotate with ANNOVAR (refGene, gnomAD, ClinVar, dbSNP)
3. Apply in-silico predictors: SIFT, REVEL, MutationTaster
4. Cross-reference with DECIPHER and ClinVar
5. Apply ACMG/AMP classification criteria (PS, PM, PP, BA, BS, BP categories)
6. Final classification: Pathogenic / Likely Pathogenic / VUS / Likely Benign / Benign
```

### ACMG/AMP Classification (Quick Reference)

Follow ACMG standards for variant classification:
- **PS** = Strong pathogenic evidence
- **PM** = Moderate pathogenic evidence
- **PP** = Supporting pathogenic evidence
- **BA** = Stand-alone benign evidence
- **BS** = Strong benign evidence
- **BP** = Supporting benign evidence

Full standards: https://www.acmg.net/ACMG/Medical-Genetics-Practice-Resources/Genetics_Lab_Standards/

### Key Databases for Cross-Referencing

- **ClinVar** — Clinical significance of variants: https://www.ncbi.nlm.nih.gov/clinvar/
- **DECIPHER** — Genomic variants in rare disease: https://www.deciphergenomics.org/
- **gnomAD** — Population allele frequencies (essential for filtering common variants)
- **NCBI GEO** — Gene expression datasets for functional context: https://www.ncbi.nlm.nih.gov/geo/

### Common Pitfalls

- Do NOT rely on a single predictor — SIFT and PolyPhen-2 agree only ~70% of the time
- Always filter by population frequency (gnomAD MAF < 0.01 for rare disease)
- VUS (Variant of Uncertain Significance) should NOT be reported as pathogenic without additional evidence
- Check strand orientation when interpreting ANNOVAR output for indels

---

> **More sections coming:** Genomics Data Sources (GEO/DECIPHER), Container & Workflow Management (Seqera), Clinical Reporting Standards (ACMG).

---

## Section 2: Pipeline Standards & Workflow Management

Reproducible, portable pipelines are the backbone of reliable bioinformatics. Follow community standards to ensure your workflows are shareable, scalable, and audit-ready.

### Core Frameworks & Standards Bodies

| Resource | Purpose | Source |
|----------|---------|--------|
| nf-core | Community-curated Nextflow pipelines for bioinformatics | https://nf-co.re/ |
| GA4GH | Global standards for genomic data sharing and interoperability | https://www.ga4gh.org/ |
| GATK Best Practices | Variant discovery pipeline guidelines from Broad Institute | https://gatk.broadinstitute.org/hc/en-us/categories/360002369672 |
| Seqera Containers | Reproducible, versioned containers for bioinformatics tools | https://seqera.io/containers/ |

### nf-core Pipeline Standards

**Before writing a pipeline, check nf-core first** — there may already be a maintained pipeline for your use case.

Key nf-core pipelines:
- `nf-core/sarek` — Germline/somatic variant calling (WGS/WES)
- `nf-core/rnaseq` — RNA-seq quantification and QC
- `nf-core/methylseq` — Bisulfite sequencing analysis
- `nf-core/chipseq` — ChIP-seq peak calling
- `nf-core/ampliseq` — 16S/ITS amplicon sequencing

**nf-core compliance checklist:**
- [ ] Use `nf-core/tools` to scaffold new pipelines (`nf-core create`)
- [ ] Pin all tool versions (no `latest` tags in production)
- [ ] Use `nf-core/configs` for institutional HPC profiles
- [ ] Include `--outdir`, `--input`, and `--genome` as standard params
- [ ] Pass `nf-core lint` before sharing

### GA4GH Standards for Data Interoperability

Apply GA4GH standards when sharing or receiving genomic data across institutions:

- **htslib/VCF spec** — Standard variant format; always validate with `bcftools stats`
- **SAM/BAM/CRAM** — Alignment formats; prefer CRAM for storage efficiency
- **GA4GH Passports** — Identity/access tokens for federated data access
- **DRS (Data Repository Service)** — Standard API for accessing genomic files across clouds
- **WES (Workflow Execution Service)** — Submit and monitor workflow runs via standard API

### GATK Best Practices Workflow

```
Germline Short Variant Discovery (WGS/WES):
1. FastQC / MultiQC → assess raw read quality
2. BWA-MEM2 → align to reference genome (GRCh38 preferred)
3. GATK MarkDuplicates → remove PCR duplicates
4. GATK BaseQualityScoreRecalibration (BQSR) → recalibrate base scores
5. GATK HaplotypeCaller → call variants per-sample (gVCF mode)
6. GATK GenomicsDBImport + GenotypeGVCFs → joint genotyping
7. VQSR (≥30 samples) or Hard Filters (<30 samples) → filter variants
8. Annotate → ANNOVAR / VEP / SnpEff
```

### Container & Reproducibility Standards

**Use Seqera Containers for tool versioning:**
- Every pipeline tool should have a pinned container image
- Prefer `docker://` or `singularity://` URIs in Nextflow configs
- Use `seqera.io/containers` to find pre-built, tested images

**Nextflow config best practices:**
```groovy
// Always pin process containers
process {
    withName: 'GATK_HAPLOTYPECALLER' {
        container = 'community.wave.seqera.io/library/gatk4:4.5.0.0'
    }
}

// Use profiles for portability
profiles {
    docker { docker.enabled = true }
    singularity { singularity.enabled = true }
    slurm { process.executor = 'slurm' }
}
```

### Common Pitfalls

- Never use `GRCh37` for new projects — use `GRCh38` (hg38) as the default reference
- Always run `FastQC` before AND after trimming — trimming can introduce bias
- Do not mix samples from different sequencing runs without batch correction
- VQSR requires ≥30 samples for reliable tranche calibration; use hard filters below that
- CRAM files require the reference genome for decoding — always store the reference alongside

### Quality Control Metrics (Minimum Thresholds)

| Metric | Minimum | Preferred |
|--------|---------|-----------|
| Mean coverage (WGS) | 30× | 50× |
| Mean coverage (WES) | 100× | 200× |
| % bases ≥ Q30 | 75% | 85% |
| Duplication rate | < 20% | < 10% |
| % on-target reads (WES) | > 70% | > 85% |
| Ti/Tv ratio (WGS) | 2.0–2.1 | 2.0–2.1 |
| Ti/Tv ratio (WES) | 2.6–3.5 | 2.8–3.3 |
