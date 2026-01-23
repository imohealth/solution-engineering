"""
SOAP Note Generator
Converts medical transcripts into structured SOAP format using Amazon Bedrock Nova Pro
"""
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import config


class SOAPGenerator:
    """
    Generate structured SOAP notes from medical transcripts using Amazon Bedrock Nova Pro.
    """
    
    def __init__(self):
        """Initialize the SOAP generator with AWS Bedrock client."""
        try:
            # Initialize Bedrock Runtime client
            if config.aws_access_key_id and config.aws_secret_access_key:
                # Build kwargs for boto3 client
                kwargs = {
                    'service_name': 'bedrock-runtime',
                    'region_name': config.aws_region,
                    'aws_access_key_id': config.aws_access_key_id,
                    'aws_secret_access_key': config.aws_secret_access_key
                }
                # Add session token if available (for temporary credentials)
                if config.aws_session_token:
                    kwargs['aws_session_token'] = config.aws_session_token
                
                self.bedrock_client = boto3.client(**kwargs)
            else:
                # Use default AWS credentials (from ~/.aws/credentials or IAM role)
                self.bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=config.aws_region
                )
            
            self.model_id = config.bedrock_model_id
            self.use_bedrock = True
            print(f"✓ Bedrock client initialized with model: {self.model_id}")
            
        except Exception as e:
            print(f"Warning: Could not initialize Bedrock client: {str(e)}")
            print("Falling back to rule-based SOAP generation")
            self.bedrock_client = None
            self.use_bedrock = False
        
        # System prompt for the model
        self.system_prompt = "I am an expert SOAP note generator. Given a medical transcript of inpatient or outpatient visits I can create a SOAP note."
    
    def generate_soap_note(self, transcript):
        """
        Generate a SOAP note from a medical transcript using Bedrock Nova Pro.
        
        Args:
            transcript (str): Medical transcript text
            
        Returns:
            dict: SOAP note with sections (subjective, objective, assessment, plan)
        """
        if not transcript:
            raise ValueError("Transcript cannot be empty")
        
        transcript = transcript.strip()
        
        # Try to use Bedrock if available
        if self.use_bedrock and self.bedrock_client:
            try:
                soap_note = self._generate_with_bedrock(transcript)
                if soap_note:
                    soap_note['generated_at'] = datetime.now().isoformat()
                    soap_note['source'] = 'bedrock_nova_pro'
                    soap_note['model'] = self.model_id
                    return soap_note
            except Exception as e:
                print(f"Error using Bedrock: {str(e)}")
                print("Falling back to rule-based generation")
        
        # Fallback to rule-based generation
        soap_note = self._generate_fallback(transcript)
        soap_note['generated_at'] = datetime.now().isoformat()
        soap_note['source'] = 'rule_based'
        return soap_note
    
    def _generate_with_bedrock(self, transcript):
        """
        Generate SOAP note using Amazon Bedrock Nova Pro model.
        
        Args:
            transcript (str): Medical transcript text
            
        Returns:
            dict: SOAP note sections
        """
        print(f"\nGenerating SOAP note with Bedrock Nova Pro...")
        print(f"Model: {self.model_id}")
        print(f"Transcript length: {len(transcript)} characters")
        
        # Construct the prompt
        user_prompt = f"""Please generate a comprehensive SOAP note from the following medical transcript. 

Format your response as follows:

SUBJECTIVE:
[Patient's reported symptoms, history, and concerns - use paragraphs and bullet points as appropriate]

OBJECTIVE:
[Physical examination findings, vital signs, and test results - use structured format with clear organization]

ASSESSMENT:
[Clinical diagnosis and evaluation - use numbered list for multiple diagnoses]

PLAN:
[Treatment plan and recommendations - use numbered or bulleted list]

Medical Transcript:
{transcript}

Please provide the SOAP note in clear, well-formatted text suitable for clinical documentation."""
        
        # Prepare the request body for Nova Pro
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": user_prompt
                        }
                    ]
                }
            ],
            "system": [
                {
                    "text": self.system_prompt
                }
            ],
            "inferenceConfig": {
                "maxTokens": 2000,
                "temperature": 0.3,
                "topP": 0.9
            }
        }
        
        try:
            # Invoke the model
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=request_body["messages"],
                system=request_body["system"],
                inferenceConfig=request_body["inferenceConfig"]
            )
            
            # Extract the response text
            response_text = response['output']['message']['content'][0]['text']
            print(f"\n✓ Received response from Bedrock ({len(response_text)} characters)")
            print(response_text)
            # Extract SOAP sections from formatted text
            soap_note = self._extract_sections_from_text(response_text)
            print("Testing..")
            print(soap_note)
            
            if soap_note:
                print(f"✓ Successfully parsed SOAP note")
                print(f"  Sections: {', '.join(soap_note.keys())}")
                return soap_note
            else:
                print("⚠ Could not extract sections, trying JSON parsing")
                return self._parse_bedrock_response(response_text)
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"✗ Bedrock API Error: {error_code} - {error_message}")
            raise
        except Exception as e:
            print(f"✗ Error calling Bedrock: {str(e)}")
            raise
    
    def _parse_bedrock_response(self, response_text):
        """
        Parse the Bedrock response to extract SOAP sections.
        
        Args:
            response_text (str): Response from Bedrock
            
        Returns:
            dict or None: SOAP sections if successfully parsed
        """
        try:
            # Try to find JSON in the response
            # Look for content between triple backticks or curly braces
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                soap_note = json.loads(json_str)
                
                # Validate required keys
                required_keys = ['subjective', 'objective', 'assessment', 'plan']
                if all(key in soap_note for key in required_keys):
                    # Ensure all values are strings (convert objects/lists to strings if needed)
                    for key in required_keys:
                        value = soap_note[key]
                        if isinstance(value, dict):
                            # If it's a dict, try to extract 'text' or convert to string
                            soap_note[key] = value.get('text', str(value))
                        elif isinstance(value, list):
                            # If it's a list, join items or convert to string
                            soap_note[key] = ' '.join(str(item) for item in value)
                        elif not isinstance(value, str):
                            # Convert any other type to string
                            soap_note[key] = str(value)
                    
                    return soap_note
            
            return None
            
        except json.JSONDecodeError:
            return None
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            return None
    
    def _extract_sections_from_text(self, text):
        """
        Extract SOAP sections from plain text response.
        
        Args:
            text (str): Response text
            
        Returns:
            dict: SOAP sections
        """
        import re
        
        sections = {
            'subjective': '',
            'objective': '',
            'assessment': '',
            'plan': ''
        }
        
        # Remove intro text before the actual SOAP note
        text = re.sub(r'^.*?(?=\*\*SUBJECTIVE|\bSUBJECTIVE:)', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove closing summary/footer after the PLAN section ends
        text = re.sub(r'---\s*This SOAP note.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'---\s*$', '', text, flags=re.DOTALL)
        
        # Patterns to find SOAP sections - handle both plain and markdown bold formatting
        patterns = {
            'subjective': r'(?i)(?:\*\*)?SUBJECTIVE:?(?:\*\*)?\s*\n+(.*?)(?=\n\s*(?:\*\*)?OBJECTIVE:|\n\s*(?:\*\*)?ASSESSMENT:|\n\s*(?:\*\*)?PLAN:|---|\Z)',
            'objective': r'(?i)(?:\*\*)?OBJECTIVE:?(?:\*\*)?\s*\n+(.*?)(?=\n\s*(?:\*\*)?ASSESSMENT:|\n\s*(?:\*\*)?PLAN:|---|\Z)',
            'assessment': r'(?i)(?:\*\*)?ASSESSMENT:?(?:\*\*)?\s*\n+(.*?)(?=\n\s*(?:\*\*)?PLAN:|---|\Z)',
            'plan': r'(?i)(?:\*\*)?PLAN:?(?:\*\*)?\s*\n+(.*?)(?=---|This SOAP note|\Z)'
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                # Get the matched content and clean it up
                content = match.group(1).strip()
                # Remove markdown formatting
                content = self._clean_markdown(content)
                # Remove excessive whitespace but preserve structure
                content = re.sub(r'\n{3,}', '\n\n', content)
                # Remove leading/trailing horizontal rules
                content = re.sub(r'^-+\s*', '', content)
                content = re.sub(r'\s*-+$', '', content)
                sections[section] = content.strip()
        
        # If no sections found, try to intelligently split the text
        if not any(sections.values()):
            sections = self._generate_fallback(text)
            print("No sections found, used fallback generation.")

        print(sections)
        
        return sections
    
    def _clean_markdown(self, text):
        """
        Remove markdown formatting from text.
        
        Args:
            text (str): Text with markdown formatting
            
        Returns:
            str: Clean text without markdown
        """
        import re
        
        # Remove bold/italic markdown (**text**, *text*, __text__, _text_)
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # bold+italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)          # italic
        text = re.sub(r'___(.+?)___', r'\1', text)        # bold+italic
        text = re.sub(r'__(.+?)__', r'\1', text)          # bold
        text = re.sub(r'_(.+?)_', r'\1', text)            # italic
        
        # Remove inline code backticks
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Remove markdown headers (keep the text, just remove the #)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        return text
    
    def _generate_fallback(self, transcript):
        """
        Fallback rule-based SOAP note generation.
        
        Args:
            transcript (str): Medical transcript text
            
        Returns:
            dict: SOAP sections
        """
        import re
        
        # Keywords for classification
        keywords = {
            'subjective': [
                'patient', 'reports', 'complains', 'states', 'presents with',
                'history', 'symptoms', 'pain', 'discomfort', 'feels', 'feeling'
            ],
            'objective': [
                'exam', 'vital signs', 'blood pressure', 'heart rate', 'temperature',
                'respiratory rate', 'physical exam', 'labs', 'imaging', 'test results',
                'findings', 'readings', 'levels'
            ],
            'assessment': [
                'diagnosis', 'assessment', 'impression', 'condition', 'problem',
                'given', 'important'
            ],
            'plan': [
                'plan', 'treatment', 'prescribe', 'medication', 'follow-up',
                'referral', 'admit', 'discharge', 'order', 'continue', 'administer',
                'monitor', 'adjust', 'review'
            ]
        }
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        soap_sections = {
            'subjective': [],
            'objective': [],
            'assessment': [],
            'plan': []
        }
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Calculate scores for each section
            scores = {}
            for section, kw_list in keywords.items():
                score = sum(1 for kw in kw_list if kw in sentence_lower)
                scores[section] = score
            
            # Assign to section with highest score
            best_section = max(scores, key=scores.get)
            if scores[best_section] > 0:
                soap_sections[best_section].append(sentence)
            else:
                # Default to subjective
                soap_sections['subjective'].append(sentence)
        
        # Convert to strings
        return {
            'subjective': ' '.join(soap_sections['subjective']),
            'objective': ' '.join(soap_sections['objective']),
            'assessment': ' '.join(soap_sections['assessment']),
            'plan': ' '.join(soap_sections['plan'])
        }
    
    def format_soap_note(self, soap_note):
        """
        Format SOAP note for display.
        
        Args:
            soap_note (dict): SOAP note sections
            
        Returns:
            str: Formatted SOAP note
        """
        formatted = []
        
        sections = [
            ('SUBJECTIVE', 'subjective'),
            ('OBJECTIVE', 'objective'),
            ('ASSESSMENT', 'assessment'),
            ('PLAN', 'plan')
        ]
        
        for title, key in sections:
            if key in soap_note and soap_note[key]:
                formatted.append(f"\n{title}:")
                formatted.append(soap_note[key])
                formatted.append("")
        
        return '\n'.join(formatted)
