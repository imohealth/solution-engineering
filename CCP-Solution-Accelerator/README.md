# Clinical Comprehensive Pipeline (CCP) Accelerator

A web-based application that showcases the IMO Clinical Comprehensive Pipeline. This is done by processing SOAP notes into structured clinical data with hyper-specific medical codes using the IMO Health Entity Extraction API.

## Features

The application implements a 3-step pipeline:

1. **Transcript Input** - Enter or upload medical transcripts from ambient listening software
2. **SOAP Note Generation** - Uses Amazon Bedrock Nova Pro AI model to convert transcripts into structured SOAP format (Subjective, Objective, Assessment, Plan)
3. **Entity Extraction** - Extracts medical entities (problems, procedures, medications, labs) from Assessment and Plan sections using the IMO Entity Extraction API and adds the relevant medical codes, such as ICD-10, LOINC, SNOMED, and RxNorm.

## Setup

### Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access (for Nova Pro model)
- AWS credentials configured (via AWS CLI or environment variables)
- IMO Health API credentials (optional - demo mode available)

### Installation

1. Navigate to the project directory:
```bash
cd CCP-Solution-Accelerator
```

2. Create and activate a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure AWS credentials (choose one method):

   **Option A: AWS CLI**
   ```bash
   aws configure
   ```

   **Option B: Environment Variables**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

   **Option C: Update config.py**
   ```python
   aws_access_key_id = "your_access_key"
   aws_secret_access_key = "your_secret_key"
   aws_region = "us-east-1"
   ```

5. Enable Bedrock Nova Pro model in your AWS account:
   - Go to AWS Bedrock Console
   - Navigate to Model Access
   - Request access to "Amazon Nova Pro" model
   - Wait for approval (usually instant)

6. (Optional) Configure IMO API credentials in `config.py`:
   ```python
   imo_client_id = "your_client_id"
   imo_client_secret = "your_client_secret"
   demo_mode = False  # Set to False to use live IMO APIs
   ```
   *Note: The app works in demo mode without IMO credentials*

### Running the Application

**Option A: Using Python directly**
```bash
python app.py
```

**Option B: Using the provided scripts**
```bash
./run.sh          # On macOS/Linux
# or
run.bat           # On Windows
```

Open your browser and navigate to:
```
http://localhost:5001
```

## Project Structure

```
CCP-Solution-Accelerator/
├── app.py                      # Flask backend with API endpoints
├── soap_generator.py           # SOAP note generation module
├── nlp_processor.py           # IMO API integration for NLP
├── config.py                  # Configuration and API credentials
├── requirements.txt           # Python dependencies
├── run.sh                     # Shell script to run the app (Unix/macOS)
├── run.bat                    # Batch script to run the app (Windows)
├── templates/
│   └── index.html            # Frontend UI
├── sample_data/               # Sample medical transcripts
│   ├── sample_transcript.txt
│   ├── inpatient-transcript3.txt
│   ├── outpatient-transcript1.txt
│   └── outpatient-transcript2.txt
├── README.md                  # This file
└── QUICKSTART.md             # Quick start guide
```

## API Endpoints

### POST /generate_soap
Generate a SOAP note from a medical transcript.
- **Input**: `{ "transcript": "medical transcript text..." }`
- **Output**: `{ "soap_note": {...}, "success": true }`

### POST /extract_entities
Extract entities from SOAP note using IMO Entity Extraction API.
- **Input**: `{ "soap_note": {...} }`
- **Output**: `{ "entities": {...}, "entity_counts": {...}, "success": true }`


### GET /load_sample_transcript
Load a sample medical transcript for testing.
- **Output**: `{ "transcript": "...", "success": true }`

## Demo Mode

The application includes a demo mode that works without IMO API credentials. It uses keyword-based entity extraction and mock normalization to demonstrate the pipeline flow.

To enable demo mode:
- Keep default values in `config.py`
- Or set `demo_mode = True`

## IMO Health API Integration

When configured with valid API credentials, the application integrates with:

1. **IMO Entity Extraction API**
   - URL: `https://api.imohealth.com/entityextraction/pipelines/imo-clinical-comprehensive`
   - Extracts medical entities from clinical text


## Usage

1. **Enter Transcript**: Paste a medical transcript or click "Load Sample Transcript"
2. **Generate SOAP**: Click "Generate SOAP Note" to structure the transcript
3. **Extract Entities**: Click "Extract Entities" to identify medical concepts (problems, procedures, medications, labs)

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI Model**: Amazon Bedrock Nova Pro (for SOAP note generation)
- **APIs**: IMO Health Entity Extraction
- **NLP**: Medical entity recognition and normalization
- **Cloud**: AWS Bedrock

## How It Works

### SOAP Note Generation with Bedrock Nova Pro

When you click "Generate SOAP Note", the application:

1. Sends the medical transcript to Amazon Bedrock Nova Pro model
2. Uses the system prompt: *"I am an expert SOAP note generator. Given a medical transcript of inpatient or outpatient visits I can create a SOAP note."*
3. The AI model analyzes the conversation and generates structured sections:
   - **Subjective**: Patient's reported symptoms, history, and concerns
   - **Objective**: Physical examination findings, vital signs, test results
   - **Assessment**: Clinical diagnosis and evaluation
   - **Plan**: Treatment plan and recommendations
4. Returns a professionally formatted SOAP note

### Fallback Mechanism

If AWS Bedrock is unavailable, the system automatically falls back to rule-based SOAP generation to ensure uninterrupted service.

## License

This project is part of the Solution Engineering toolkit.

## Support

For questions or issues, please contact the development team.
# CCP-Solution-Accelerator
