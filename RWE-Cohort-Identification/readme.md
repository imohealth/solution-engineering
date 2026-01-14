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

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RWD COHORT IDENTIFICATION PIPELINE                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│  Notes (CSV input)   │       │   IMO NLP API        │       │  patient_output.xlsx │
│  upload_ihm/*.csv    │  ───▶ │  Entity Extraction   │  ───▶ │  (structured results)│
└─────────┬────────────┘       └──────────┬───────────┘       └─────────┬────────────┘
       │                                 │                              │
       │                                 ▼                              ▼
       │                    ┌──────────────────────────┐    ┌──────────────────────┐
       │                    │   OMOP Conversion        │    │  OMOP CSV Tables     │
       │                    │  (vocabularies/*.csv)    │    │  Output/OMOP_CSV/*   │
       │                    └──────────┬───────────────┘    └─────────┬────────────┘
       │                                 │                              │
       │                                 ▼                              ▼
       │                    ┌──────────────────────────┐    ┌──────────────────────┐
       │                    │  Cohort Criteria Apply  │    │  Cohort Results      │
       │                    │  (IMO FHIR ValueSets)   │    │  (reports/exports)   │
       │                    └──────────────────────────┘    └──────────────────────┘
       │
       ▼
┌──────────────────────┐  Alternative Path
│ HL7 messages         │  uploads/hl7_data/*  ▶  HL7 Parse ▶ Matching
└──────────────────────┘

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
  cd "SolutionAccelertors/RWD-Cohort-Identification/PythonNotebook"
  ```

2. Create and activate a virtual environment, then install dependencies.

  Windows (PowerShell):
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install --upgrade pip
  pip install pandas numpy requests xlsxwriter openpyxl hl7apy boto3 nbformat nbconvert ipykernel jupyter
  python -m ipykernel install --user --name rwd-cohort-notebooks --display-name "Python (rwd-cohort)"
  ```

  macOS/Linux (bash):
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install pandas numpy requests xlsxwriter openpyxl hl7apy boto3 nbformat nbconvert ipykernel jupyter
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
1. `SolutionAccelerator_RWE_Extraction_From_Notes_To_Patient_Data.ipynb`
  - Input: `upload_ihm/*.csv`
  - Output: `Output/patient_output.xlsx`
2. `SolutionAccelerator_RWE_Patient_Data_to_OMOP_Converter.ipynb`
  - Input: `Output/patient_output.xlsx`, `vocabularies/*`
  - Output: `Output/OMOP_CSV/*.csv`
3. `SolutionAccelerator_RWE_Applying_Cohort_Criteria.ipynb`
  - Input: `Output/OMOP_CSV/*.csv`
  - Action: Fetch ValueSets via IMO FHIR; apply inclusion criteria; export results

### HL7 Workflow (HL7 → Codes → Cohort)

Prerequisites:
- HL7 messages under project-level `uploads/hl7_data/`

Run Order:
1. `SolutionAccelerator_for_RWE_Cohort_identification_withHL7.ipynb`
  - Input: `uploads/hl7_data/*`
  - Action: Parse HL7 with `hl7apy`, extract codes, optional normalization via IMO APIs
  - Note: If running from this folder, adjust path to `../uploads/hl7_data/` or start Jupyter from project root

2. (Optional) Apply cohort criteria within the HL7 notebook or use the OMOP criteria notebook if you convert to OMOP downstream.

### Data Lake Workflow (Medallion)

Prerequisites:
- DQA and staged inputs under `using-DataLake-Architecture/`

Run Order (example):
1. `Medallion_DataLake_Patient_Pipeline.ipynb` (in `using-DataLake-Architecture/`)
  - Input: `DQA_TargetRWE_Input.csv` and source datasets
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
