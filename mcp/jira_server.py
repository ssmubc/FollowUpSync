from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import base64
import os

app = FastAPI(title="Jira MCP Server")

class JiraCreateIssue(BaseModel):
    cloud_base_url: str
    email: str
    api_token: str
    project_key: str
    summary: str
    description: str
    assignee: Optional[str] = None

@app.post("/jira_create_issue")
async def jira_create_issue(request: JiraCreateIssue):
    url = f"{request.cloud_base_url}/rest/api/3/issue"
    
    # Create basic auth header
    auth_string = f"{request.email}:{request.api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "fields": {
            "project": {
                "key": request.project_key
            },
            "summary": request.summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": request.description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": "Task"
            }
        }
    }
    
    # Add assignee if provided
    if request.assignee:
        payload["fields"]["assignee"] = {
            "emailAddress": request.assignee
        }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        if response.status_code == 201:
            issue_key = result.get("key")
            return {
                "key": issue_key,
                "url": f"{request.cloud_base_url}/browse/{issue_key}"
            }
        else:
            raise HTTPException(status_code=response.status_code, detail=result.get("errorMessages", ["Unknown error"]))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "jira-mcp"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)