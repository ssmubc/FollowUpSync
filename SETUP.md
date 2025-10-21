# FollowUpSync Setup Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env  # Unix/Mac
copy .env.example .env  # Windows

# Edit .env with your settings:
# MODE=aws (for Bedrock) or MODE=local (for testing)
# Add API tokens for integrations (optional for basic testing)
```

### 3. Test the Pipeline
```bash
python test_pipeline.py
```

### 4. Start the Application

**Option A: Use startup script (Windows)**
```bash
start_local.bat
```

**Option B: Manual startup**
```bash
# Terminal 1 - Slack MCP Server
python mcp/slack_server.py

# Terminal 2 - Notion MCP Server  
python mcp/notion_server.py

# Terminal 3 - Jira MCP Server
python mcp/jira_server.py

# Terminal 4 - Main App
streamlit run app/streamlit_app.py
```

### 5. Test with Sample Data
1. Open http://localhost:8501 in your browser
2. Click "Load Sample" in the sidebar
3. Copy the sample text to the main input area
4. Click "🔄 Process"
5. Review the extracted decisions, action items, and risks
6. Click "💾 Generate Artifacts" to download files

## 🔧 Integration Setup (Optional)

### Slack Integration
1. Go to https://api.slack.com/apps
2. Create new app → "From scratch"
3. Add OAuth scope: `chat:write`
4. Install app to workspace
5. Copy "Bot User OAuth Token" to `.env` as `SLACK_BOT_TOKEN`

### Notion Integration  
1. Go to https://www.notion.so/my-integrations
2. Create new integration
3. Create a database with columns: Name (title), Due Date (date), Assignee (text)
4. Share database with your integration
5. Copy integration token to `.env` as `NOTION_TOKEN`
6. Copy database ID from URL to `.env` as `NOTION_DATABASE_ID`

## 📋 Project Structure Created

```
followupsync/
├── app/
│   └── streamlit_app.py          # ✅ Main Streamlit UI
├── core/
│   ├── __init__.py               # ✅ Package init
│   ├── pipeline.py               # ✅ Main orchestrator
│   ├── extract.py                # ✅ Local/Bedrock extraction
│   ├── schema.py                 # ✅ Pydantic data models
│   ├── storage.py                # ✅ Local/S3 storage
│   ├── mcp_client.py            # ✅ MCP communication
│   └── config.py                 # ✅ Environment config
├── mcp/
│   ├── __init__.py               # ✅ Package init
│   ├── slack_server.py           # ✅ Slack MCP server
│   ├── notion_server.py          # ✅ Notion MCP server
│   └── jira_server.py            # ✅ Jira MCP server
├── content/prompts/
│   ├── extractor_system.txt      # ✅ Bedrock system prompt
│   └── extractor_fewshots.json   # ✅ Few-shot examples
├── data/
│   ├── input/
│   │   └── sample.txt            # ✅ Sample transcript
│   └── output/                   # Generated artifacts go here
├── aws/
│   └── deploy_instructions.md    # ✅ AWS deployment guide
├── requirements.txt              # ✅ Python dependencies
├── .env.example                  # ✅ Environment template
├── README.md                     # ✅ Full documentation
├── test_pipeline.py              # ✅ Test script
├── start_local.bat               # ✅ Windows startup script
├── start_local.sh                # ✅ Unix startup script
└── SETUP.md                      # ✅ This setup guide
```

## ✅ Success Criteria Met

- ✅ **End-to-end demo**: Paste transcript → structured items → create external follow-ups
- ✅ **Reproducible**: Given sample.txt, creates Summary.md and ActionItems.json
- ✅ **Cross-platform**: Works on Windows/Mac with startup scripts
- ✅ **Clear README**: Complete setup and run instructions
- ✅ **3-minute demo**: Sample data and UI ready for quick demo

## 🎯 Demo Flow

1. **Load sample** (10s): Click "Load Sample" → copy to input
2. **Process** (20s): Click "🔄 Process" → show extraction results
3. **Review** (30s): Show decisions/actions/risks tables
4. **Generate** (20s): Click "💾 Generate Artifacts" → download files
5. **Integrations** (60s): Show Slack/Notion checkboxes (configure if needed)

## 🔍 Troubleshooting

**Import errors**: Run `pip install -r requirements.txt`

**MCP servers not starting**: Check ports 8001, 8002, 8003 are available

**No extractions found**: This is normal with the local rule-based extractor - it looks for keywords like "decided", "action:", "risk"

**Integration disabled**: Configure API tokens in .env file

## 🚀 Next Steps

1. **Test locally**: Follow steps 1-5 above
2. **Configure integrations**: Add API tokens to .env
3. **Try AWS mode**: Follow aws/deploy_instructions.md
4. **Customize prompts**: Edit content/prompts/ files
5. **Add more integrations**: Extend MCP servers

---

**Your FollowUpSync project is ready! 🎉**

The MVP runs locally with mock integrations, and you can enable real Slack/Notion integration by adding API tokens. AWS mode with Bedrock and Lambda is available for production use.