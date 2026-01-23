"""
Configuration file for Ambient AI Solution
Store API credentials and settings here
"""
import os

# AWS Bedrock Configuration
aws_region = "us-east-1"  # Change to your preferred region
# Try to get AWS credentials from environment variables first, otherwise use None
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')  # Will use default AWS credentials if None
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')  # Will use default AWS credentials if None
aws_session_token = os.getenv('AWS_SESSION_TOKEN')  # Session token for temporary credentials
bedrock_model_id = "us.amazon.nova-pro-v1:0"  # Amazon Nova Pro model

# IMO Health API Credentials
# Get your credentials from https://developer.imohealth.com
imo_client_id = "0mfNrRuxic2cMF1s06Tjcz5efsNVRdi3"
imo_client_secret = "vYebkuasAO2Kka1xKCBL4CZJE3AjFNux6lyWoY_6OFkMI_cXHZf7_1ojPQlwz_Hn"

# API Endpoints
imo_auth_url = "https://auth.imohealth.com/oauth/token"
imo_entity_extraction_url = "https://api.imohealth.com/entityextraction/pipelines/imo-clinical-comprehensive?version=3.0"
imo_precision_normalize_enrichment_url = "https://api.imohealth.com/precision/normalize/enrichment"
imo_precision_normalize_url = "https://api.imohealth.com/precision/normalize"
imo_diagnostic_workflow_url = "https://api.imohealth.com/core/search/v2/product/problemIT_Professional/workflows/diagnosis"
imo_diagnostic_workflow_client_id = "6SUMV7X6S1jp4jLiXZNth2tvlISGuPoU"
imo_diagnostic_workflow_client_secret = "fd-BVfydxGC8RGG2H6op-v9dp1HDYEeyJDD6LthSTO__jb4vUke534KU5sBLJMHC"

# Application Settings
debug_mode = True
demo_mode = True  # Set to True to use demo data when API credentials are not available
show_normalization_step = False  # Set to True to show normalization step in UI, False to hide it