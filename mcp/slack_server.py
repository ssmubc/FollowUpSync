from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Slack MCP Server")

class SlackPostMessage(BaseModel):
    channel: str
    text: str
    thread_ts: Optional[str] = None

@app.post("/slack_post_message")
async def slack_post_message(request: SlackPostMessage):
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        raise HTTPException(status_code=400, detail="SLACK_BOT_TOKEN not configured")
    
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "channel": request.channel,
        "text": request.text
    }
    
    if request.thread_ts:
        payload["thread_ts"] = request.thread_ts
    
    try:
        print(f"Sending to Slack: {payload}")
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        print(f"Slack response status: {response.status_code}")
        print(f"Slack response: {result}")
        
        if result.get("ok"):
            return {
                "ok": True,
                "ts": result.get("ts"),
                "permalink": f"https://slack.com/archives/{request.channel}/p{result.get('ts', '').replace('.', '')}"
            }
        else:
            error_msg = result.get("error", "Unknown error")
            print(f"Slack API error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
    
    except Exception as e:
        print(f"Slack exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "slack-mcp"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)