# ValueSet Generation Tool

A comprehensive tool for generating medical value sets from patient education documents. This tool uses AI/LLM services to extract medical entities, expand terms, generate keywords, and create standardized value sets for clinical use.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Features and Settings](#features-and-settings)
- [Troubleshooting](#troubleshooting)

## Overview

The ValueSet Generation Tool processes medical documents through the following pipeline:

1. **Document Conversion**: Converts PDF/HTML documents to plain text
2. **Document Summarization**: Extracts primary subjects and entities from documents
3. **Term Expansion**: Expands medical terms using IMO search and ICD-10 hierarchy
4. **Pruning**: Filters relevant terms based on clinical context
5. **Keyword Generation**: Creates search keywords for the value sets
6. **ValueSet Creation**: Generates standardized value set files with codes and metadata

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VALUESET GENERATION PIPELINE                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  Step 1: Document    │
│     Conversion       │
│ ┌──────────────────┐ │
│ │ PDF/HTML Files   │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │  pypdf/BS4       │ │
│ │  Conversion      │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │  Plain Text      │ │◀─────────────┐
│ │  (.txt files)    │ │              │
│ └────────┬─────────┘ │              │
└──────────┼───────────┘              │
           │                          │  Input to
           v                          │  Main Pipeline
┌──────────────────────┐              │
│  Step 2: Document    │              │
│   Summarization      │              │
│ ┌──────────────────┐ │              │
│ │  Plain Text      │ │──────────────┘
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │ LLM Service      │ │
│ │ ┌──────────────┐ │ │
│ │ │ IMO API  or  │ │ │
│ │ │ OpenAI GPT-4 │ │ │
│ │ └──────────────┘ │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │ Summary Object   │ │
│ │ • Primary:       │ │
│ │   - title        │ │
│ │   - domain       │ │
│ │   - IMO code     │ │
│ │ • Related types  │ │
│ │ • Gender         │ │
│ │ • Age group      │ │
│ └────────┬─────────┘ │
└──────────┼───────────┘
           │
           v
┌──────────────────────┐
│  Step 3: Term        │
│    Expansion         │
│ ┌──────────────────┐ │
│ │ Summary + Terms  │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │ Diagnostic       │ │
│ │ Workflow Search  │ │
│ │ (IMO API)        │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │ Core Search      │ │
│ │ (IMO Search API) │ │
│ │ • ICD-10 codes   │ │
│ │ • CPT codes      │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │ ICD-10 Hierarchy │ │
│ │ Expansion        │ │
│ │ (Parent codes)   │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │ Expanded Terms   │ │
│ │ (100-2000 codes) │ │
│ └────────┬─────────┘ │
└──────────┼───────────┘
           │
           v
┌──────────────────────┐
│  Step 4: Pruning     │
│   (Optional)         │
│ ┌──────────────────┐ │
│ │ Expanded Terms   │ │
│ └────────┬─────────┘ │
│          │           │
│  Enable? │           │
│ ┌────────v────────┐ │
│ │ Config Check:   │ │
│ │ enable_pruning  │ │
│ └────┬──────┬─────┘ │
│      │      │       │
│  YES │      │ NO    │
│      │      │       │
│      v      v       │
│ ┌────────┐ Skip    │
│ │ LLM    │ ─────┐  │
│ │Service │      │  │
│ │┌──────┐│      │  │
│ ││ AWS  ││      │  │
│ ││ or   ││      │  │
│ ││OpenAI││      │  │
│ │└──────┘│      │  │
│ │Batches │      │  │
│ │of 25   │      │  │
│ └───┬────┘      │  │
│     │           │  │
│     v           v  │
│ ┌──────────────────┐ │
│ │ Pruned Terms     │ │
│ │ (10-200 codes)   │ │
│ └────────┬─────────┘ │
└──────────┼───────────┘
           │
           v
┌──────────────────────┐
│  Step 5: Keyword     │
│    Generation        │
│   (Optional)         │
│ ┌──────────────────┐ │
│ │ Pruned Terms +   │ │
│ │ Document Text    │ │
│ └────────┬─────────┘ │
│          │           │
│  Enable? │           │
│ ┌────────v────────┐ │
│ │ Config Check:   │ │
│ │ enable_keywords │ │
│ └────┬──────┬─────┘ │
│      │      │       │
│  YES │      │ NO    │
│      │      │       │
│      v      v       │
│ ┌────────┐ Skip    │
│ │ LLM    │ ─────┐  │
│ │Service │      │  │
│ │┌──────┐│      │  │
│ ││ AWS  ││      │  │
│ ││ or   ││      │  │
│ ││OpenAI││      │  │
│ │└──────┘│      │  │
│ │Domain: │      │  │
│ │Problem,│      │  │
│ │Proc,   │      │  │
│ │Med     │      │  │
│ └───┬────┘      │  │
│     │           │  │
│     v           v  │
│ ┌──────────────────┐ │
│ │ Keywords List    │ │
│ │ (0-50 keywords)  │ │
│ └────────┬─────────┘ │
└──────────┼───────────┘
           │
           v
┌──────────────────────┐
│  Step 6: ValueSet    │
│     Creation         │
│ ┌──────────────────┐ │
│ │ Assemble:        │ │
│ │ • Summary        │ │
│ │ • Codes          │ │
│ │ • Keywords       │ │
│ │ • Metadata       │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │ Format JSON      │ │
│ │ Structure        │ │
│ └────────┬─────────┘ │
│          │           │
│          v           │
│ ┌──────────────────┐ │
│ │ Write Files:     │ │
│ │ • valueset.json  │ │
│ │ • summary.json   │ │
│ └────────┬─────────┘ │
└──────────┼───────────┘
           │
           v
    ┌─────────────┐
    │   OUTPUT    │
    │   FILES     │
    └─────────────┘

Legend:
═══════════════════════════════════════════════════
┌────┐
│    │  Processing Step
└────┘

┌────┐
│    │  Data Object
└────┘

  │     Data Flow
  v

═══════════════════════════════════════════════════

Configuration Impact:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 2: summarization.use_openai_llm (IMO vs OpenAI)
Step 4: term_expander.enable_pruning (Enable/Disable)
        pruning_service.llm_provider (AWS vs OpenAI)
Step 5: keyword_service.enable_keywords (Enable/Disable)
        keyword_service.llm_provider (AWS vs OpenAI)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access (if using AWS Bedrock)
- OpenAI API key (if using OpenAI GPT-4)
- IMO API credentials
- Virtual environment (recommended)

## Installation

1. **Clone the repository**:
   ```bash
   cd /path/to/Medical-Documents-To-ValueSets/src/valueset-generation
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Configuration File: `config.json`

The application is configured via the `config.json` file. Below are all available settings:

#### Authentication Settings

```json
{
  "auth.base_url": "https://api.imohealth.com",
  "auth.client_id": "YOUR_IMO_CLIENT_ID",
  "auth.client_secret": "YOUR_IMO_CLIENT_SECRET"
}
```

- **auth.base_url**: Base URL for IMO API authentication
- **auth.client_id**: Your IMO API client ID
- **auth.client_secret**: Your IMO API client secret

#### Summarization Service Settings

```json
{
  "summarization.base_url": "https://api.imohealth.com",
  "summarization.prompt_name": "v4_educational_document_subject_identification",
  "summarization.use_openai_llm": false,
  "summarization.openai_llm_api_key": "YOUR_OPENAI_API_KEY"
}
```

- **summarization.base_url**: IMO API base URL for document analysis
- **summarization.prompt_name**: Prompt template name for entity extraction
- **summarization.use_openai_llm**: 
  - `true`: Use OpenAI GPT-4 for summarization
  - `false`: Use IMO documentanalysis service (default)
- **summarization.openai_llm_api_key**: Your OpenAI API key (required if `use_openai_llm=true`)

#### Term Expansion Settings

```json
{
  "term_expander.enable_pruning": true,
  "search.base_url": "https://api.imohealth.com",
  "precision_sets.base_url": "https://precisionsets-api.imohealth.com"
}
```

- **term_expander.enable_pruning**: 
  - `true`: Enable term pruning to filter relevant terms (default)
  - `false`: Disable pruning, keep all expanded terms
- **search.base_url**: Base URL for IMO search API
- **precision_sets.base_url**: Base URL for IMO Precision Sets API

#### Keyword Service Settings

```json
{
  "keyword_service.enable_keywords": true,
  "keyword_service.llm_provider": "aws_bedrock",
  "keyword_service.openai_llm_api_key": "YOUR_OPENAI_API_KEY"
}
```

- **keyword_service.enable_keywords**: 
  - `true`: Generate keywords for value sets (default)
  - `false`: Skip keyword generation (empty keywords list)
- **keyword_service.llm_provider**: 
  - `"aws_bedrock"`: Use AWS Bedrock for keyword generation (default)
  - `"openai"`: Use OpenAI GPT-4 for keyword generation
- **keyword_service.openai_llm_api_key**: Your OpenAI API key (required if `llm_provider="openai"`)

#### Pruning Service Settings

```json
{
  "pruning_service.llm_provider": "aws_bedrock",
  "pruning_service.openai_llm_api_key": "YOUR_OPENAI_API_KEY"
}
```

- **pruning_service.llm_provider**: 
  - `"aws_bedrock"`: Use AWS Bedrock for term pruning (default)
  - `"openai"`: Use OpenAI GPT-4 for term pruning
- **pruning_service.openai_llm_api_key**: Your OpenAI API key (required if `llm_provider="openai"`)

#### S3 Settings (Optional)

```json
{
  "source_bucket": "your-s3-bucket",
  "processed_prefix": "processed/"
}
```

- **source_bucket**: S3 bucket name for source documents (optional)
- **processed_prefix**: S3 prefix for processed documents (optional)

## Usage

### Basic Command

```bash
python main.py \
  --input-dir "/path/to/input/documents" \
  --output-dir "/path/to/output" \
  --process-domain "problem"
```

### Command-Line Arguments

#### Required Arguments

- `--input-dir`: Path to input documents directory (or S3 URI: `s3://bucket/path`)
  - Supports local file paths or S3 URIs
  - Must contain `.txt` files (output from document conversion tool)

- `--process-domain`: Domain type for processing
  - Options: `"problem"`, `"procedure"`, `"medication"`
  - Determines which expansion and pruning logic to use

#### Optional Arguments

- `--output-dir`: Output directory for generated value sets (default: `./output`)
  - Supports local paths or S3 URIs
  - Directory will be created if it doesn't exist

- `--processed-dir`: Directory for marking processed documents (optional)
  - Used when tracking document processing status

- `--valueset-version`: Version string for generated value sets (default: `1.25.4.12`)
  - Embedded in value set metadata

- `--aws-profile`: AWS profile name to use (optional)
  - Overrides default AWS credentials
  - Useful for multi-account setups

- `--auth-client-id`: IMO API client ID (optional)
  - Overrides `config.json` value

- `--auth-client-secret`: IMO API client secret (optional)
  - Overrides `config.json` value

### Usage Examples

#### Example 1: Basic Local Processing

```bash
python main.py \
  --input-dir "../document-conversion/output" \
  --output-dir "output" \
  --process-domain "problem"
```

#### Example 2: Using S3 Input/Output

```bash
python main.py \
  --input-dir "s3://my-bucket/documents/" \
  --output-dir "s3://my-bucket/valuesets/" \
  --process-domain "procedure" \
  --aws-profile my-aws-profile
```

#### Example 3: Custom Version and Credentials

```bash
python main.py \
  --input-dir "/data/documents" \
  --output-dir "/data/valuesets" \
  --process-domain "medication" \
  --valueset-version "2.0.0" \
  --auth-client-id "your-client-id" \
  --auth-client-secret "your-client-secret"
```

## Features and Settings

### LLM Provider Selection

You can mix and match LLM providers for different services:

#### Scenario 1: All AWS Bedrock (Default)

```json
{
  "summarization.use_openai_llm": false,
  "keyword_service.llm_provider": "aws_bedrock",
  "pruning_service.llm_provider": "aws_bedrock"
}
```

**Requirements**: AWS credentials configured, Bedrock access enabled

#### Scenario 2: All OpenAI GPT-4

```json
{
  "summarization.use_openai_llm": true,
  "summarization.openai_llm_api_key": "sk-...",
  "keyword_service.llm_provider": "openai",
  "keyword_service.openai_llm_api_key": "sk-...",
  "pruning_service.llm_provider": "openai",
  "pruning_service.openai_llm_api_key": "sk-..."
}
```

**Requirements**: Valid OpenAI API key with GPT-4 access

#### Scenario 3: Hybrid Configuration

```json
{
  "summarization.use_openai_llm": true,
  "summarization.openai_llm_api_key": "sk-...",
  "keyword_service.llm_provider": "aws_bedrock",
  "pruning_service.llm_provider": "aws_bedrock"
}
```

**Use Case**: Use OpenAI for summarization, AWS Bedrock for everything else

### Enabling/Disabling Features

#### Disable Pruning

To skip term pruning and keep all expanded terms:

```json
{
  "term_expander.enable_pruning": false
}
```

**Impact**: 
- Faster processing (no LLM calls for pruning)
- Larger value sets (more terms included)
- Less precise filtering

#### Disable Keyword Generation

To skip keyword generation:

```json
{
  "keyword_service.enable_keywords": false
}
```

**Impact**: 
- Faster processing
- Empty keywords list in output
- May affect downstream search/indexing

#### Fast Mode (Minimal Processing)

For the fastest processing with basic output:

```json
{
  "term_expander.enable_pruning": false,
  "keyword_service.enable_keywords": false
}
```

### AWS Bedrock Setup

1. **Configure AWS Credentials**:
   ```bash
   aws configure
   # Or use --aws-profile flag
   ```

2. **Enable Bedrock Model Access**:
   - Go to AWS Console → Bedrock → Model access
   - Request access to `amazon.nova-pro-v1:0`
   - Wait for approval (usually immediate)

3. **Set IAM Permissions**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel"
         ],
         "Resource": "arn:aws:bedrock:*::foundation-model/amazon.nova-pro-v1:0"
       }
     ]
   }
   ```

### OpenAI Setup

1. **Get API Key**:
   - Visit https://platform.openai.com/api-keys
   - Create new secret key
   - Copy key (starts with `sk-`)

2. **Add to Configuration**:
   ```json
   {
     "summarization.openai_llm_api_key": "sk-your-actual-key",
     "keyword_service.openai_llm_api_key": "sk-your-actual-key",
     "pruning_service.openai_llm_api_key": "sk-your-actual-key"
   }
   ```

3. **Verify Access**:
   - Ensure your account has GPT-4 access
   - Check usage limits and billing

## Output Format

The tool generates value set files in the output directory with the following structure:

```
output/
├── <document-name>_valueset.json
└── <document-name>_summary.json
```

### ValueSet JSON Structure

```json
{
  "name": "Document Primary Subject",
  "version": "1.25.4.12",
  "domain": "problem",
  "codes": [
    {
      "code": "R07.9",
      "system": "ICD10CM",
      "display": "Chest pain, unspecified",
      "imo_code": "85191",
      "imo_title": "Chest pain"
    }
  ],
  "keywords": [
    "chest pain",
    "thoracic discomfort",
    "cardiac pain"
  ],
  "metadata": {
    "source_document": "chest_pain_education.txt",
    "generated_date": "2025-12-10T12:34:56Z",
    "primary_subject": "Chest Pain",
    "gender": "Both",
    "age_group": "All"
  }
}
```

## Troubleshooting

### Common Issues

#### 1. AWS Credentials Error

**Error**: `Unable to locate credentials`

**Solution**:
```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### 2. OpenAI API Error

