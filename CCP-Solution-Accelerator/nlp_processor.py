"""
NLP Processor
Handles IMO Entity Extraction API and Precision Normalize API integration
"""
import requests
import json
from typing import Dict, List, Any
import config


class NLPProcessor:
    """
    Process medical text using IMO Health APIs for entity extraction and normalization.
    """
    
    def __init__(self):
        """Initialize the NLP processor with IMO API credentials."""
        self.auth_url = config.imo_auth_url if hasattr(config, 'imo_auth_url') else "https://auth.imohealth.com/oauth/token"
        self.entity_extraction_url = config.imo_entity_extraction_url if hasattr(config, 'imo_entity_extraction_url') else "https://api.imohealth.com/entityextraction/pipelines/imo-clinical-comprehensive"
        self.normalize_enrichment_url = config.imo_precision_normalize_enrichment_url if hasattr(config, 'imo_precision_normalize_enrichment_url') else "https://api.imohealth.com/precision/normalize/enrichment"
        self.normalize_url = config.imo_precision_normalize_url if hasattr(config, 'imo_precision_normalize_url') else "https://api.imohealth.com/precision/normalize"
        
        # Get API credentials from config
        try:
            self.client_id = config.imo_client_id
            self.client_secret = config.imo_client_secret
            self.access_token = None
            self.token_expiry = None
            
            # Diagnostic workflow credentials
            self.workflow_client_id = config.imo_diagnostic_workflow_client_id if hasattr(config, 'imo_diagnostic_workflow_client_id') else None
            self.workflow_client_secret = config.imo_diagnostic_workflow_client_secret if hasattr(config, 'imo_diagnostic_workflow_client_secret') else None
            self.workflow_access_token = None
            self.workflow_token_expiry = None
        except AttributeError:
            print("Warning: IMO API credentials not found in config. Using demo mode.")
            self.client_id = None
            self.client_secret = None
            self.access_token = None
            self.token_expiry = None
            self.workflow_client_id = None
            self.workflow_client_secret = None
            self.workflow_access_token = None
            self.workflow_token_expiry = None
    
    def _get_access_token(self) -> str:
        """
        Get OAuth access token from IMO auth endpoint.
        
        Returns:
            str: Access token
        """
        import time
        
        # Check if we have a valid token
        if self.access_token and self.token_expiry and time.time() < self.token_expiry:
            return self.access_token
        
        print("Getting new access token from IMO OAuth endpoint...")
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'audience': 'https://api.imohealth.com'
            }
            
            response = requests.post(
                self.auth_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                expires_in = result.get('expires_in', 3600)
                self.token_expiry = time.time() + expires_in - 60  # Refresh 60s before expiry
                print(f"✓ Access token obtained (expires in {expires_in}s)")
                return self.access_token
            else:
                print(f"✗ OAuth Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error getting access token: {str(e)}")
            return None
    
    def _get_diagnostic_workflow_token(self) -> str:
        """
        Get OAuth access token for diagnostic workflow endpoint.
        Uses separate credentials from the main API.
        
        Returns:
            str: Access token for diagnostic workflow
        """
        import time
        
        # Check if we have a valid token
        if self.workflow_access_token and self.workflow_token_expiry and time.time() < self.workflow_token_expiry:
            return self.workflow_access_token
        
        print("Getting new diagnostic workflow access token from IMO OAuth endpoint...")
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.workflow_client_id,
                'client_secret': self.workflow_client_secret,
                'audience': 'https://api.imohealth.com'
            }
            
            response = requests.post(
                self.auth_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.workflow_access_token = result.get('access_token')
                expires_in = result.get('expires_in', 3600)
                self.workflow_token_expiry = time.time() + expires_in - 60  # Refresh 60s before expiry
                print(f"✓ Diagnostic workflow access token obtained (expires in {expires_in}s)")
                return self.workflow_access_token
            else:
                print(f"✗ Diagnostic Workflow OAuth Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error getting diagnostic workflow access token: {str(e)}")
            return None
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract entities from medical text using IMO Entity Extraction API.
        
        Args:
            text (str): Medical text (Assessment and Plan sections)
            
        Returns:
            dict: Extracted entities categorized by type (problems, procedures, medications, labs)
        """
        if not text:
            return {
                'problems': [],
                'procedures': [],
                'medications': [],
                'labs': []
            }
        
        print(f"Extracting entities from text: {len(text)} characters")
        
        # If no API credentials, use demo extraction
        if not self.client_id or not self.client_secret:
            print("No API credentials found, using demo mode")
            return self._demo_extract_entities(text)
        
        try:
            # Get OAuth access token
            access_token = self._get_access_token()
            if not access_token:
                print("Could not obtain access token, using demo mode")
                return self._demo_extract_entities(text)
            
            # Prepare API request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            payload = {
                'text': text
            }
            
            # Call IMO Entity Extraction API
            print(f"Calling IMO Entity Extraction API: {self.entity_extraction_url}")
            response = requests.post(
                self.entity_extraction_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Successfully extracted entities from API")

                return self._parse_extraction_response(result, text)
            else:
                print(f"✗ API Error: {response.status_code} - {response.text}")
                return self._demo_extract_entities(text)
                
        except Exception as e:
            print(f"Error calling Entity Extraction API: {str(e)}")
            return self._demo_extract_entities(text)
    
    def _parse_extraction_response(self, response: Dict, original_text: str = "") -> Dict[str, List[Dict]]:
        """
        Parse IMO Entity Extraction API response.
        
        Args:
            response (dict): API response
            original_text (str): Original text for context extraction
            
        Returns:
            dict: Categorized entities with context
        """
        entities = {
            'problems': [],
            'procedures': [],
            'medications': [],
            'labs': []
        }
        
        # Parse entities from response
        if 'entities' in response:
            print(f"Parsing {len(response['entities'])} entities from response")
            
            # Define entities to ignore (generic/administrative terms)
            ignore_patterns = [
                'review test results', 'patient education', 'lifestyle', 
                'education', 'review', 'follow-up', 'follow up',
                'appointment', 'monitoring', 'discussion', 'counseling',
                'instructions', 'recommendations', 'assessment', 'plan'
            ]
            
            for entity in response['entities']:
                # Only include entities with assertion "present"
                assertion = entity.get('assertion', '').lower()
                if assertion != 'present':
                    print(f"Skipping entity '{entity.get('text', '')}' with assertion '{assertion}'")
                    continue
                
                # Check if entity text matches ignore patterns
                entity_text = entity.get('text', '').lower().strip()
                if any(pattern in entity_text for pattern in ignore_patterns):
                    print(f"Ignoring generic entity: '{entity.get('text', '')}'")
                    continue
                
                category = entity.get('semantic', '').lower()
                offset = entity.get('begin', 0)
                end_offset = entity.get('end', 0)
                length = end_offset - offset
                
                # Extract context around the entity (200 chars before and after for context)
                context = self._extract_context(original_text, offset, length, context_window=200)
                
                # Extract codes from codemaps
                imo_code = ''
                imo_description = ''
                code_system = 'IMO'
                confidence = 0.0
                
                if 'codemaps' in entity and 'imo' in entity['codemaps']:
                    imo_data = entity['codemaps']['imo']
                    imo_code = imo_data.get('lexical_code', '')
                    imo_description = imo_data.get('lexical_title', '')
                    confidence = float(imo_data.get('confidence', 0.0))
                
                entity_data = {
                    'text': entity.get('text', ''),
                    'code': imo_code,
                    'code_system': code_system,
                    'description': imo_description,
                    'offset': offset,
                    'length': length,
                    'confidence': confidence,
                    'context': context,
                    'entity_id': entity.get('id', ''),
                    'semantic': entity.get('semantic', ''),
                    'assertion': entity.get('assertion', ''),
                    'codemaps': entity.get('codemaps', {})
                }
                
                # Map categories
                if 'problem' in category or 'condition' in category or 'diagnosis' in category:
                    entities['problems'].append(entity_data)
                elif 'procedure' in category:
                    entities['procedures'].append(entity_data)
                elif 'medication' in category or 'drug' in category:
                    entities['medications'].append(entity_data)
                elif 'lab' in category or 'observation' in category or 'test' in category:
                    entities['labs'].append(entity_data)
        
        return entities
    
    def _extract_context(self, text: str, offset: int, length: int, context_window: int = 1000) -> str:
        """
        Extract context around an entity in the text.
        
        Args:
            text (str): Full text
            offset (int): Starting position of entity
            length (int): Length of entity
            context_window (int): Number of characters before/after to include
            
        Returns:
            str: Context string with entity highlighted
        """
        if not text:
            return ""
        
        start = max(0, offset - context_window)
        end = min(len(text), offset + length + context_window)
        
        context = text[start:end].strip()
        
        # Add ellipsis if context is truncated
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    def _demo_extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """
        Demo entity extraction using keyword matching (fallback when API not available).
        
        Args:
            text (str): Medical text
            
        Returns:
            dict: Extracted entities
        """
        entities = {
            'problems': [],
            'procedures': [],
            'medications': [],
            'labs': []
        }
        
        text_lower = text.lower()
        
        # Common medical terms for demo
        problem_keywords = [
            'hypertension', 'diabetes', 'stemi', 'myocardial infarction', 'chest pain',
            'hyperlipidemia', 'pain', 'infection', 'fever', 'pneumonia', 'copd',
            'heart failure', 'arrhythmia', 'stroke', 'asthma'
        ]
        
        procedure_keywords = [
            'catheterization', 'surgery', 'biopsy', 'intubation', 'procedure',
            'operation', 'endoscopy', 'colonoscopy', 'angiography', 'stent'
        ]
        
        medication_keywords = [
            'aspirin', 'metformin', 'lisinopril', 'atorvastatin', 'clopidogrel',
            'heparin', 'insulin', 'warfarin', 'levothyroxine', 'amlodipine',
            'omeprazole', 'prednisone', 'albuterol'
        ]
        
        lab_keywords = [
            'troponin', 'ekg', 'blood pressure', 'heart rate', 'glucose',
            'hemoglobin', 'creatinine', 'bun', 'wbc', 'platelets', 'inr',
            'cholesterol', 'ldl', 'hdl', 'triglycerides'
        ]
        
        # Extract problems
        for keyword in problem_keywords:
            if keyword in text_lower:
                offset = text_lower.find(keyword)
                context = self._extract_context(text, offset, len(keyword), context_window=50)
                entities['problems'].append({
                    'text': keyword.title(),
                    'code': 'DEMO-' + keyword.replace(' ', '-').upper(),
                    'code_system': 'ICD-10-CM',
                    'description': keyword.title(),
                    'confidence': 0.85,
                    'context': context
                })
        
        # Extract procedures
        for keyword in procedure_keywords:
            if keyword in text_lower:
                offset = text_lower.find(keyword)
                context = self._extract_context(text, offset, len(keyword), context_window=50)
                entities['procedures'].append({
                    'text': keyword.title(),
                    'code': 'DEMO-' + keyword.replace(' ', '-').upper(),
                    'code_system': 'CPT',
                    'description': keyword.title(),
                    'confidence': 0.80,
                    'context': context
                })
        
        # Extract medications
        for keyword in medication_keywords:
            if keyword in text_lower:
                offset = text_lower.find(keyword)
                context = self._extract_context(text, offset, len(keyword), context_window=50)
                entities['medications'].append({
                    'text': keyword.title(),
                    'code': 'DEMO-' + keyword.replace(' ', '-').upper(),
                    'code_system': 'RxNorm',
                    'description': keyword.title(),
                    'confidence': 0.90,
                    'context': context
                })
        
        # Extract labs
        for keyword in lab_keywords:
            if keyword in text_lower:
                offset = text_lower.find(keyword)
                context = self._extract_context(text, offset, len(keyword), context_window=50)
                entities['labs'].append({
                    'text': keyword.title(),
                    'code': 'DEMO-' + keyword.replace(' ', '-').upper(),
                    'code_system': 'LOINC',
                    'description': keyword.title(),
                    'confidence': 0.75,
                    'context': context
                })
        
        return entities
    
    def normalize_problems(self, problems: List[Dict]) -> List[Dict]:
        """
        Normalize problems using IMO Precision Normalize API to get ICD-10 and SNOMED codes.
        
        Args:
            problems (list): List of problem entities
            
        Returns:
            list: Problems with ICD-10 and SNOMED codes
        """
        if not problems:
            return []
        
        print(f"\nNormalizing {len(problems)} problems to get ICD-10 and SNOMED codes...")
        
        # If no API credentials, return original problems
        if not self.client_id or not self.client_secret:
            print("No API credentials available")
            return problems
        
        # Get OAuth access token
        access_token = self._get_access_token()
        if not access_token:
            print("Could not obtain access token")
            return problems
        
        normalized_problems = []
        
        for problem in problems:
            try:
                normalized_problem = self._normalize_single_problem(problem, access_token)
                normalized_problems.append(normalized_problem)
            except Exception as e:
                print(f"Error normalizing problem '{problem.get('text')}': {str(e)}")
                # Add original problem if normalization fails
                normalized_problems.append(problem)
        
        return normalized_problems
    
    def _normalize_single_problem(self, problem: Dict, access_token: str) -> Dict:
        """
        Normalize a single problem using IMO Precision Normalize API.
        Uses the IMO lexical code from entity extraction to get ICD-10 and SNOMED codes.
        
        Args:
            problem (dict): Problem entity to normalize
            access_token (str): OAuth access token
            
        Returns:
            dict: Problem with IMO, ICD-10 and SNOMED codes
        """
        problem_text = problem.get('text', '')
        imo_code = problem.get('code', '')  # IMO lexical code from entity extraction
        
        print(f"  Normalizing: '{problem_text}' (IMO: {imo_code})")
        
        # Start with the original problem data
        normalized_problem = problem.copy()
        
        # If we don't have an IMO code, we can't normalize
        if not imo_code:
            print(f"    ⚠ No IMO code available, skipping normalization")
            return normalized_problem
        
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use the IMO Precision Normalize API v1 format
            payload = {
                'client_request_id': f'normalize_{imo_code}',
                'requests': [
                    {
                        'record_id': str(imo_code),
                        'domain': 'Problem',
                        'input_code': str(imo_code),
                        'input_code_system': 'IMO'
                    }
                ]
            }
            
            print(f"    Payload: {json.dumps(payload)}")
            
            response = requests.post(
                'https://api.imohealth.com/precision/normalize/v1',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"    Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract ICD-10 and SNOMED codes from the response
                icd10_code = ''
                icd10_description = ''
                snomed_code = ''
                snomed_description = ''
                
                # Navigate the response structure
                if 'requests' in result and len(result['requests']) > 0:
                    request_result = result['requests'][0]
                    
                    if 'response' in request_result and 'items' in request_result['response']:
                        items = request_result['response']['items']
                        
                        if len(items) > 0:
                            item = items[0]  # Get the best match
                            metadata = item.get('metadata', {})
                            mappings = metadata.get('mappings', {})
                            
                            # Extract ICD-10-CM codes
                            if 'icd10cm' in mappings:
                                icd10_data = mappings['icd10cm'].get('codes', [])
                                if len(icd10_data) > 0:
                                    icd10_code = icd10_data[0].get('code', '')
                                    icd10_description = icd10_data[0].get('title', '')
                            
                            # Extract SNOMED International codes
                            if 'snomedInternational' in mappings:
                                snomed_data = mappings['snomedInternational'].get('codes', [])
                                if len(snomed_data) > 0:
                                    snomed_code = snomed_data[0].get('code', '')
                                    snomed_description = snomed_data[0].get('title', '')
                            
                            if icd10_code or snomed_code:
                                print(f"    ✓ ICD-10: {icd10_code} | SNOMED: {snomed_code}")
                            else:
                                print(f"    ⚠ No mappings found in response")
                        else:
                            print(f"    ⚠ No items in response")
                    else:
                        print(f"    ⚠ No response data in result")
                else:
                    print(f"    ⚠ No requests in response")
                
                # Add codes to problem (preserve original IMO code)
                normalized_problem['icd10_code'] = icd10_code
                normalized_problem['icd10_description'] = icd10_description
                normalized_problem['snomed_code'] = snomed_code
                normalized_problem['snomed_description'] = snomed_description
                
                return normalized_problem
            else:
                print(f"    ✗ API Error: {response.status_code}")
                if response.text:
                    try:
                        error_json = response.json()
                        print(f"    Full error response: {json.dumps(error_json, indent=2)}")
                        error_msg = error_json.get('error', {}).get('message', '')
                        error_code = error_json.get('error', {}).get('details', {}).get('code', '')
                        error_details = error_json.get('error', {}).get('details', {})
                        print(f"    Error: {error_msg} (Code: {error_code})")
                        print(f"    Details: {error_details}")
                    except:
                        print(f"    Error details: {response.text}")
                return normalized_problem
                
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return normalized_problem
    
    def normalize_procedures(self, procedures: List[Dict]) -> List[Dict]:
        """
        Normalize procedures using IMO Precision Normalize API to get CPT and ICD-10-PCS codes.
        
        Args:
            procedures (list): List of procedure entities
            
        Returns:
            list: Procedures with CPT and ICD-10-PCS codes
        """
        if not procedures:
            return []
        
        print(f"\nNormalizing {len(procedures)} procedures to get CPT and ICD-10-PCS codes...")
        
        # If no API credentials, return original procedures
        if not self.client_id or not self.client_secret:
            print("No API credentials available")
            return procedures
        
        # Get OAuth access token
        access_token = self._get_access_token()
        if not access_token:
            print("Could not obtain access token")
            return procedures
        
        normalized_procedures = []
        
        for procedure in procedures:
            try:
                normalized_procedure = self._normalize_single_procedure(procedure, access_token)
                normalized_procedures.append(normalized_procedure)
            except Exception as e:
                print(f"Error normalizing procedure '{procedure.get('text')}': {str(e)}")
                # Add original procedure if normalization fails
                normalized_procedures.append(procedure)
        
        return normalized_procedures
    
    def _normalize_single_procedure(self, procedure: Dict, access_token: str) -> Dict:
        """
        Normalize a single procedure using IMO Precision Normalize API.
        Uses the IMO lexical code from entity extraction to get CPT and ICD-10-PCS codes.
        
        Args:
            procedure (dict): Procedure entity to normalize
            access_token (str): OAuth access token
            
        Returns:
            dict: Procedure with IMO, CPT and ICD-10-PCS codes
        """
        procedure_text = procedure.get('text', '')
        imo_code = procedure.get('code', '')  # IMO lexical code from entity extraction
        
        print(f"  Normalizing: '{procedure_text}' (IMO: {imo_code})")
        
        # Start with the original procedure data
        normalized_procedure = procedure.copy()
        
        # If we don't have an IMO code, we can't normalize
        if not imo_code:
            print(f"    ⚠ No IMO code available, skipping normalization")
            return normalized_procedure
        
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use the IMO Precision Normalize API v1 format
            payload = {
                'client_request_id': f'normalize_proc_{imo_code}',
                'requests': [
                    {
                        'record_id': str(imo_code),
                        'domain': 'Procedure',
                        'input_code': str(imo_code),
                        'input_code_system': 'IMO'
                    }
                ]
            }
            
            print(f"    Payload: {json.dumps(payload)}")
            
            response = requests.post(
                'https://api.imohealth.com/precision/normalize/v1',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"    Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"    Full response: {json.dumps(result, indent=2)}")
                
                # Extract CPT and ICD-10-PCS codes from the response
                cpt_code = ''
                cpt_description = ''
                icd10pcs_code = ''
                icd10pcs_description = ''
                
                # Navigate the response structure
                if 'requests' in result and len(result['requests']) > 0:
                    request_result = result['requests'][0]
                    
                    if 'response' in request_result and 'items' in request_result['response']:
                        items = request_result['response']['items']
                        
                        if len(items) > 0:
                            item = items[0]  # Get the best match
                            metadata = item.get('metadata', {})
                            mappings = metadata.get('mappings', {})
                            
                            # Extract CPT codes
                            if 'cpt' in mappings:
                                cpt_data = mappings['cpt'].get('codes', [])
                                if len(cpt_data) > 0:
                                    cpt_code = cpt_data[0].get('code', '')
                                    cpt_description = cpt_data[0].get('title', '')
                            
                            # Extract ICD-10-PCS codes
                            if 'icd10pcs' in mappings:
                                icd10pcs_data = mappings['icd10pcs'].get('codes', [])
                                if len(icd10pcs_data) > 0:
                                    icd10pcs_code = icd10pcs_data[0].get('code', '')
                                    icd10pcs_description = icd10pcs_data[0].get('title', '')
                            
                            if cpt_code or icd10pcs_code:
                                print(f"    ✓ CPT: {cpt_code} | ICD-10-PCS: {icd10pcs_code}")
                            else:
                                print(f"    ⚠ No mappings found in response")
                        else:
                            print(f"    ⚠ No items in response")
                    else:
                        print(f"    ⚠ No response data in result")
                else:
                    print(f"    ⚠ No requests in response")
                
                # Add codes to procedure (preserve original IMO code)
                normalized_procedure['cpt_code'] = cpt_code
                normalized_procedure['cpt_description'] = cpt_description
                normalized_procedure['icd10pcs_code'] = icd10pcs_code
                normalized_procedure['icd10pcs_description'] = icd10pcs_description
                
                return normalized_procedure
            else:
                print(f"    ✗ API Error: {response.status_code}")
                if response.text:
                    try:
                        error_json = response.json()
                        error_msg = error_json.get('error', {}).get('message', '')
                        error_code = error_json.get('error', {}).get('details', {}).get('code', '')
                        print(f"    Error: {error_msg} (Code: {error_code})")
                    except:
                        print(f"    Error details: {response.text[:300]}")
                return normalized_procedure
                
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return normalized_procedure
    
    def normalize_medications(self, medications: List[Dict]) -> List[Dict]:
        """
        Normalize medications using IMO Precision Normalize API to get RxNorm codes.
        
        Args:
            medications (list): List of medication entities
            
        Returns:
            list: Medications with RxNorm codes
        """
        if not medications:
            return []
        
        print(f"\nNormalizing {len(medications)} medications to get RxNorm codes...")
        
        # If no API credentials, return original medications
        if not self.client_id or not self.client_secret:
            print("No API credentials available")
            return medications
        
        # Get OAuth access token
        access_token = self._get_access_token()
        if not access_token:
            print("Could not obtain access token")
            return medications
        
        normalized_medications = []
        
        for medication in medications:
            try:
                normalized_medication = self._normalize_single_medication(medication, access_token)
                normalized_medications.append(normalized_medication)
            except Exception as e:
                print(f"Error normalizing medication '{medication.get('text')}': {str(e)}")
                # Add original medication if normalization fails
                normalized_medications.append(medication)
        
        return normalized_medications
    
    def _normalize_single_medication(self, medication: Dict, access_token: str) -> Dict:
        """
        Normalize a single medication using IMO Precision Normalize API.
        Uses the IMO lexical code from entity extraction to get RxNorm codes.
        
        Args:
            medication (dict): Medication entity to normalize
            access_token (str): OAuth access token
            
        Returns:
            dict: Medication with IMO and RxNorm codes
        """
        medication_text = medication.get('text', '')
        imo_code = medication.get('code', '')  # IMO lexical code from entity extraction
        
        print(f"  Normalizing: '{medication_text}' (IMO: {imo_code})")
        
        # Start with the original medication data
        normalized_medication = medication.copy()
        
        # If we don't have an IMO code, we can't normalize
        if not imo_code:
            print(f"    ⚠ No IMO code available, skipping normalization")
            return normalized_medication
        
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use the IMO Precision Normalize API v1 format
            payload = {
                'client_request_id': f'normalize_med_{imo_code}',
                'requests': [
                    {
                        'record_id': str(imo_code),
                        'domain': 'Medication',
                        'input_code': str(imo_code),
                        'input_code_system': 'IMO'
                    }
                ]
            }
            
            print(f"    Payload: {json.dumps(payload)}")
            
            response = requests.post(
                'https://api.imohealth.com/precision/normalize/v1',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"    Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"    Full response: {json.dumps(result, indent=2)}")
                
                # Extract RxNorm codes from the response
                rxnorm_code = ''
                rxnorm_description = ''
                
                # Navigate the response structure
                if 'requests' in result and len(result['requests']) > 0:
                    request_result = result['requests'][0]
                    
                    if 'response' in request_result and 'items' in request_result['response']:
                        items = request_result['response']['items']
                        
                        if len(items) > 0:
                            item = items[0]  # Get the best match
                            metadata = item.get('metadata', {})
                            mappings = metadata.get('mappings', {})
                            
                            # Extract RxNorm codes
                            if 'rxnorm' in mappings:
                                rxnorm_data = mappings['rxnorm'].get('codes', [])
                                if len(rxnorm_data) > 0:
                                    # RxNorm uses different field names: rxnorm_code and rxnorm_titles
                                    rxnorm_code = rxnorm_data[0].get('rxnorm_code', '')
                                    rxnorm_titles = rxnorm_data[0].get('rxnorm_titles', [])
                                    if len(rxnorm_titles) > 0:
                                        rxnorm_description = rxnorm_titles[0].get('title', '')
                            
                            if rxnorm_code:
                                print(f"    ✓ RxNorm: {rxnorm_code}")
                            else:
                                print(f"    ⚠ No RxNorm mapping found in response")
                        else:
                            print(f"    ⚠ No items in response")
                    else:
                        print(f"    ⚠ No response data in result")
                else:
                    print(f"    ⚠ No requests in response")
                
                # Add codes to medication (preserve original IMO code)
                normalized_medication['rxnorm_code'] = rxnorm_code
                normalized_medication['rxnorm_description'] = rxnorm_description
                
                return normalized_medication
            else:
                print(f"    ✗ API Error: {response.status_code}")
                if response.text:
                    try:
                        error_json = response.json()
                        error_msg = error_json.get('error', {}).get('message', '')
                        error_code = error_json.get('error', {}).get('details', {}).get('code', '')
                        print(f"    Error: {error_msg} (Code: {error_code})")
                    except:
                        print(f"    Error details: {response.text[:300]}")
                return normalized_medication
                
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return normalized_medication
    
    def normalize_labs(self, labs: List[Dict]) -> List[Dict]:
        """
        Normalize labs using IMO Precision Normalize API to get LOINC codes.
        
        Args:
            labs (list): List of lab entities
            
        Returns:
            list: Labs with LOINC codes
        """
        if not labs:
            return []
        
        print(f"\nNormalizing {len(labs)} labs to get LOINC codes...")
        
        # If no API credentials, return original labs
        if not self.client_id or not self.client_secret:
            print("No API credentials available")
            return labs
        
        # Get OAuth access token
        access_token = self._get_access_token()
        if not access_token:
            print("Could not obtain access token")
            return labs
        
        normalized_labs = []
        
        for lab in labs:
            try:
                normalized_lab = self._normalize_single_lab(lab, access_token)
                normalized_labs.append(normalized_lab)
            except Exception as e:
                print(f"Error normalizing lab '{lab.get('text')}': {str(e)}")
                # Add original lab if normalization fails
                normalized_labs.append(lab)
        
        return normalized_labs
    
    def _normalize_single_lab(self, lab: Dict, access_token: str) -> Dict:
        """
        Normalize a single lab using IMO Precision Normalize API.
        Uses the IMO lexical code from entity extraction to get LOINC codes.
        
        Args:
            lab (dict): Lab entity to normalize
            access_token (str): OAuth access token
            
        Returns:
            dict: Lab with IMO and LOINC codes
        """
        lab_text = lab.get('text', '')
        imo_code = lab.get('code', '')  # IMO lexical code from entity extraction
        
        print(f"  Normalizing: '{lab_text}' (IMO: {imo_code})")
        
        # Start with the original lab data
        normalized_lab = lab.copy()
        
        # If we don't have an IMO code, we can't normalize
        if not imo_code:
            print(f"    ⚠ No IMO code available, skipping normalization")
            return normalized_lab
        
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use the IMO Precision Normalize API v1 format
            payload = {
                'client_request_id': f'normalize_lab_{imo_code}',
                'requests': [
                    {
                        'record_id': str(imo_code),
                        'domain': 'Lab',
                        'input_code': str(imo_code),
                        'input_code_system': 'IMO'
                    }
                ]
            }
            
            print(f"    Payload: {json.dumps(payload)}")
            
            response = requests.post(
                'https://api.imohealth.com/precision/normalize/v1',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"    Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"    Full response: {json.dumps(result, indent=2)}")
                
                # Extract LOINC codes from the response
                loinc_code = ''
                loinc_description = ''
                
                # Navigate the response structure
                if 'requests' in result and len(result['requests']) > 0:
                    request_result = result['requests'][0]
                    
                    if 'response' in request_result and 'items' in request_result['response']:
                        items = request_result['response']['items']
                        
                        if len(items) > 0:
                            item = items[0]  # Get the best match
                            metadata = item.get('metadata', {})
                            mappings = metadata.get('mappings', {})
                            
                            # Extract LOINC codes
                            if 'loinc' in mappings:
                                loinc_data = mappings['loinc'].get('codes', [])
                                if len(loinc_data) > 0:
                                    loinc_code = loinc_data[0].get('code', '')
                                    loinc_description = loinc_data[0].get('title', '')
                            
                            if loinc_code:
                                print(f"    ✓ LOINC: {loinc_code}")
                            else:
                                print(f"    ⚠ No LOINC mapping found in response")
                        else:
                            print(f"    ⚠ No items in response")
                    else:
                        print(f"    ⚠ No response data in result")
                else:
                    print(f"    ⚠ No requests in response")
                
                # Add codes to lab (preserve original IMO code)
                normalized_lab['loinc_code'] = loinc_code
                normalized_lab['loinc_description'] = loinc_description
                
                return normalized_lab
            else:
                print(f"    ✗ API Error: {response.status_code}")
                if response.text:
                    try:
                        error_json = response.json()
                        error_msg = error_json.get('error', {}).get('message', '')
                        error_code = error_json.get('error', {}).get('details', {}).get('code', '')
                        print(f"    Error: {error_msg} (Code: {error_code})")
                    except:
                        print(f"    Error details: {response.text[:300]}")
                return normalized_lab
                
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return normalized_lab
    
    def normalize_entities(self, entities: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Normalize entities using IMO Precision Normalize API.
        
        Args:
            entities (dict): Extracted entities
            
        Returns:
            dict: Normalized entities with IMO codes
        """
        # Normalization functionality is intentionally disabled in this configuration.
        # The original implementation is preserved below as a commented placeholder
        # to make re-enabling straightforward in the future.
        """
        if not entities:
            return {
                'problems': [],
                'procedures': [],
                'medications': [],
                'labs': []
            }

        print(f"Normalizing entities...")

        # If no API credentials, use demo normalization
        if not self.client_id or not self.client_secret:
            return self._demo_normalize_entities(entities)

        # Get OAuth access token
        access_token = self._get_access_token()
        if not access_token:
            print("Could not obtain access token for normalization, using demo mode")
            return self._demo_normalize_entities(entities)

        normalized = {
            'problems': [],
            'procedures': [],
            'medications': [],
            'labs': []
        }

        # Normalize each category
        for category, entity_list in entities.items():
            for entity in entity_list:
                try:
                    normalized_entity = self._normalize_single_entity(entity, category, access_token)
                    normalized[category].append(normalized_entity)
                except Exception as e:
                    print(f"Error normalizing entity {entity.get('text')}: {str(e)}")
                    # Add original entity if normalization fails
                    normalized[category].append(entity)

        return normalized
        """

        raise NotImplementedError("Normalization step removed from pipeline")
    
    def _normalize_single_entity(self, entity: Dict, category: str, access_token: str) -> Dict:
        """
        Normalize a single entity using IMO API.
        Uses enrichment endpoint for problems (with context), regular endpoint for others.
        
        Args:
            entity (dict): Entity to normalize
            category (str): Entity category (problems, procedures, medications, labs)
            access_token (str): OAuth access token
        """
        # The full original implementation was intentionally removed from the
        # active pipeline and is preserved in the repository history.
        # If you need to re-enable it, restore the original implementation
        # here and ensure proper configuration and credentials.

        raise NotImplementedError("Single-entity normalization removed from pipeline")
    
    def _demo_normalize_entities(self, entities: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Demo normalization (fallback when API not available).
        
        Args:
            entities (dict): Extracted entities
            
        Returns:
            dict: Normalized entities
        """
        # Demo normalization removed - not available when normalization step is disabled
        raise NotImplementedError("Demo normalization removed from pipeline")
    
    def _check_refinement_needed(self, entity: Dict, category: str) -> bool:
        """
        Check if an entity needs additional refinement.
        
        Args:
            entity (dict): Normalized entity
            category (str): Entity category
            
        Returns:
            bool: True if refinement needed
        """
        # Refinement logic removed - not used when normalization is disabled
        raise NotImplementedError("Refinement checks removed from pipeline")
    
    def refine_entities(self, entities_to_refine: List[Dict]) -> List[Dict]:
        """
        Refine entities that need additional specificity.
        
        Args:
            entities_to_refine (list): Entities needing refinement
            
        Returns:
            list: Refined entities with additional specificity
        """
        # Refinement workflow removed from pipeline
        raise NotImplementedError("Refinement step removed from pipeline")
    
    def _get_refinement_options(self, entity: Dict, category: str) -> List[Dict]:
        """
        Get refinement options for an entity.
        
        Args:
            entity (dict): Entity to refine
            category (str): Entity category
            
        Returns:
            list: Refinement options
        """
        # Refinement options removed from pipeline
        raise NotImplementedError("Refinement options removed from pipeline")
