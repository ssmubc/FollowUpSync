import json
import re
from typing import Dict, Any
from datetime import datetime
from core.schema import ExtractionResult, Decision, ActionItem, Risk
from core.config import Config

class Extractor:
    def __init__(self):
        self.is_aws = Config.is_aws_mode()
        if self.is_aws:
            import boto3
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=Config.BEDROCK_REGION)
    
    def extract(self, transcript: str, run_id: str) -> ExtractionResult:
        print(f"🔍 Extract mode: {'AWS' if self.is_aws else 'LOCAL'}")
        if self.is_aws:
            return self._extract_bedrock(transcript, run_id)
        else:
            return self._extract_local(transcript, run_id)
    
    def _extract_bedrock(self, transcript: str, run_id: str) -> ExtractionResult:
        print(f"🔥 Using AWS Bedrock with model: {Config.BEDROCK_MODEL_ID}")
        system_prompt = self._load_system_prompt()
        
        if "nova" in Config.BEDROCK_MODEL_ID.lower():
            # Nova format
            body = {
                "messages": [
                    {
                        "role": "user", 
                        "content": [
                            {"text": f"{system_prompt}\n\nExtract from this transcript:\n\n{transcript}"}
                        ]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 4000
                }
            }
        else:
            # Claude format
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": f"Extract from this transcript:\n\n{transcript}"}
                ]
            }
        
        response = self.bedrock_client.invoke_model(
            modelId=Config.BEDROCK_MODEL_ID,
            body=json.dumps(body)
        )
        
        result = json.loads(response['body'].read())
        
        if "nova" in Config.BEDROCK_MODEL_ID.lower():
            content = result['output']['message']['content'][0]['text']
        else:
            content = result['content'][0]['text']
        
        try:
            print(f"🤖 Full Bedrock response: {content}")
            
            # Clean up the response - remove markdown code blocks
            clean_content = content.strip()
            if clean_content.startswith('```json'):
                clean_content = clean_content[7:]  # Remove ```json
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3]  # Remove ```
            clean_content = clean_content.strip()
            
            extracted_data = json.loads(clean_content)
            print("✅ Successfully parsed Bedrock JSON response")
            return self._build_extraction_result(extracted_data, run_id)
        except json.JSONDecodeError as e:
            print(f"❌ Bedrock JSON parse failed: {e}, falling back to local")
            return self._extract_local(transcript, run_id)
    
    def _extract_local(self, transcript: str, run_id: str) -> ExtractionResult:
        # Simple rule-based extraction as fallback
        decisions = []
        action_items = []
        risks = []
        
        lines = transcript.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for decision patterns
            if any(keyword in line.lower() for keyword in ['decided', 'decision', 'agreed', 'resolved']):
                decisions.append(Decision(text=line))
            
            # Look for action patterns
            elif any(keyword in line.lower() for keyword in ['action:', 'todo:', 'task:', 'will do', 'needs to']):
                title = re.sub(r'^(action:|todo:|task:)\s*', '', line, flags=re.IGNORECASE)
                action_items.append(ActionItem(title=title))
            
            # Look for risk patterns
            elif any(keyword in line.lower() for keyword in ['risk', 'blocker', 'concern', 'issue']):
                risks.append(Risk(text=line))
        
        summary_md = f"# Meeting Summary\n\n**Decisions:** {len(decisions)}\n**Action Items:** {len(action_items)}\n**Risks:** {len(risks)}"
        
        return ExtractionResult(
            run_id=run_id,
            decisions=decisions,
            action_items=action_items,
            risks=risks,
            summary_md=summary_md
        )
    
    def _load_system_prompt(self) -> str:
        try:
            with open('content/prompts/extractor_system.txt', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return """You are an expert project assistant. Extract ALL action items, decisions, and risks from this meeting transcript.

For Action Items, extract EVERY task mentioned with:
- title: Clean task description (e.g., "Set up development environment")
- owner: Person's name only (e.g., "John", "Sarah", "Mike") or "Unassigned"
- due_date: Convert phrases like "by Friday", "next Tuesday" to YYYY-MM-DD format
- priority: High/Medium/Low based on urgency
- notes: Additional context

Return ONLY valid JSON:
{"decisions": [{"text": "...", "owners": ["..."]}], "action_items": [{"title": "...", "owner": "...", "due_date": "...", "priority": "...", "notes": "..."}], "risks": [{"text": "...", "severity": "..."}], "summary_md": "..."}"""
    
    def _build_extraction_result(self, data: Dict[str, Any], run_id: str) -> ExtractionResult:
        decisions = [Decision(**d) for d in data.get('decisions', [])]
        
        # Clean up action items - handle invalid dates
        action_items = []
        for item_data in data.get('action_items', []):
            # Fix invalid due_date
            if item_data.get('due_date') == 'YYYY-MM-DD' or not item_data.get('due_date'):
                item_data['due_date'] = None
            
            # Fix only clearly outdated years (2023, 2024) but keep future years (2026+)
            elif item_data.get('due_date'):
                date_str = item_data['due_date']
                current_year = datetime.now().year
                
                # Only fix years that are clearly from old training data
                if date_str.startswith('2023-') or date_str.startswith('2024-'):
                    item_data['due_date'] = f"{current_year}{date_str[4:]}"
                # Keep years 2025+ as they're likely intentional future dates
            
            # Process relative dates from source_quote or notes (even if due_date exists)
            source_text = item_data.get('source_quote', '') or item_data.get('notes', '') or item_data.get('title', '')
            calculated_date = self._parse_relative_date(source_text)
            if calculated_date:
                # Override any existing due_date with our calculated one
                item_data['due_date'] = calculated_date
            elif not item_data.get('due_date'):
                # Only keep existing due_date if we couldn't calculate a better one
                pass
            
            action_items.append(ActionItem(**item_data))
        
        risks = [Risk(**r) for r in data.get('risks', [])]
        
        return ExtractionResult(
            run_id=run_id,
            decisions=decisions,
            action_items=action_items,
            risks=risks,
            summary_md=data.get('summary_md', '')
        )
    
    def _parse_relative_date(self, text: str) -> str:
        """Parse relative dates from text and return YYYY-MM-DD format"""
        from datetime import datetime, timedelta
        import re
        
        if not text:
            return None
            
        text = text.lower()
        today = datetime.now()
        
        # Check for specific dates like "Oct 30", "December 15", etc.
        month_pattern = r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{1,2})'
        month_match = re.search(month_pattern, text)
        
        if month_match:
            month_abbr = month_match.group(1)
            day = int(month_match.group(2))
            
            # Map month abbreviations
            months = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            month = months.get(month_abbr)
            if month:
                # Try current year first
                try:
                    target_date = datetime(today.year, month, day)
                    # If date has passed, use next year
                    if target_date < today:
                        target_date = datetime(today.year + 1, month, day)
                    return target_date.strftime('%Y-%m-%d')
                except ValueError:
                    pass  # Invalid date
        
        # Relative dates - check for various day patterns
        day_patterns = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for day_name, day_num in day_patterns.items():
            if f'next {day_name}' in text:
                days_ahead = (day_num - today.weekday()) % 7 + 7
                return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            elif f'by {day_name}' in text:
                days_ahead = (day_num - today.weekday()) % 7
                if days_ahead <= 0:
                    days_ahead += 7  # Next week if day has passed
                return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        if 'end of month' in text:
            next_month = today.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            return last_day.strftime('%Y-%m-%d')
        
        return None