**Error**: `401 Unauthorized`

**Solution**: 
- Verify API key is correct in `config.json`
- Check API key hasn't expired
- Ensure billing is set up

#### 3. IMO API Authentication Error

**Error**: `403 Forbidden`

**Solution**:
- Verify `client_id` and `client_secret` in `config.json`
- Contact IMO support for credential validation

#### 4. Bedrock Model Not Available

**Error**: `ResourceNotFoundException: Could not resolve model`

**Solution**:
- Go to AWS Console → Bedrock → Model access
- Request access to `amazon.nova-pro-v1:0`
- Wait for approval

#### 5. No Output Files Generated

**Checklist**:
1. Verify input directory contains `.txt` files
2. Check write permissions for output directory
3. Review console output for errors
4. Ensure `process-domain` matches document content

### Debug Mode

For verbose output, you can modify the logging level:

```python
# Add to main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

If you encounter issues:

1. Check configuration settings in `config.json`
2. Review console output for error messages
3. Verify all API credentials are valid
4. Check network connectivity to API endpoints
5. Review the [IMO API documentation](https://api.imohealth.com/docs)

## Performance Considerations

### Processing Speed

Approximate processing times per document:

| Configuration | Time per Document | Notes |
|--------------|------------------|-------|
| Full pipeline (Bedrock) | 30-60 seconds | Includes all steps |
| Full pipeline (OpenAI) | 45-90 seconds | API latency may vary |
| Pruning disabled | 15-30 seconds | Skips pruning LLM calls |
| Keywords disabled | 25-45 seconds | Skips keyword generation |
| Minimal (both disabled) | 10-20 seconds | Basic expansion only |

### Cost Optimization

**AWS Bedrock**:
- Pay per token usage
- Approximately $0.01-0.05 per document
- No additional infrastructure costs

**OpenAI GPT-4**:
- Pay per token usage
- Approximately $0.05-0.20 per document
- Higher cost but potentially better accuracy

**Cost Saving Tips**:
1. Disable pruning for large batches of similar documents
2. Batch process documents in off-peak hours
3. Use AWS Bedrock for cost-effective processing
4. Monitor token usage in AWS/OpenAI dashboards

## Architecture

### Service Overview

```
main.py
├── SummarizationService (IMO API or OpenAI)
│   └── Extracts entities from documents
├── TermExpander
│   ├── SearchService (IMO Search API)
│   ├── PruningService (LLMService)
│   └── PrecisionSetsService (IMO Precision Sets)
├── KeywordService (LLMService)
│   └── Generates search keywords
└── ValueSetsService
    └── Creates final value set files
```

### LLM Service Abstraction

The `LLMService` provides a unified interface for both AWS Bedrock and OpenAI:

```python
from services.llm_service import LLMService

# AWS Bedrock
llm = LLMService(
    llm_provider="aws_bedrock",
    aws_bedrock_client=bedrock_client
)

# OpenAI
llm = LLMService(
    llm_provider="openai",
    openai_api_key="sk-..."
)

# Invoke (same interface for both)
response = llm.invoke(
    user_prompt="Extract medical terms",
    system_prompt="You are a medical AI assistant",
    temperature=0.7
)
```

## License

[Include your license information here]

## Support

For questions or issues, contact:
- IMO API Support: [support contact]
- Internal Team: [team contact]
