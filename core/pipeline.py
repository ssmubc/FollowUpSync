import uuid
from typing import Dict, Any, List
from core.schema import ExtractionResult
from core.extract import Extractor
from core.storage import StorageManager
from core.mcp_client import MCPClient

class Pipeline:
    def __init__(self):
        self.extractor = Extractor()
        self.storage = StorageManager()
        self.mcp_client = MCPClient()
    
    def process_transcript(self, transcript: str) -> ExtractionResult:
        run_id = str(uuid.uuid4())[:8]
        
        # Save input
        self.storage.save_input(run_id, transcript)
        
        # Extract structured data
        result = self.extractor.extract(transcript, run_id)
        
        return result
    
    def save_artifacts(self, result: ExtractionResult) -> Dict[str, str]:
        # Generate summary markdown
        summary_md = self._generate_summary_md(result)
        
        # Save artifacts
        summary_path = self.storage.save_output(result.run_id, "Summary.md", summary_md)
        json_path = self.storage.save_output(result.run_id, "ActionItems.json", result.dict())
        
        return {
            "summary_md": summary_path,
            "action_items_json": json_path
        }
    
    def deliver_to_integrations(self, result: ExtractionResult, integrations: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        
        if integrations.get('slack'):
            channel = integrations['slack'].get('channel', '#general')
            slack_result = self._send_to_slack(result, channel)
            results['slack'] = slack_result
        
        if integrations.get('notion'):
            notion_result = self._send_to_notion(result)
            results['notion'] = notion_result
        
        if integrations.get('jira'):
            jira_result = self._send_to_jira(result)
            results['jira'] = jira_result
        
        return results
    
    def _generate_summary_md(self, result: ExtractionResult) -> str:
        md = f"# Meeting Summary - {result.run_id}\n\n"
        
        if result.decisions:
            md += "## Decisions\n"
            for i, decision in enumerate(result.decisions, 1):
                md += f"{i}. {decision.text}\n"
                if decision.owners:
                    md += f"   - Owners: {', '.join(decision.owners)}\n"
            md += "\n"
        
        if result.action_items:
            md += "## Action Items\n"
            for i, item in enumerate(result.action_items, 1):
                md += f"{i}. **{item.title}**\n"
                if item.owner:
                    md += f"   - Owner: {item.owner}\n"
                if item.due_date:
                    md += f"   - Due: {item.due_date}\n"
                if item.priority:
                    md += f"   - Priority: {item.priority}\n"
            md += "\n"
        
        if result.risks:
            md += "## Risks & Blockers\n"
            for i, risk in enumerate(result.risks, 1):
                md += f"{i}. {risk.text}\n"
                if risk.severity:
                    md += f"   - Severity: {risk.severity}\n"
                if risk.mitigation:
                    md += f"   - Mitigation: {risk.mitigation}\n"
            md += "\n"
        
        return md
    
    def _send_to_slack(self, result: ExtractionResult, channel: str) -> Dict[str, Any]:
        summary_text = f"📋 Meeting Summary - {result.run_id}\n"
        summary_text += f"Decisions: {len(result.decisions)} | Actions: {len(result.action_items)} | Risks: {len(result.risks)}"
        
        main_result = self.mcp_client.post_to_slack(channel, summary_text)
        
        if main_result.get('ok') and result.action_items:
            thread_ts = main_result.get('ts')
            for item in result.action_items:
                action_text = f"🎯 {item.title}"
                if item.owner:
                    action_text += f" (@{item.owner})"
                if item.due_date:
                    action_text += f" - Due: {item.due_date}"
                
                self.mcp_client.post_to_slack(channel, action_text, thread_ts)
        
        return main_result
    
    def _send_to_notion(self, result: ExtractionResult) -> List[Dict[str, Any]]:
        results = []
        for item in result.action_items:
            notion_result = self.mcp_client.create_notion_task(
                title=item.title,
                body=item.notes or "",
                due_date=str(item.due_date) if item.due_date else None,
                assignee=item.owner
            )
            results.append(notion_result)
        return results
    
    def _send_to_jira(self, result: ExtractionResult) -> List[Dict[str, Any]]:
        results = []
        for item in result.action_items:
            jira_result = self.mcp_client.create_jira_issue(
                summary=item.title,
                description=item.notes or f"Action item from meeting {result.run_id}",
                assignee=item.owner
            )
            results.append(jira_result)
        return results