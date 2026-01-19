# RWD Cohort Identification (Python Notebooks)

A complete, notebook-driven pipeline to extract structured patient data from clinical notes or HL7, convert results to OMOP CDM, and apply cohort eligibility criteria using IMO APIs.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Features and Settings](#features-and-settings)
- [Troubleshooting](#troubleshooting)
- [Output Format](#output-format)
- [Architecture](#architecture)
- [License](#license)
- [Support](#support)

## Overview

This solution supports three workflows. Choose the one that fits your inputs and target outputs:

1. **OMOP Workflow (Notes → OMOP → Cohort)**
  - Start with de-identified clinical notes in CSV
  - Extract entities via IMO NLP → Excel
  - Convert to OMOP CDM tables
  - Apply cohort eligibility criteria via IMO FHIR ValueSets

2. **HL7 Workflow (HL7 → Codes → Cohort)**
  - Start with HL7 messages
  - Parse/normalize to extract ICD10CM/CPT/LOINC/SNOMED codes
  - Apply cohort eligibility criteria

3. **Data Lake Workflow (Medallion pipeline)**
  - Governed bronze/silver/gold data layers
  - Ingestion, normalization, enrichment and curation at scale
  - Produces curated datasets for analytics and cohorting

### Data Flow Diagrams

#### using-OMOP (Notes → OMOP → Cohort)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                              RWD COHORT IDENTIFICATION (using-OMOP)                                                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ───▶  ┌──────────────────────┐  ───▶  ┌──────────────────────┐  ───▶  ┌──────────────────────────┐  ───▶  ┌──────────────────────┐  ───▶  ┌──────────────────────────┐  ───▶  ┌──────────────────────┐
│  Notes (CSV input)   │        │   IMO NLP API        │        │  patient_output.xlsx │        │   OMOP Conversion        │        │  OMOP CSV Tables     │        │  Cohort Criteria Apply   │        │  Cohort Results      │
│  upload_ihm/*.csv    │        │  Entity Extraction   │        │  (structured results)│        │  (vocabularies/*.csv)    │        │  Output/OMOP_CSV/*   │        │  (IMO FHIR ValueSets)    │        │  (reports/exports)   │
└──────────────────────┘        └──────────────────────┘        └──────────────────────┘        └──────────────────────────┘        └──────────────────────┘        └──────────────────────────┘        └──────────────────────┘
```

#### using-HL7 (HL7 → Codes → Cohort)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                              RWD COHORT IDENTIFICATION (using-HL7)                                                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ───▶  ┌──────────────────────────┐  ───▶  ┌────────────────────────────┐  ───▶  ┌──────────────────────────┐  ───▶  ┌────────────────────────────┐  ───▶  ┌──────────────────────────┐  ───▶  ┌──────────────────────┐
│  HL7 messages        │        │  HL7 Parse & Extraction  │        │  trial_patient_dict        │        │  Code Normalization      │        │  Normalized Patient Codes  │        │  Cohort Criteria Apply   │        │  Cohort Results      │
│  uploads_hl7/hl7_data│        │  (ICD10CM/CPT/LOINC/SCT) │        │  (codes per patient)       │        │  (IMO Precision API)     │        │  (filled/corrected codes)  │        │  (IMO FHIR ValueSets)    │        │  (reports/exports)   │
└──────────────────────┘        └──────────────────────────┘        └────────────────────────────┘        └──────────────────────────┘        └────────────────────────────┘        └──────────────────────────┘        └──────────────────────┘
```

#### using-DataLake-Architecture (Medallion Pipeline)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                          MEDALLION DATA LAKE ARCHITECTURE (using-DataLake-Architecture)                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────┐  ───▶  ┌────────────────────────────────┐  ───▶  ┌───────────────────────────────┐  ───▶  ┌────────────────────────────┐  ───▶  ┌───────────────────────────┐  ───▶  ┌─────────────────────────┐
│  Raw Patient Data     │        │  🥉 BRONZE ZONE (S3)           │        │  🥈 SILVER ZONE (S3)          │        │  Download Precision Set    │        │  🥇 GOLD ZONE (S3)        │        │  Curated Analytics Data │
│  DQA_Input.csv        │        │  Raw Ingestion & Storage       │        │  Normalized Data              │        │  IMO FHIR ValueSet API     │        │  Cohort-Filtered          │        │  Business Intelligence  │
│  (local files)        │        │  bronze/patient_data.csv       │        │  IMO Precision Normalize API  │        │  Cohort Criteria Codes     │        │  gold/cohort_patient_data │        │  Reporting & Decisions  │
└───────────────────────┘        │  • Unprocessed                 │        │  • Standardized codes         │        │  (LOINC/ICD10CM/RXNORM/CPT)│        │  • Business-ready         │        └─────────────────────────┘
                                 │  • As-is storage               │        │  • LOINC, ICD10CM, RXNORM,    │        └────────────────────────────┘        │  • Criteria-matched       │
                                 │  • Historical archive          │        │    CPT enrichment             │                                              │  • Decision support       │
                                 └────────────────────────────────┘        │  • Quality improved           │                                              │  • Reporting ready        │
                                                                           │  silver/normalized_patient_   │                                              └───────────────────────────┘
                                                                           │        data.csv               │
                                                                           └───────────────────────────────┘
```
```
Legend:
┌────┐ Step    │  Data ▶▶▶ Flow
└────┘ Object
```

## Prerequisites

- Python 3.9 or higher
- IMO API credentials (Auth0 client credentials)
- Jupyter Notebook/Lab or VS Code + Jupyter extension
- OMOP vocabularies (for conversion): `vocabularies/CONCEPT.csv`, `vocabularies/CONCEPT_RELATIONSHIP.csv` (tab-delimited from OHDSI Athena)

## Installation

1. Navigate to this folder:
  ```bash
  cd "solution-engineering/RWE-Cohort-Identification"
  ```

2. Create and activate a virtual environment.

  Windows (PowerShell):
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install --upgrade pip
  ```

  macOS/Linux (bash):
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  ```

3. Install the required packages (from requirements.txt):

  ```bash
  pip install -r requirements.txt
  ```

4. (Optional) Register the kernel for Jupyter/VS Code:

  ```bash
  python -m ipykernel install --user --name rwd-cohort-notebooks --display-name "Python (rwd-cohort)"
  ```

## Configuration

Configure IMO API access in `config.json` (this folder):

```json
{
  "auth0": {
   "domain": "auth.imohealth.com",
   "client_id": "YOUR_IMO_CLIENT_ID",
   "client_secret": "YOUR_IMO_CLIENT_SECRET",
   "audience": "https://api.imohealth.com"
  },
  "api": { "base_url": "https://api.imohealth.com" }
}
```


## Usage

### OMOP Workflow (Notes → OMOP → Cohort)

Prerequisites:
- Notes CSVs in `upload_ihm/` with columns: `hospitalGuid`, `encounterGuid`, `patientGuid`, `notesDEID`
- OMOP vocabularies in `vocabularies/`: `CONCEPT.csv`, `CONCEPT_RELATIONSHIP.csv` (tab-delimited from OHDSI Athena)

Run Order:
1. `SolutionAccelerator_RWE_Extraction_From_Notes_To_Patient_Data.ipynb` (in `using-OMOP/`) 
  - Input: `upload_ihm/*.csv`
  - Output: `Output/patient_output.xlsx`
2. `SolutionAccelerator_RWE_Patient_Data_to_OMOP_Converter.ipynb` (in `using-OMOP/`) 
  - Input: `Output/patient_output.xlsx`, `vocabularies/*`
  - Output: `Output/OMOP_CSV/*.csv`
3. `SolutionAccelerator_RWE_Applying_Cohort_Criteria.ipynb` (in `using-OMOP/`) 
  - Input: `Output/OMOP_CSV/*.csv`
  - Action: Fetch ValueSets via IMO FHIR; apply inclusion criteria; export results

### HL7 Workflow (HL7 → Codes → Cohort)

Prerequisites:
- HL7 messages under project-level `uploads/hl7_data/`

Run Order:
1. `SolutionAccelerator_for_RWE_Cohort_identification_withHL7.ipynb` (in `using-HL7/`)
  - Input: `uploads/hl7_data/*`
  - Action: Parse HL7 with `hl7apy`, extract codes, optional normalization via IMO APIs
  - Note: If running from this folder, adjust path to `../uploads/hl7_data/` or start Jupyter from project root


### Data Lake Workflow (Medallion)

Prerequisites:
- DQA and staged inputs under `using-DataLake-Architecture/`

Run Order (example):
1. `Medallion_DataLake_Patient_Pipeline.ipynb` (in `using-DataLake-Architecture/`)
  - Input: `DQA_Input.csv` and source datasets
  - Action: Ingest → Normalize/Enrich → Curate (bronze/silver/gold)
  - Output: Curated tables for analytics/cohorting

### Launch Jupyter

```bash
jupyter lab
# or
jupyter notebook
```

Select the kernel "Python (rwd-cohort)" and Run All Cells in each notebook in the order above.

## Features and Settings

### NLP Extraction (Notes)

- Endpoint: IMO Clinical Comprehensive NLP (`/entityextraction/pipelines/imo-clinical-comprehensive?version=3.0`)
- Adjustable parameters inside the notebook:

```python
domain_filter = ["problem", "procedure", "medication", "lab"]
score_threshold = 0.0
request_delay = 0.5  # seconds between API calls to avoid rate limiting
```

### OMOP Conversion

- Requires `vocabularies/CONCEPT.csv` and `vocabularies/CONCEPT_RELATIONSHIP.csv`
- Maps ICD10CM/RXNORM/LOINC/CPT to OMOP standard concepts
- Exports tables to `Output/OMOP_CSV/*.csv`

### HL7-Based Path

- Parses HL7 messages from `uploads/hl7_data/`
- Extracts codes and performs cohort matching similar to the notes-based flow

## Troubleshooting

### Common Issues

1. Authentication Error (IMO Auth0)
  - Verify `domain`, `client_id`, `client_secret`, `audience` in `config.json`

2. Rate Limiting (HTTP 429)
  - Notebooks include pacing and retry examples; re-run after a short wait

3. Missing CSV Columns
  - Ensure notes CSVs include: `hospitalGuid`, `encounterGuid`, `patientGuid`, `notesDEID`

4. OMOP Vocabulary Files Not Found
  - Download from OHDSI Athena and place in `vocabularies/`

5. Excel Write/Read Issues
  - Confirm `openpyxl` and `xlsxwriter` are installed in the selected kernel

## Output Format

Directory structure and key files:

```
Output/
├── patient_output.xlsx
├── cohort_matching_results.csv
└── OMOP_CSV/
   ├── PERSON.csv
   ├── VISIT_OCCURRENCE.csv
   ├── CONDITION_OCCURRENCE.csv
   ├── DRUG_EXPOSURE.csv
   ├── MEASUREMENT.csv
   └── PROCEDURE_OCCURRENCE.csv
```

## Architecture



## License

[Include your license information here]

## Support

For questions or issues, contact:
- IMO API Support: [support contact]
- Internal Team: [team contact]
