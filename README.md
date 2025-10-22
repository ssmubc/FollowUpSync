# FollowUpSync

Convert meeting transcripts into actionable execution plans. Extract decisions and tasks, then create tasks/post follow-ups in Slack and Notion via MCP tools.

## Table of Contents
- [Demo Video](#demo-video)
- [URL to Deployed Project](#url-to-deployed-project)
- [Hackathon Requirements](#hackathon-requirements)
- [Quick Start](#quick-start-aws-mode---recommended)
- [Architecture Diagram](#architecture-diagram)
- [Features](#features)
- [Configuration](#configuration)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [AWS Deployment](#aws-deployment-optional)
- [License](#license)
- [Contributing](#contributing)
- [Author](#author)

## Demo Video

**Public Access Link to the Demo Video:**
https://drive.google.com/file/d/1KQczyus1zABMdyiVenltd3tcH66stmd1/view?usp=sharing

<video controls src="https://private-user-images.githubusercontent.com/97367319/504031197-42744ea2-3e90-4e5b-b957-63428794b346.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjExMTQ1MjEsIm5iZiI6MTc2MTExNDIyMSwicGF0aCI6Ii85NzM2NzMxOS81MDQwMzExOTctNDI3NDRlYTItM2U5MC00ZTViLWI5NTctNjM0Mjg3OTRiMzQ2Lm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTEwMjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUxMDIyVDA2MjM0MVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTBlNDFhMTNhNmI1YTExNjZkODYzNzk1ZTJmYzBmMjA5OGQ2ODU5MGZlODAwYTMwMjIyNDY1NTI2ZWJlZTkyZDQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.v--VwIEl4e-f9Wfb0tQnh38uhozraPkti-LohHPhEFU" title="[REPLACE_WITH_YOUR_VIDEO_URL_FROM_ISSUE]"></video>

*3-minute walkthrough showing AWS Bedrock Nova Micro extraction, Slack integration, Notion task creation, and artifact generation.*

- [Local File of the Demo Video](./demo_video/FollowUpSyncDemo.mp4)

## URL to Deployed Project

🌐 **https://followupsync.streamlit.app/** *(Note: Deployed version runs in local mode with sample integrations)*

## Hackathon Requirements

✅ **AWS AI Agent**: Uses Amazon Bedrock Nova Micro via boto3 SDK for intelligent extraction  
✅ **Autonomous Capabilities**: Independently processes transcripts and delivers to multiple platforms  
✅ **External Integrations**: MCP FastAPI servers for Slack and Notion connectivity  
✅ **Reasoning LLM**: Nova Micro performs complex date parsing and task categorization  
✅ **Architecture Diagram**: Available in repository and submission  
✅ **Public Repository**: Complete source code with setup instructions  
✅ **Deployed Project**: URL to the deployed project via Streamlit Cloud and a video demonstrating how to run the application

## Quick Start (AWS Mode - Recommended)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS**:
   ```bash
   aws configure  # Set up AWS credentials
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env: Set MODE=aws and add your API tokens
   ```

4. **Test the pipeline** (optional):
   ```bash
   python test_pipeline.py
   ```

5. **Start the application**:
   
   **Option A: Use startup script (Windows)**
   ```bash
   start_local.bat
   ```
   
   **Option B: Manual startup** (in separate terminals)
   ```bash
   # Terminal 1 - Slack MCP
   python mcp/slack_server.py
   
   # Terminal 2 - Notion MCP  
   python mcp/notion_server.py
   
   # Terminal 3 - Main App
   streamlit run app/streamlit_app.py
   ```

6. **Test with sample data**:
   - Open http://localhost:8501 in your browser
   - Click "Load Sample" in the sidebar
   - Copy the sample text to the main input area
   - Click "🔄 Process"
   - Review extracted data and click "💾 Generate Artifacts"

### Local Mode (Alternative)
For local testing without AWS, set `MODE=local` in `.env` and follow the same steps.

## Architecture Diagram

![FollowUpSync Architecture](./FollowUpSyncArchitecture.drawio.png)

*FollowUpSync uses AWS Bedrock Nova for AI extraction, S3 for artifact storage, and MCP servers for autonomous integration with Slack and Notion.* 

## Features

### Core Pipeline
- **Extract**: Decisions, Action Items, Risks from meeting transcripts
- **Review**: Tables for the extracted data
- **Deliver**: Send to Slack and Notion via MCP tools *(connection to Jira is in development)*
- **Artifacts**: Generate Summary.md and ActionItems.json

### Modes
- **Local Mode**: MCP servers on localhost, files in `data/`
- **AWS Mode**: MCP servers on localhost, S3 storage, Bedrock extraction

### Integrations
- **Slack**: Post summary + threaded action items + due dates
- **Notion**: Create task pages in database
- **Jira**: Create issues for action items *(In Development)*

## Configuration

### Required Environment Variables

```bash
# Mode
MODE=aws  # or 'local' for testing

# Slack (required for Slack integration)
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_DEFAULT_CHANNEL=#followupsync-demo

# Notion (required for Notion integration)
NOTION_TOKEN=secret_your-token
NOTION_DATABASE_ID=your-database-id

# AWS (required for AWS mode)
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
S3_BUCKET=your-bucket-name
```

### Setup Instructions

### Slack Setup (Detailed)

#### Step 1: Create Slack Workspace
1. Go to https://slack.com/get-started#/createnew
2. Enter your email and create a workspace
3. Choose a workspace name (e.g., "FollowUpSync Demo")
4. Skip adding team members

#### Step 2: Create Slack App
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. App Name: "FollowUpSync"
4. Choose your workspace → Click "Create App"

#### Step 3: Configure Bot Permissions
1. Go to "OAuth & Permissions" (left sidebar)
2. Scroll to "Bot Token Scopes"
3. Click "Add an OAuth Scope" → Add: `chat:write`

#### Step 4: Install App
1. Scroll up and click "Install to Workspace"
2. Click "Allow"
3. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
4. Add to `.env`: `SLACK_BOT_TOKEN=xoxb-your-token`

#### Step 5: Invite Bot to Channel
1. Go to your Slack workspace
2. Go to any channel (e.g., #general)
3. Type: `/invite @FollowUpSync` and press Enter
4. Update `.env`: `SLACK_DEFAULT_CHANNEL=#your-channel`

### Notion Setup (Detailed)

#### Step 1: Create Notion Account & Integration
1. Go to https://notion.so and sign up
2. Go to https://www.notion.so/my-integrations
3. Click "Create new integration"
4. Name: "FollowUpSync" → Select workspace → Submit
5. Copy token (starts with `secret_` or `ntn_`)
6. Add to `.env`: `NOTION_TOKEN=your-token`

#### Step 2: Create Database
1. In Notion, create new page
2. Type `/database` and create database
3. Add columns: Name (Title), Due Date (Date), Assignee (Text)
4. Click "Share" → Invite "FollowUpSync" integration
5. Copy database ID from URL (32 characters)
6. Add to `.env`: `NOTION_DATABASE_ID=your-database-id`

### AWS Setup (Required for AWS Mode)
1. Configure AWS credentials (`aws configure`)
2. Create S3 bucket for artifacts
3. Enable Bedrock model access in AWS console
4. Ensure Nova model access in your region

## Testing

### Local Testing
```bash
# Test with sample data
python -c "
from core.pipeline import Pipeline
pipeline = Pipeline()
with open('data/input/sample.txt') as f:
    result = pipeline.process_transcript(f.read())
print(f'Extracted {len(result.action_items)} action items')
"
```

### MCP Server Testing
```bash
# Test Slack MCP
curl -X POST http://localhost:8001/slack_post_message \
  -H "Content-Type: application/json" \
  -d '{"channel": "#test", "text": "Hello from FollowUpSync!"}'

# Test Notion MCP  
curl -X POST http://localhost:8002/notion_create_task \
  -H "Content-Type: application/json" \
  -d '{"database_id": "your-db-id", "title": "Test Task", "body": "Test body"}'
```

## Project Structure

```
followupsync/
├── app/
│   └── streamlit_app.py          # Main UI
├── core/
│   ├── pipeline.py               # Orchestrator
│   ├── extract.py                # Bedrock/local extraction
│   ├── schema.py                 # Data models
│   ├── storage.py                # Local/S3 abstraction
│   ├── mcp_client.py            # MCP communication
│   └── config.py                 # Environment config
├── mcp/
│   ├── slack_server.py           # Slack MCP server
│   ├── notion_server.py          # Notion MCP server
│   └── jira_server.py            # Jira MCP server
├── content/prompts/
│   ├── extractor_system.txt      # Bedrock system prompt
│   └── extractor_fewshots.json   # Few-shot examples
├── data/
│   ├── input/
│   │   └── sample.txt            # Sample transcript
│   └── output/                   # Generated artifacts
├── .env.example                  # Environment template
├── test_pipeline.py              # Test script
├── start_local.bat               # Windows startup script
├── start_local.sh                # Unix startup script
└── requirements.txt              # Python dependencies
```

## Troubleshooting

### Common Issues

**"Module not found" errors**:
- Run `pip install -r requirements.txt`
- Ensure you're running from the project root
- Check Python path in streamlit_app.py

**MCP servers not responding**:
- Check ports 8001, 8002, 8003 are available
- Verify servers are running on correct ports
- Check environment variables are set

**No extractions found**:
- This is normal with local mode - it looks for keywords like "decided", "action:", "risk"
- Switch to AWS mode for better extraction with Nova Micro

**Slack/Notion integration fails**:
- Verify API tokens in .env
- Check bot permissions and database sharing

**AWS mode issues**:
- Verify AWS credentials and region
- Check Bedrock model access
- Ensure S3 bucket exists and is accessible

### Logs
- Streamlit logs appear in terminal
- MCP server logs appear in their respective terminals
- Check `data/output/<run_id>/log.txt` for pipeline logs

## AWS Deployment (Future Enhancement)

*This is a planned future phase for the application:*

1. Package MCP servers as Lambda functions
2. Create Function URLs or API Gateway endpoints
3. Update MCP client URLs in config
4. Deploy with IAM roles for S3 and Bedrock access

## License

MIT License - see [LICENSE](./LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## **Author**

**Sharon Marfatia** - Built for the AWS AI Agent Global Hackathon

- GitHub: [@ssmubc](https://github.com/ssmubc)
- LinkedIn: [Sharon Marfatia](https://www.linkedin.com/in/sharon-cs)

---

**Built for the AWS AI Agent Global Hackathon**