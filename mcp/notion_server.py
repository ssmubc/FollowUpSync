from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Notion MCP Server")

class NotionCreateTask(BaseModel):
    database_id: str
    title: str
    body: str
    due_date: Optional[str] = None
    assignee: Optional[str] = None

@app.post("/notion_create_task")
async def notion_create_task(request: NotionCreateTask):
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise HTTPException(status_code=400, detail="NOTION_TOKEN not configured")
    
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Get database schema first to find the correct property names
    db_url = f"https://api.notion.com/v1/databases/{request.database_id}"
    db_response = requests.get(db_url, headers=headers)
    
    properties = {}
    
    if db_response.status_code == 200:
        db_info = db_response.json()
        db_properties = db_info.get("properties", {})
        
        # Find the title property
        for prop_name, prop_info in db_properties.items():
            if prop_info.get("type") == "title":
                # Clean up the title - remove leading dashes and extract just the task
                clean_title = request.title.strip()
                if clean_title.startswith('-'):
                    clean_title = clean_title[1:].strip()
                
                properties[prop_name] = {
                    "title": [
                        {
                            "text": {
                                "content": clean_title
                            }
                        }
                    ]
                }
                break
        
        # Add due date if provided
        if request.due_date:
            for prop_name, prop_info in db_properties.items():
                if prop_info.get("type") == "date":
                    properties[prop_name] = {
                        "date": {
                            "start": request.due_date
                        }
                    }
                    break
        
        # Add assignee if provided
        if request.assignee:
            for prop_name, prop_info in db_properties.items():
                prop_type = prop_info.get("type")
                if prop_type == "rich_text" and ("assignee" in prop_name.lower() or "owner" in prop_name.lower()):
                    properties[prop_name] = {
                        "rich_text": [
                            {
                                "text": {
                                    "content": request.assignee
                                }
                            }
                        ]
                    }
                    break
    else:
        # Fallback
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": request.title
                        }
                    }
                ]
            }
        }
    
    payload = {
        "parent": {
            "database_id": request.database_id
        },
        "properties": properties
    }
    
    # Add body content if provided
    if request.body:
        payload["children"] = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": request.body
                            }
                        }
                    ]
                }
            }
        ]
    
    try:
        print(f"Sending payload: {payload}")
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        print(f"Response status: {response.status_code}")
        print(f"Response body: {result}")
        
        if response.status_code == 200:
            return {
                "id": result.get("id"),
                "url": result.get("url")
            }
        else:
            error_msg = result.get("message", "Unknown error")
            print(f"Notion API error: {error_msg}")
            raise HTTPException(status_code=response.status_code, detail=error_msg)
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notion-mcp"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)