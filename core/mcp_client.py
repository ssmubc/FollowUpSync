import requests
from typing import Dict, Any, List
from core.config import Config

class MCPClient:
    def __init__(self):
        self.is_aws = Config.is_aws_mode()
        self.base_urls = {
            'slack': 'http://localhost:8001',
            'notion': 'http://localhost:8002', 
            'jira': 'http://localhost:8003'
        }
    
    def post_to_slack(self, channel: str, text: str, thread_ts: str = None) -> Dict[str, Any]:
        if not Config.has_slack_config():
            return {"error": "Slack not configured"}
        
        url = f"{self.base_urls['slack']}/slack_post_message"
        payload = {
            "channel": channel,
            "text": text
        }
        if thread_ts:
            payload["thread_ts"] = thread_ts
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def create_notion_task(self, title: str, body: str, due_date: str = None, assignee: str = None) -> Dict[str, Any]:
        if not Config.has_notion_config():
            return {"error": "Notion not configured"}
        
        url = f"{self.base_urls['notion']}/notion_create_task"
        payload = {
            "database_id": Config.NOTION_DATABASE_ID,
            "title": title,
            "body": body
        }
        if due_date:
            payload["due_date"] = due_date
        if assignee:
            payload["assignee"] = assignee
        
        try:
            print(f"Sending to Notion: {payload}")
            response = requests.post(url, json=payload, timeout=30)
            print(f"Notion response status: {response.status_code}")
            result = response.json()
            print(f"Notion response: {result}")
            return result
        except Exception as e:
            print(f"Notion error: {str(e)}")
            return {"error": str(e)}
    
    def create_jira_issue(self, summary: str, description: str, assignee: str = None) -> Dict[str, Any]:
        if not Config.has_jira_config():
            return {"error": "Jira not configured"}
        
        url = f"{self.base_urls['jira']}/jira_create_issue"
        payload = {
            "cloud_base_url": Config.JIRA_BASE_URL,
            "email": Config.JIRA_EMAIL,
            "api_token": Config.JIRA_API_TOKEN,
            "project_key": Config.JIRA_PROJECT_KEY,
            "summary": summary,
            "description": description
        }
        if assignee:
            payload["assignee"] = assignee
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}