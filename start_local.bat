@echo off
echo Starting FollowUpSync in Local Mode...
echo.

echo Starting MCP servers...
start "Slack MCP" cmd /k "python mcp/slack_server.py"
timeout /t 2 /nobreak >nul

start "Notion MCP" cmd /k "python mcp/notion_server.py"
timeout /t 2 /nobreak >nul

start "Jira MCP" cmd /k "python mcp/jira_server.py"
timeout /t 2 /nobreak >nul

echo Waiting for MCP servers to start...
timeout /t 5 /nobreak >nul

echo Starting Streamlit app...
streamlit run app/streamlit_app.py

echo.
echo Press any key to exit...
pause >nul