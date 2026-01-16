"""
Configuration file for Ambient AI Solution
Store API credentials and settings here
"""

# AWS Bedrock Configuration
aws_region = "us-east-1"  # Change to your preferred region
aws_access_key_id = None  # Will use default AWS credentials if None
aws_secret_access_key = None  # Will use default AWS credentials if None
bedrock_model_id = "us.amazon.nova-pro-v1:0"  # Amazon Nova Pro model

import boto3
import os
from botocore.exceptions import ClientError

# Helper to fetch secrets from AWS SSM Parameter Store
def get_ssm_param(name, with_decryption=True):
	ssm = boto3.client("ssm", region_name=aws_region)
	try:
		param = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
		return param["Parameter"]["Value"]
	except ClientError as e:
		if os.environ.get("DEBUG", "0") == "1":
			print(f"[config.py] Failed to fetch {name} from SSM: {e}")
		return None

# SSM parameter names (update if needed)
IMO_CLIENT_ID_PARAM = "/ambient-ai-solution/imo_client_id"
IMO_CLIENT_SECRET_PARAM = "/ambient-ai-solution/imo_client_secret"
IMO_DIAG_CLIENT_ID_PARAM = "/ambient-ai-solution/imo_diagnostic_workflow_client_id"
IMO_DIAG_CLIENT_SECRET_PARAM = "/ambient-ai-solution/imo_diagnostic_workflow_client_secret"

# IMO Health API Credentials (fetched from SSM)
_default_imo_client_id = ""
_default_imo_client_secret = ""
_default_imo_diag_client_id = ""
_default_imo_diag_client_secret = ""

imo_client_id = get_ssm_param(IMO_CLIENT_ID_PARAM) or _default_imo_client_id
imo_client_secret = get_ssm_param(IMO_CLIENT_SECRET_PARAM) or _default_imo_client_secret
imo_diagnostic_workflow_client_id = get_ssm_param(IMO_DIAG_CLIENT_ID_PARAM) or _default_imo_diag_client_id
imo_diagnostic_workflow_client_secret = get_ssm_param(IMO_DIAG_CLIENT_SECRET_PARAM) or _default_imo_diag_client_secret
# API Endpoints
imo_auth_url = "https://auth.imohealth.com/oauth/token"
imo_entity_extraction_url = "https://api.imohealth.com/entityextraction/pipelines/imo-clinical-comprehensive?version=3.0"
imo_precision_normalize_enrichment_url = "https://api.imohealth.com/precision/normalize/enrichment"
imo_precision_normalize_url = "https://api.imohealth.com/precision/normalize"
imo_diagnostic_workflow_url = "https://api.imohealth.com/core/search/v2/product/problemIT_Professional/workflows/diagnosis"

# Application Settings
debug_mode = True
demo_mode = True  # Set to True to use demo data when API credentials are not available
show_normalization_step = False  # Set to True to show normalization step in UI, False to hide it